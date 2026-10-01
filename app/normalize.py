import ipaddress
import re
import unicodedata

import phonenumbers

from app.models import Entity, EType

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$", re.I)
USERNAME_RE = re.compile(r"^@?[a-z0-9._-]{2,40}$", re.I)
NAME_RE = re.compile(r"^[^\W\d_]+(?:[ '\-.][^\W\d_]+){1,4}$")
PHONE_CHARS_RE = re.compile(r"^\+?[\d\s().-]{7,20}$")


def _clean(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", s).split())


def norm_phone(raw: str, region: str) -> str | None:
    try:
        n = phonenumbers.parse(raw, region)
    except phonenumbers.NumberParseException:
        return None
    if not phonenumbers.is_possible_number(n):
        return None
    return phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)


def norm_name(raw: str) -> str:
    return _clean(raw).title()


def norm_address(raw: str) -> str:
    return re.sub(r"\s*,\s*", ", ", _clean(raw)).strip(", ")


def normalize(etype: EType, raw: str, region: str = "ZA") -> str | None:
    raw = _clean(raw)
    match etype:
        case EType.email:
            return raw.lower() if EMAIL_RE.match(raw) else None
        case EType.phone:
            return norm_phone(raw, region)
        case EType.ip:
            try:
                return str(ipaddress.ip_address(raw))
            except ValueError:
                return None
        case EType.domain:
            d = raw.lower().removeprefix("http://").removeprefix("https://").split("/")[0].removeprefix("www.")
            return d if DOMAIN_RE.match(d) else None
        case EType.username:
            return raw.lstrip("@").lower() if USERNAME_RE.match(raw) else None
        case EType.name:
            return norm_name(raw)
        case EType.address:
            return norm_address(raw)
        case _:
            return raw


def detect(raw: str, region: str = "ZA") -> Entity | None:
    raw = _clean(raw)
    if not raw:
        return None
    prefix, sep, rest = raw.partition(":")
    if sep and prefix.lower() in EType._value2member_map_ and rest.strip():
        etype = EType(prefix.lower())
        value = normalize(etype, rest, region)
        return Entity(type=etype, value=value, seed=True) if value else None

    order: list[EType] = [EType.email, EType.ip]
    if PHONE_CHARS_RE.match(raw):
        order.append(EType.phone)
    if "." in raw and " " not in raw:
        order.append(EType.domain)
    if any(c.isdigit() for c in raw) and (" " in raw or "," in raw):
        order.append(EType.address)
    if NAME_RE.match(raw):
        order.append(EType.name)
    if raw.startswith("@") or " " not in raw:
        order.append(EType.username)
    if "," in raw:
        order.append(EType.address)

    for etype in order:
        value = normalize(etype, raw, region)
        if value:
            return Entity(type=etype, value=value, seed=True)
    return None
