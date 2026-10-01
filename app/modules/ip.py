from app.models import Entity, EType, Finding, ModuleResult
from app.modules.base import Ctx, Module, get_json
from app.normalize import normalize


class InternetDB(Module):
    name = "shodan_internetdb"
    accepts = {EType.ip}

    async def run(self, entity: Entity, ctx: Ctx) -> ModuleResult:
        url = f"https://internetdb.shodan.io/{entity.value}"
        status, data = await get_json(ctx, url)
        if status != 200 or not isinstance(data, dict):
            return ModuleResult()
        findings = []
        for host in data.get("hostnames", []):
            d = normalize(EType.domain, host)
            if d:
                findings.append(Finding(
                    entity=Entity(type=EType.domain, value=d),
                    relation="resolves_from", confidence=0.7, evidence={"source": url},
                ))
        return ModuleResult(
            attrs={k: data.get(k, []) for k in ("ports", "vulns", "cpes", "tags")},
            findings=findings,
        )


class IPInfo(Module):
    name = "ipinfo"
    accepts = {EType.ip}

    async def run(self, entity: Entity, ctx: Ctx) -> ModuleResult:
        params = {"token": ctx.settings.ipinfo_token} if ctx.settings.ipinfo_token else None
        status, data = await get_json(ctx, f"https://ipinfo.io/{entity.value}/json", params=params)
        if status != 200 or not isinstance(data, dict) or data.get("bogon"):
            return ModuleResult()
        return ModuleResult(attrs={
            "city": data.get("city"), "region": data.get("region"),
            "country": data.get("country"), "org": data.get("org"),
            "rdns": data.get("hostname"),
        })
