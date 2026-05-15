"""CRC32 и проверка встроенной УКЭП РФ (63-ФЗ) в PDF."""

from __future__ import annotations

import re
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import fitz
from asn1crypto import cms
from pypdf import PdfReader
from pypdf.generic import NameObject

from app.config import Settings, get_settings
from app.schemas import BundlePdfUkepValidation, Fz63CheckItem, Status
from app.services.fz63.constants import FZ63_NOTE
from app.services.fz63.validate import ParsedCmsSignature, validate_russian_ukep

UKEP_STRUCTURAL_NOTE = FZ63_NOTE


@dataclass
class _SigMeta:
    signer_full_name: str | None = None
    certificate_valid: bool | None = None
    certificate_validity_label: str = "не определено"
    signed_at: datetime | None = None
    parsed_cms: ParsedCmsSignature | None = None
    is_qualified_certificate: bool | None = None
    fz63_compliant: bool | None = None
    fz63_summary: str = ""
    fz63_checks: list[Fz63CheckItem] = field(default_factory=list)


def compute_file_crc32_hex(path: Path) -> str:
    crc = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            crc = zlib.crc32(chunk, crc)
    return f"{crc & 0xFFFFFFFF:08X}"


def compute_bundle_manifest_crc32_hex(lines: list[tuple[str, str]]) -> str:
    body = "\n".join(f"{rel}\t{crc}" for rel, crc in sorted(lines, key=lambda x: x[0]))
    crc = zlib.crc32(body.encode("utf-8"))
    return f"{crc & 0xFFFFFFFF:08X}"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_pdf_date_m(value: object) -> datetime | None:
    if value is None:
        return None
    s = str(value).strip()
    if s.startswith("D:"):
        s = s[2:]
    s = re.sub(r"[+'Z].*$", "", s, count=1)
    s = re.sub(r"[^0-9]", "", s)[:14]
    if len(s) < 8:
        return None
    for fmt, length in (("%Y%m%d%H%M%S", 14), ("%Y%m%d%H%M", 12), ("%Y%m%d", 8)):
        chunk = s[:length]
        if len(chunk) < length and fmt != "%Y%m%d":
            continue
        try:
            return _ensure_aware(datetime.strptime(chunk, fmt))
        except ValueError:
            continue
    return None


def _subject_to_fio(subject: dict) -> str | None:
    cn = subject.get("common_name") or subject.get("cn")
    if cn and str(cn).strip():
        return str(cn).strip()
    surname = subject.get("surname") or subject.get("sn")
    given = subject.get("given_name") or subject.get("gn") or subject.get("g")
    parts = [str(p).strip() for p in (surname, given) if p]
    if parts:
        return " ".join(parts)
    return None


def _cert_validity_at(not_before: datetime, not_after: datetime, at: datetime) -> tuple[bool, str]:
    nb = _ensure_aware(not_before)
    na = _ensure_aware(not_after)
    moment = _ensure_aware(at)
    if moment < nb:
        return False, "ещё не действует"
    if moment > na:
        return False, "истёк"
    return True, "действителен"


def _name_is_sig(ft: object) -> bool:
    if ft is None:
        return False
    if isinstance(ft, NameObject):
        return ft == "/Sig"
    return str(ft) == "/Sig"


def _pdf_contents_to_bytes(contents: object) -> bytes:
    if contents is None:
        return b""
    if isinstance(contents, (bytes, bytearray)):
        return bytes(contents)
    getter = getattr(contents, "get_data", None)
    if callable(getter):
        try:
            return bytes(getter())
        except Exception:
            pass
    try:
        return bytes(contents)
    except Exception:
        return b""


def _parse_byte_range(value: object) -> list[int] | None:
    if value is None:
        return None
    try:
        nums = [int(x) for x in value]
    except (TypeError, ValueError):
        return None
    return nums if len(nums) >= 4 else None


def _parse_pkcs7_contents(contents: bytes, byte_range: list[int] | None = None) -> ParsedCmsSignature | None:
    data = contents.rstrip(b"\x00")
    if len(data) < 20:
        return None
    try:
        content_info = cms.ContentInfo.load(data)
    except Exception:
        return None
    if content_info["content_type"].native != "signed_data":
        return None
    signed_data = content_info["content"]
    certs: list = []
    for choice in signed_data["certificates"] or []:
        certs.append(choice.chosen)
    if not certs:
        return None

    signed_at: datetime | None = None
    signer_cert = certs[0]
    signer_info = signed_data["signer_infos"][0]
    for info in signed_data["signer_infos"] or []:
        signer_info = info
        signed_attrs = info["signed_attrs"]
        if signed_attrs:
            for attr in signed_attrs:
                if attr["type"].native == "signing_time":
                    raw = attr["values"][0].native
                    if isinstance(raw, datetime):
                        signed_at = _ensure_aware(raw)
                    break
        sid = info["sid"]
        if sid.name == "issuer_and_serial_number":
            serial = sid.chosen["serial_number"].native
            issuer = sid.chosen["issuer"].human_friendly
            for cert in certs:
                if (
                    cert["tbs_certificate"]["serial_number"].native == serial
                    and cert.issuer.human_friendly == issuer
                ):
                    signer_cert = cert
                    break

    return ParsedCmsSignature(
        signer_cert=signer_cert,
        all_certs=certs,
        signed_data=signed_data,
        signer_info=signer_info,
        signed_at=signed_at,
        byte_range=byte_range,
    )


def _meta_from_parsed(parsed: ParsedCmsSignature) -> _SigMeta:
    subject = parsed.signer_cert.subject.native
    fio = _subject_to_fio(subject)
    nb = parsed.signer_cert["tbs_certificate"]["validity"]["not_before"].native
    na = parsed.signer_cert["tbs_certificate"]["validity"]["not_after"].native
    check_at = parsed.signed_at or _utc_now()
    valid, label = _cert_validity_at(nb, na, check_at)
    return _SigMeta(
        signer_full_name=fio,
        certificate_valid=valid,
        certificate_validity_label=label,
        signed_at=parsed.signed_at,
        parsed_cms=parsed,
    )


def _run_fz63(meta: _SigMeta, pdf_path: Path, settings: Settings) -> _SigMeta:
    if not settings.fz63_check_enabled or meta.parsed_cms is None:
        return meta
    result = validate_russian_ukep(
        meta.parsed_cms,
        pdf_path,
        crl_timeout=settings.fz63_crl_timeout_seconds,
        require_crl=settings.fz63_require_crl,
    )
    meta.is_qualified_certificate = result.is_qualified
    meta.fz63_compliant = result.compliant
    meta.fz63_summary = result.summary
    meta.fz63_checks = result.checks
    if result.compliant and meta.certificate_valid:
        meta.certificate_validity_label = "действителен"
    elif not result.compliant and meta.certificate_valid:
        meta.certificate_validity_label = meta.certificate_validity_label
    return meta


def extract_signature_details(path: Path, settings: Settings | None = None) -> _SigMeta:
    settings = settings or get_settings()
    meta = _SigMeta()
    try:
        reader = PdfReader(str(path), strict=False)
    except Exception:
        return meta
    for field in (reader.get_fields() or {}).values():
        if not isinstance(field, dict) or not _name_is_sig(field.get("/FT")):
            continue
        v = field.get("/V")
        if v is None:
            continue
        try:
            v_dict = reader.get_object(v)
        except Exception:
            v_dict = v
        if not hasattr(v_dict, "get"):
            continue

        name = v_dict.get("/Name")
        if name and not meta.signer_full_name:
            meta.signer_full_name = str(name).strip()

        pdf_date = _parse_pdf_date_m(v_dict.get("/M"))
        if pdf_date:
            meta.signed_at = pdf_date

        contents = _pdf_contents_to_bytes(v_dict.get("/Contents"))
        byte_range = _parse_byte_range(v_dict.get("/ByteRange"))
        if len(contents) >= 20:
            parsed = _parse_pkcs7_contents(contents, byte_range)
            if parsed:
                if pdf_date and not parsed.signed_at:
                    parsed.signed_at = pdf_date
                cms_meta = _meta_from_parsed(parsed)
                meta.signer_full_name = meta.signer_full_name or cms_meta.signer_full_name
                meta.certificate_valid = cms_meta.certificate_valid
                meta.certificate_validity_label = cms_meta.certificate_validity_label
                meta.signed_at = meta.signed_at or cms_meta.signed_at
                meta.parsed_cms = parsed
                meta = _run_fz63(meta, path, settings)
                return meta
    return meta


def _ukep_validation(
    *,
    sig_flags: int | None,
    signature_widget_count: int,
    has_signed: bool,
    status: Status,
    message: str,
    meta: _SigMeta,
) -> BundlePdfUkepValidation:
    structural_only = meta.parsed_cms is None or not meta.fz63_checks
    return BundlePdfUkepValidation(
        sig_flags=sig_flags,
        signature_widget_count=signature_widget_count,
        has_signed_embedded_signature=has_signed,
        signer_full_name=meta.signer_full_name,
        certificate_valid=meta.certificate_valid,
        certificate_validity_label=meta.certificate_validity_label,
        signed_at=meta.signed_at,
        is_qualified_certificate=meta.is_qualified_certificate,
        fz63_compliant=meta.fz63_compliant,
        fz63_summary=meta.fz63_summary,
        fz63_checks=meta.fz63_checks,
        status=status,
        message=message,
        structural_validation_only=structural_only,
        note=UKEP_STRUCTURAL_NOTE,
    )


def _widget_is_signature(widget: object, sig_type: int | None) -> bool:
    fts = getattr(widget, "field_type_string", None)
    if fts == "Sig":
        return True
    ft = getattr(widget, "field_type", None)
    return sig_type is not None and ft == sig_type


def _count_signature_widgets_fitz(doc: fitz.Document) -> int:
    sig_type = getattr(fitz, "PDF_WIDGET_TYPE_SIGNATURE", None)
    total = 0
    for i in range(doc.page_count):
        page = doc.load_page(i)
        try:
            widgets_iter = page.widgets()
        except (AttributeError, RuntimeError, ValueError):
            widgets_iter = None
        if widgets_iter is not None:
            for w in widgets_iter:
                if _widget_is_signature(w, sig_type):
                    total += 1
            continue
        w = page.first_widget
        while w:
            if _widget_is_signature(w, sig_type):
                total += 1
            w = w.next
    return total


def _pypdf_embedded_signature_state(path: Path) -> tuple[int | None, int, bool]:
    try:
        reader = PdfReader(str(path), strict=False)
    except Exception:
        return None, 0, False
    fields = reader.get_fields()
    if not fields:
        return 0, 0, False
    n_sig = 0
    signed_any = False
    for field in fields.values():
        if not isinstance(field, dict) or not _name_is_sig(field.get("/FT")):
            continue
        n_sig += 1
        v = field.get("/V")
        if v is None:
            continue
        try:
            v_dict = reader.get_object(v)
        except Exception:
            v_dict = v
        if hasattr(v_dict, "get") and len(_pdf_contents_to_bytes(v_dict.get("/Contents"))) > 0:
            signed_any = True
    if n_sig == 0:
        return 0, 0, False
    return (3 if signed_any else 1), n_sig, signed_any


def _resolve_ukep_status(has_signed: bool, meta: _SigMeta) -> Status:
    if not has_signed:
        return "Требует проверки"
    if meta.fz63_compliant is False:
        return "Критично"
    if meta.fz63_compliant is None and meta.certificate_valid is False:
        return "Требует проверки"
    if meta.fz63_compliant is True and meta.certificate_valid is not False:
        return "OK"
    if meta.certificate_valid is False:
        return "Требует проверки"
    return "OK"


def analyze_embedded_ukep_structural(path: Path, settings: Settings | None = None) -> BundlePdfUkepValidation:
    settings = settings or get_settings()
    meta = extract_signature_details(path, settings)

    try:
        doc = fitz.open(path)
    except Exception as exc:
        return _ukep_validation(
            sig_flags=None,
            signature_widget_count=0,
            has_signed=False,
            status="Критично",
            message=f"Не удалось открыть PDF для анализа подписи: {exc}",
            meta=meta,
        )
    try:
        pypdf_flags, pypdf_widgets, pypdf_signed = _pypdf_embedded_signature_state(path)
        flags: int | None
        if hasattr(doc, "get_sigflags"):
            raw_flags = doc.get_sigflags()
            flags = int(raw_flags) if raw_flags is not None else None
        else:
            flags = None
        if flags is None or (flags is not None and flags < 0):
            flags = pypdf_flags

        widget_count = _count_signature_widgets_fitz(doc)
        if widget_count == 0 and pypdf_widgets > 0:
            widget_count = pypdf_widgets

        has_signed = (flags is not None and flags in (2, 3)) or pypdf_signed
        n_sig_fields = max(widget_count, pypdf_widgets)

        if has_signed:
            detail = f" Подписант: {meta.signer_full_name}." if meta.signer_full_name else ""
            if meta.fz63_summary:
                detail += f" {meta.fz63_summary}"
            elif not detail:
                detail = " Обнаружена встроенная подпись PDF."
            return _ukep_validation(
                sig_flags=flags,
                signature_widget_count=widget_count,
                has_signed=True,
                status=_resolve_ukep_status(True, meta),
                message=detail.strip(),
                meta=meta,
            )

        if n_sig_fields > 0:
            return _ukep_validation(
                sig_flags=flags,
                signature_widget_count=widget_count,
                has_signed=False,
                status="Требует проверки",
                message="Обнаружено поле подписи PDF, но подпись отсутствует или не подтверждена.",
                meta=meta,
            )

        return _ukep_validation(
            sig_flags=flags,
            signature_widget_count=widget_count,
            has_signed=False,
            status="Требует проверки",
            message="Встроенная подпись PDF не обнаружена (нет полей /Sig).",
            meta=meta,
        )
    finally:
        doc.close()


def worst_status(statuses: list[Status]) -> Status:
    if any(s == "Критично" for s in statuses):
        return "Критично"
    if any(s == "Требует проверки" for s in statuses):
        return "Требует проверки"
    return "OK"
