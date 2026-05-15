"""Комплексная проверка УКЭП РФ по 63-ФЗ."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from asn1crypto import cms, x509

from app.schemas import Fz63CheckItem, Status
from app.services.fz63.cms_crypto import verify_cms_signature, verify_pdf_message_digest
from app.services.fz63.constants import FZ63_NOTE
from app.services.fz63.crl_check import check_certificate_revocation
from app.services.fz63.qualified_cert import is_qualified_russian_certificate
from app.services.fz63.trust_chain import is_accredited_issuer, verify_trust_chain


@dataclass
class ParsedCmsSignature:
    signer_cert: x509.Certificate
    all_certs: list[x509.Certificate]
    signed_data: cms.SignedData
    signer_info: cms.SignerInfo
    signed_at: datetime | None
    byte_range: list[int] | None = None


@dataclass
class Fz63ValidationResult:
    compliant: bool
    summary: str
    checks: list[Fz63CheckItem] = field(default_factory=list)
    is_qualified: bool | None = None
    trust_chain_valid: bool | None = None
    revocation_ok: bool | None = None
    crypto_ok: bool | None = None
    pdf_integrity_ok: bool | None = None


def _ensure_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _cert_period_ok(cert: x509.Certificate, moment: datetime) -> tuple[bool, str]:
    nb = _ensure_aware(cert["tbs_certificate"]["validity"]["not_before"].native)
    na = _ensure_aware(cert["tbs_certificate"]["validity"]["not_after"].native)
    m = _ensure_aware(moment)
    if m < nb:
        return False, "Сертификат на дату подписи ещё не действовал."
    if m > na:
        return False, "Срок действия сертификата на дату подписи истёк."
    return True, "Срок действия сертификата на дату подписи в порядке."


def validate_russian_ukep(
    parsed: ParsedCmsSignature,
    pdf_path: Path | None = None,
    *,
    crl_timeout: float = 12.0,
    require_crl: bool = True,
) -> Fz63ValidationResult:
    checks: list[Fz63CheckItem] = []
    moment = parsed.signed_at or datetime.now(timezone.utc)

    qualified, q_msg = is_qualified_russian_certificate(parsed.signer_cert)
    checks.append(
        Fz63CheckItem(
            id="qualified_cert",
            title="Квалифицированный сертификат РФ (63-ФЗ, ст. 5)",
            passed=qualified,
            detail=q_msg,
        )
    )

    period_ok, period_msg = _cert_period_ok(parsed.signer_cert, moment)
    checks.append(
        Fz63CheckItem(
            id="cert_period",
            title="Срок действия сертификата на дату подписи",
            passed=period_ok,
            detail=period_msg,
        )
    )

    accredited, acc_msg = is_accredited_issuer(parsed.signer_cert)
    checks.append(
        Fz63CheckItem(
            id="accredited_ca",
            title="Аккредитованный удостоверяющий центр РФ",
            passed=accredited,
            detail=acc_msg,
        )
    )

    chain_ok, chain_msg, _chain = verify_trust_chain(parsed.signer_cert, parsed.all_certs)
    checks.append(
        Fz63CheckItem(
            id="trust_chain",
            title="Цепочка до корня доверия / УЦ РФ",
            passed=chain_ok,
            detail=chain_msg,
        )
    )

    rev_ok, rev_msg = check_certificate_revocation(
        parsed.signer_cert,
        moment,
        timeout_seconds=crl_timeout,
        require_crl=require_crl,
    )
    checks.append(
        Fz63CheckItem(
            id="crl",
            title="Статус отзыва (CRL)",
            passed=rev_ok,
            detail=rev_msg,
        )
    )

    crypto_ok, crypto_msg = verify_cms_signature(
        parsed.signed_data,
        parsed.signer_info,
        parsed.signer_cert,
    )
    checks.append(
        Fz63CheckItem(
            id="cms_crypto",
            title="Криптографическая проверка подписи CMS",
            passed=crypto_ok,
            detail=crypto_msg,
        )
    )

    pdf_ok: bool | None = None
    pdf_msg = "ByteRange PDF не проверялся."
    if pdf_path and parsed.byte_range:
        pdf_ok, pdf_msg = verify_pdf_message_digest(pdf_path, parsed.byte_range, parsed.signer_info)
    elif pdf_path:
        pdf_msg = "В подписи PDF отсутствует ByteRange."
    checks.append(
        Fz63CheckItem(
            id="pdf_integrity",
            title="Целостность PDF (ByteRange / message-digest)",
            passed=pdf_ok,
            detail=pdf_msg,
        )
    )

    hard_fail = any(c.passed is False for c in checks if c.id in {"qualified_cert", "cert_period", "cms_crypto", "pdf_integrity"})
    soft_fail = any(
        c.passed is False
        for c in checks
        if c.id in {"accredited_ca", "trust_chain", "crl"}
    )
    soft_unknown = any(c.passed is None for c in checks if c.id in {"crl", "cms_crypto", "pdf_integrity"})

    if hard_fail:
        compliant = False
        summary = "Не соответствует требованиям 63-ФЗ: выявлены критические несоответствия."
    elif soft_fail:
        compliant = False
        summary = "Не соответствует требованиям 63-ФЗ: цепочка доверия, УЦ или отзыв."
    elif soft_unknown:
        compliant = False
        summary = "Требует проверки: не все проверки 63-ФЗ выполнены (CRL/крипто/целостность)."
    else:
        compliant = True
        summary = "Соответствует проверкам 63-ФЗ для квалифицированной УКЭП РФ (автоматический режим)."

    return Fz63ValidationResult(
        compliant=compliant,
        summary=summary,
        checks=checks,
        is_qualified=qualified,
        trust_chain_valid=chain_ok,
        revocation_ok=rev_ok,
        crypto_ok=crypto_ok,
        pdf_integrity_ok=pdf_ok,
    )


def fz63_note() -> str:
    return FZ63_NOTE
