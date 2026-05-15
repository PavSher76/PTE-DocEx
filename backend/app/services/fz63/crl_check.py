"""Проверка отзыва по CRL (63-ФЗ, ст. 5 — действительность сертификата)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from asn1crypto import crl, x509


def _urls_from_general_names(names: Any) -> list[str]:
    urls: list[str] = []
    if names is None:
        return urls
    for name in names:
        try:
            if name.name == "uniform_resource_identifier":
                value = name.native
                if value:
                    urls.append(str(value))
        except AttributeError:
            continue
    return urls


def _urls_from_dp_name(dp_name: Any) -> list[str]:
    if dp_name is None:
        return []
    try:
        if dp_name.name == "full_name":
            return _urls_from_general_names(dp_name.chosen)
    except AttributeError:
        pass
    return []


def _urls_from_distribution_point(dist_point: Any) -> list[str]:
    urls: list[str] = []
    try:
        dpn = dist_point["distribution_point"]
        urls.extend(_urls_from_dp_name(dpn))
    except (KeyError, TypeError, AttributeError):
        pass
    try:
        native = dist_point.native
        if isinstance(native, dict):
            dp = native.get("distribution_point") or {}
            full = dp.get("full_name") or []
            for item in full:
                if isinstance(item, dict) and "uniform_resource_identifier" in item:
                    urls.append(str(item["uniform_resource_identifier"]))
                elif isinstance(item, str) and item.startswith("http"):
                    urls.append(item)
    except Exception:
        pass
    return urls


def _crl_urls(cert: x509.Certificate) -> list[str]:
    urls: list[str] = []
    try:
        ext = cert["tbs_certificate"]["extensions"]
        if not ext:
            return urls
        for extension in ext:
            if extension["extn_id"].dotted != "2.5.29.31":
                continue
            dp_list = extension["extn_value"].parsed
            if not dp_list:
                continue
            for dist_point in dp_list:
                urls.extend(_urls_from_distribution_point(dist_point))
    except Exception:
        pass
    # убрать дубликаты, сохранить порядок
    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def _is_revoked(
    cert_list: crl.CertificateList,
    serial: int,
    moment: datetime,
) -> bool:
    try:
        tbs = cert_list["tbs_cert_list"]
        revoked = tbs["revoked_certificates"]
    except (KeyError, TypeError):
        return False
    if not revoked:
        return False
    for entry in revoked:
        try:
            if entry["user_certificate"].native != serial:
                continue
            rev_date = entry["revocation_date"].native
            if isinstance(rev_date, datetime) and rev_date <= moment:
                return True
        except (KeyError, TypeError):
            continue
    return False


def check_certificate_revocation(
    cert: x509.Certificate,
    moment: datetime,
    *,
    timeout_seconds: float = 12.0,
    require_crl: bool = True,
) -> tuple[bool | None, str]:
    """
    None — CRL не проверялся (нет URL или сеть).
    True — не отозван.
    False — отозван.
    """
    urls = _crl_urls(cert)
    if not urls:
        if require_crl:
            return None, "В сертификате не указан URL CRL; отзыв не подтверждён."
        return None, "CRL не указан (проверка пропущена)."

    last_error = ""
    for url in urls[:3]:
        try:
            with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
            cert_list = crl.CertificateList.load(response.content)
            serial = cert["tbs_certificate"]["serial_number"].native
            if _is_revoked(cert_list, serial, moment):
                return False, f"Сертификат отозван (CRL: {url})."
            return True, "Сертификат не найден в CRL (не отозван)."
        except Exception as exc:
            last_error = str(exc)
            continue

    if require_crl:
        return None, f"Не удалось загрузить CRL: {last_error or 'нет ответа'}"
    return None, f"CRL недоступен: {last_error}"
