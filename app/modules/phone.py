import phonenumbers
from phonenumbers import carrier, geocoder, timezone

from app.models import Entity, EType, ModuleResult
from app.modules.base import Ctx, Module

TYPES = {v: k.lower() for k, v in vars(phonenumbers.PhoneNumberType).items() if k.isupper()}


class PhoneInfo(Module):
    name = "phone_info"
    accepts = {EType.phone}

    async def run(self, entity: Entity, ctx: Ctx) -> ModuleResult:
        n = phonenumbers.parse(entity.value)
        return ModuleResult(attrs={
            "valid": phonenumbers.is_valid_number(n),
            "line_type": TYPES.get(phonenumbers.number_type(n), "unknown"),
            "country": phonenumbers.region_code_for_number(n),
            "region": geocoder.description_for_number(n, "en") or None,
            "carrier_allocated": carrier.name_for_number(n, "en") or None,
            "timezones": list(timezone.time_zones_for_number(n)),
        })
