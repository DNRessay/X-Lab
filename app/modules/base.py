from dataclasses import dataclass
from typing import ClassVar

import httpx

from app.config import Settings
from app.models import Entity, EType, ModuleResult


@dataclass
class Ctx:
    client: httpx.AsyncClient
    settings: Settings


class Module:
    name: ClassVar[str]
    accepts: ClassVar[set[EType]]

    def enabled(self, settings: Settings) -> bool:
        return True

    async def run(self, entity: Entity, ctx: Ctx) -> ModuleResult:
        raise NotImplementedError


async def get_json(ctx: Ctx, url: str, **kw) -> tuple[int, dict | list | None]:
    r = await ctx.client.get(url, **kw)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, None
