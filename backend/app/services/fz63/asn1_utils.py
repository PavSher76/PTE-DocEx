"""Безопасное чтение OID и ключей из сертификатов РФ (ГОСТ 1.2.643.*)."""

from __future__ import annotations

from asn1crypto import x509
from asn1crypto.core import ObjectIdentifier


def _iter_oids_in_der(data: bytes) -> list[str]:
    oids: list[str] = []
    pos = 0
    length = len(data)
    while pos < length - 1:
        if data[pos] != 0x06:
            pos += 1
            continue
        pos += 1
        lb = data[pos]
        pos += 1
        if lb & 0x80:
            n = lb & 0x7F
            if pos + n > length:
                break
            ln = int.from_bytes(data[pos : pos + n], "big")
            pos += n
        else:
            ln = lb
        if pos + ln > length:
            break
        try:
            oids.append(ObjectIdentifier.load(data[pos : pos + ln]).dotted)
        except Exception:
            pass
        pos += ln
    return oids


def _oids_via_cryptography(cert: x509.Certificate) -> tuple[str | None, str | None]:
    try:
        from cryptography import x509 as cx509

        cx = cx509.load_der_x509_certificate(cert.dump())
        sig = cx.signature_algorithm_oid
        sig_oid = sig.dotted if sig is not None else None
        pub_oid: str | None = None
        pub_algo = getattr(cx, "public_key_algorithm_oid", None)
        if pub_algo is not None:
            pub_oid = pub_algo.dotted
        return sig_oid, pub_oid
    except Exception:
        return None, None


def _pick_spki_oid(oids: list[str]) -> str | None:
    for oid in oids:
        if oid.startswith("1.2.643.7.1.1") or oid.startswith("1.2.643.2.2"):
            return oid
    for oid in oids:
        if oid.startswith("1.2.643."):
            return oid
    return None


def _tbs_der(cert: x509.Certificate) -> bytes:
    try:
        return cert["tbs_certificate"].dump()
    except Exception:
        return cert.dump()


def safe_spki_algorithm_oid(cert: x509.Certificate) -> str | None:
    _, pub = _oids_via_cryptography(cert)
    if pub:
        return pub
    return _pick_spki_oid(_iter_oids_in_der(_tbs_der(cert)))


def safe_signature_algorithm_oid(cert: x509.Certificate) -> str | None:
    sig, _ = _oids_via_cryptography(cert)
    if sig:
        return sig
    oids = _iter_oids_in_der(_tbs_der(cert))
    return oids[0] if oids else None


def _read_asn1_length(data: bytes, pos: int) -> tuple[int, int] | None:
    if pos >= len(data):
        return None
    lb = data[pos]
    pos += 1
    if lb & 0x80:
        n = lb & 0x7F
        if pos + n > len(data):
            return None
        ln = int.from_bytes(data[pos : pos + n], "big")
        pos += n
    else:
        ln = lb
    return ln, pos


def _parse_bit_string_at(data: bytes, pos: int) -> bytes | None:
    if pos >= len(data) or data[pos] != 0x03:
        return None
    read = _read_asn1_length(data, pos + 1)
    if read is None:
        return None
    ln, start = read
    content = data[start : start + ln]
    if not content:
        return b""
    return content[1:] if len(content) > 1 else content


def safe_public_key_bytes(cert: x509.Certificate) -> bytes | None:
    spki_oid = safe_spki_algorithm_oid(cert)
    if spki_oid:
        try:
            oid_der = ObjectIdentifier(spki_oid).dump()
        except Exception:
            oid_der = b""
        if oid_der:
            der = cert.dump()
            pos = der.find(oid_der)
            if pos >= 0:
                bit_pos = der.find(b"\x03", pos, min(pos + 256, len(der)))
                if bit_pos >= 0:
                    key = _parse_bit_string_at(der, bit_pos)
                    if key:
                        return key

    try:
        spki_der = cert["tbs_certificate"]["subject_public_key_info"].dump()
        bit_pos = spki_der.find(b"\x03")
        if bit_pos >= 0:
            return _parse_bit_string_at(spki_der, bit_pos)
    except Exception:
        pass

    return None
