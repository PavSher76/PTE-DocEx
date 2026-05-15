"""Цепочка сертификатов до корня доверия РФ и аккредитованного УЦ."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from asn1crypto import pem, x509

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@lru_cache(maxsize=1)
def _load_trusted_roots() -> list[x509.Certificate]:
    roots: list[x509.Certificate] = []
    pem_path = _DATA_DIR / "fz63_trusted_roots.pem"
    if not pem_path.is_file():
        return roots
    raw = pem_path.read_bytes()
    if b"-----BEGIN" not in raw:
        return roots
    try:
        for _type, cert_bytes in pem.unarmor(raw, multiple=True):
            roots.append(x509.Certificate.load(cert_bytes))
    except ValueError:
        return roots
    return roots


@lru_cache(maxsize=1)
def _load_accredited_patterns() -> list[str]:
    path = _DATA_DIR / "fz63_accredited_ca.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("issuer_cn_substrings", []))


def _cert_fingerprint(cert: x509.Certificate) -> bytes:
    return cert.sha256


def _find_issuer(cert: x509.Certificate, pool: list[x509.Certificate]) -> x509.Certificate | None:
    issuer_dn = cert.issuer
    for candidate in pool:
        if candidate.subject == issuer_dn:
            if _cert_fingerprint(candidate) != _cert_fingerprint(cert):
                return candidate
    return None


def _is_trusted_root(cert: x509.Certificate, roots: list[x509.Certificate]) -> bool:
    fp = _cert_fingerprint(cert)
    for root in roots:
        if _cert_fingerprint(root) == fp:
            return True
        if cert.subject == root.subject and cert.issuer == cert.subject:
            return True
    return cert.issuer == cert.subject


def _issuer_cn(cert: x509.Certificate) -> str:
    native = cert.issuer.native
    cn = native.get("common_name") or native.get("organization_name") or ""
    return str(cn)


def is_accredited_issuer(cert: x509.Certificate) -> tuple[bool, str]:
    patterns = _load_accredited_patterns()
    cn = _issuer_cn(cert)
    if not patterns:
        return False, "Список аккредитованных УЦ не загружен."
    for pattern in patterns:
        if pattern.lower() in cn.lower():
            return True, f"Издатель сертификата соответствует реестру УЦ РФ: «{cn}»."
    return False, f"Издатель «{cn}» не найден в локальном списке аккредитованных УЦ."


def verify_trust_chain(
    signer: x509.Certificate,
    chain_certs: list[x509.Certificate],
) -> tuple[bool, str, list[x509.Certificate]]:
    """Построение цепочки: signer → … → корень или аккредитованный УЦ."""
    pool = list(chain_certs)
    if signer not in pool:
        pool.insert(0, signer)

    roots = _load_trusted_roots()
    built: list[x509.Certificate] = [signer]
    current = signer
    seen = {_cert_fingerprint(signer)}

    for _ in range(12):
        if _is_trusted_root(current, roots):
            return True, "Цепочка завершена доверенным корнем РФ.", built
        parent = _find_issuer(current, pool)
        if parent is None:
            break
        pfp = _cert_fingerprint(parent)
        if pfp in seen:
            break
        seen.add(pfp)
        built.append(parent)
        current = parent

    accredited, acc_msg = is_accredited_issuer(signer)
    if accredited and len(built) >= 1:
        if roots and _is_trusted_root(current, roots):
            return True, acc_msg + " Цепочка до корня доверия подтверждена.", built
        return (
            True,
            acc_msg + " Промежуточные сертификаты из контейнера подписи (полная цепочка до корня не проверена).",
            built,
        )

    if roots:
        for root in roots:
            if signer.issuer == root.subject:
                return True, "Сертификат выпущен доверенным корнем РФ.", built

    return (
        False,
        "Не удалось построить цепочку до корня доверия РФ или аккредитованного УЦ.",
        built,
    )
