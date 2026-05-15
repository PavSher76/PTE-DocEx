"""Криптографическая проверка CMS (ГОСТ) и message-digest PDF."""

from __future__ import annotations

import hashlib
from datetime import datetime

from asn1crypto import cms, core, x509

from app.services.fz63.asn1_utils import safe_public_key_bytes
from app.services.fz63.constants import OID_MESSAGE_DIGEST
from app.services.fz63.constants import RUSSIAN_SIG_ALGO_PREFIXES
from app.services.fz63.pdf_byte_range import hash_pdf_byte_range
from pathlib import Path


def _oid_prefix(oid: str) -> bool:
    return any(oid == p or oid.startswith(p + ".") for p in RUSSIAN_SIG_ALGO_PREFIXES)


def _gost_digest(data: bytes, digest_oid: str) -> bytes | None:
    try:
        from gostcrypto import gosthash
    except ImportError:
        return None
    try:
        if "34.11-2012-256" in digest_oid or digest_oid.endswith("1.2.643.7.1.1.2.2"):
            h = gosthash.new("streebog256", data=data)
        elif "34.11-2012-512" in digest_oid or digest_oid.endswith("1.2.643.7.1.1.2.3"):
            h = gosthash.new("streebog512", data=data)
        elif "34.11-94" in digest_oid or "2.2.2" in digest_oid:
            h = gosthash.new("gost94", data=data)
        else:
            h = gosthash.new("streebog256", data=data)
        return h.digest()
    except Exception:
        return None


def _gost_verify(digest: bytes, signature: bytes, cert: x509.Certificate, sig_oid: str) -> bool | None:
    try:
        from gostcrypto import gostsignature
    except ImportError:
        return None
    pub_bytes = safe_public_key_bytes(cert)
    if not pub_bytes:
        return None
    param_set = None
    try:
        params = cert["tbs_certificate"]["subject_public_key_info"]["algorithm"].get("parameters")
        if params is not None:
            param_set = params.native
    except (KeyError, Exception):
        param_set = None
    try:
        if "34.10-2012-512" in sig_oid or "1.2.643.7.1.1.1.2" in sig_oid:
            mode = "MODE_512"
        else:
            mode = "MODE_256"
        verifier = gostsignature.new(mode, pub_bytes, param_set)
        return bool(verifier.verify(digest, signature))
    except Exception:
        return None


def _rsa_verify(digest: bytes, signature: bytes, cert: x509.Certificate, digest_oid: str) -> bool | None:
    try:
        from cryptography import x509 as cx509
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding, utils
    except ImportError:
        return None
    try:
        cx = cx509.load_der_x509_certificate(cert.dump())
        pub = cx.public_key()
        if "sha256" in digest_oid.lower():
            algo = hashes.SHA256()
        elif "sha1" in digest_oid.lower():
            algo = hashes.SHA1()
        else:
            algo = hashes.SHA256()
        pub.verify(signature, digest, padding.PKCS1v15(), utils.Prehashed(algo))
        return True
    except Exception:
        return False


def _standard_digest(data: bytes, digest_oid: str) -> bytes:
    if "sha256" in digest_oid:
        return hashlib.sha256(data).digest()
    if "sha1" in digest_oid or "1.3.14.3.2.26" in digest_oid:
        return hashlib.sha1(data).digest()
    return hashlib.sha256(data).digest()


def _signed_attrs_digest(signer_info: cms.SignerInfo) -> bytes | None:
    signed_attrs = signer_info["signed_attrs"]
    if signed_attrs is None:
        return None
    # DER SET OF signed attributes (tag 0xA0 implicit in CMS)
    return signed_attrs.dump()


def _message_digest_from_attrs(signer_info: cms.SignerInfo) -> bytes | None:
    signed_attrs = signer_info["signed_attrs"]
    if signed_attrs is None:
        return None
    for attr in signed_attrs:
        if attr["type"].dotted != OID_MESSAGE_DIGEST:
            continue
        val = attr["values"][0].native
        if isinstance(val, bytes):
            return val
        if isinstance(val, core.OctetString):
            return val.native
    return None


def verify_cms_signature(
    signed_data: cms.SignedData,
    signer_info: cms.SignerInfo,
    signer_cert: x509.Certificate,
) -> tuple[bool | None, str]:
    digest_oid = signer_info["digest_algorithm"]["algorithm"].dotted
    sig_oid = signer_info["signature_algorithm"]["algorithm"].dotted
    attrs_der = _signed_attrs_digest(signer_info)
    if attrs_der is None:
        return None, "Нет подписанных атрибутов CMS."
    if _oid_prefix(digest_oid):
        digest = _gost_digest(attrs_der, digest_oid)
    else:
        digest = _standard_digest(attrs_der, digest_oid)
    if digest is None:
        return None, "Не удалось вычислить хеш подписанных атрибутов (ГОСТ)."
    sig_bytes = signer_info["signature"].native
    if not isinstance(sig_bytes, bytes):
        sig_bytes = bytes(sig_bytes)
    if _oid_prefix(sig_oid):
        ok = _gost_verify(digest, sig_bytes, signer_cert, sig_oid)
        if ok is True:
            return True, "Криптографическая подпись CMS (ГОСТ) подтверждена."
        if ok is False:
            return False, "Криптографическая подпись CMS (ГОСТ) не прошла проверку."
        return None, "Модуль gostcrypto недоступен для проверки ГОСТ."
    ok = _rsa_verify(digest, sig_bytes, signer_cert, digest_oid)
    if ok is True:
        return True, "Криптографическая подпись CMS подтверждена."
    if ok is False:
        return False, "Криптографическая подпись CMS не прошла проверку."
    return None, "Алгоритм подписи не поддерживается для автоматической проверки."


def verify_pdf_message_digest(
    pdf_path: Path,
    byte_range: list[int],
    signer_info: cms.SignerInfo,
) -> tuple[bool | None, str]:
    expected = _message_digest_from_attrs(signer_info)
    if expected is None:
        return None, "Атрибут message-digest отсутствует в подписи."
    payload = hash_pdf_byte_range(pdf_path, byte_range)
    if payload is None:
        return False, "Некорректный ByteRange PDF."
    digest_oid = signer_info["digest_algorithm"]["algorithm"].dotted
    if _oid_prefix(digest_oid):
        actual = _gost_digest(payload, digest_oid)
    else:
        actual = _standard_digest(payload, digest_oid)
    if actual is None:
        return None, "Не удалось вычислить хеш документа (ГОСТ)."
    if actual == expected:
        return True, "Хеш PDF по ByteRange совпадает с message-digest подписи."
    return False, "Хеш PDF не совпадает с message-digest (документ изменён после подписания)."
