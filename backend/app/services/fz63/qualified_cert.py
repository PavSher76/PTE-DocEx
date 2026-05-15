"""Признаки квалифицированного сертификата по 63-ФЗ (ст. 5)."""

from __future__ import annotations

from asn1crypto import x509

from app.services.fz63.asn1_utils import safe_signature_algorithm_oid, safe_spki_algorithm_oid
from app.services.fz63.constants import (
    COMPLIANCE_POLICY_PREFIXES,
    QUALIFIED_POLICY_PREFIXES,
    RUSSIAN_COUNTRY_OIDS,
    RUSSIAN_SIG_ALGO_PREFIXES,
)


def _oid_matches_prefix(oid: str, prefixes: tuple[str, ...]) -> bool:
    return any(oid == p or oid.startswith(p + ".") for p in prefixes)


def _collect_policy_oids(cert: x509.Certificate) -> list[str]:
    oids: list[str] = []
    ext = cert["tbs_certificate"]["extensions"]
    if not ext:
        return oids
    for extension in ext:
        if extension["extn_id"].dotted != "2.5.29.32":
            continue
        policies = extension["extn_value"].parsed
        for policy in policies or []:
            pid = policy["policy_identifier"].dotted
            oids.append(pid)
    return oids


def _collect_eku_oids(cert: x509.Certificate) -> list[str]:
    oids: list[str] = []
    ext = cert["tbs_certificate"]["extensions"]
    if not ext:
        return oids
    for extension in ext:
        if extension["extn_id"].dotted != "2.5.29.37":
            continue
        eku = extension["extn_value"].parsed
        for oid in eku or []:
            oids.append(oid.dotted if hasattr(oid, "dotted") else str(oid))
    return oids


def _is_russian_certificate(cert: x509.Certificate) -> bool:
    subject = cert.subject.native
    country = subject.get("country_name") or subject.get("c")
    if country and str(country).upper() in {"RU", "RUS", "РФ", "RUSSIA"}:
        return True
    for key in subject:
        ks = str(key)
        if ks.startswith("1.2.643") or ks in RUSSIAN_COUNTRY_OIDS:
            return True
    sig_oid = safe_signature_algorithm_oid(cert)
    if sig_oid and _oid_matches_prefix(sig_oid, RUSSIAN_SIG_ALGO_PREFIXES):
        return True
    spki_oid = safe_spki_algorithm_oid(cert)
    if spki_oid and _oid_matches_prefix(spki_oid, RUSSIAN_SIG_ALGO_PREFIXES):
        return True
    return False


def is_qualified_russian_certificate(cert: x509.Certificate) -> tuple[bool, str]:
    """Квалифицированный сертификат РФ: политики КС/КВ, российский субъект, ГОСТ."""
    if not _is_russian_certificate(cert):
        return False, "Сертификат не относится к российской инфраструктуре УКЭП (страна/алгоритм)."

    policies = _collect_policy_oids(cert)
    eku = _collect_eku_oids(cert)
    qualified_policy = any(_oid_matches_prefix(p, QUALIFIED_POLICY_PREFIXES) for p in policies)
    compliance_policy = any(_oid_matches_prefix(p, COMPLIANCE_POLICY_PREFIXES) for p in policies)
    qualified_eku = any(_oid_matches_prefix(e, QUALIFIED_POLICY_PREFIXES) for e in eku)

    if not (qualified_policy or qualified_eku):
        return (
            False,
            "В сертификате нет политики квалифицированной ЭП (OID 1.2.643.100.113.x) или соответствующего EKU.",
        )

    spki_oid = safe_spki_algorithm_oid(cert)
    if not spki_oid or not _oid_matches_prefix(spki_oid, RUSSIAN_SIG_ALGO_PREFIXES):
        label = spki_oid or "не определён"
        return False, f"Ключ подписи не на алгоритме ГОСТ РФ (OID {label})."

    return True, "Сертификат содержит признаки квалифицированной УКЭП РФ (политики/алгоритмы)."
