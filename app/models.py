import hashlib
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EType(str, Enum):
    email = "email"
    phone = "phone"
    name = "name"
    address = "address"
    username = "username"
    domain = "domain"
    ip = "ip"
    profile = "profile"
    breach = "breach"


class Entity(BaseModel):
    type: EType
    value: str
    attrs: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    depth: int = 0
    seed: bool = False

    @property
    def key(self) -> str:
        return entity_key(self.type, self.value)


def entity_key(etype: EType, value: str) -> str:
    return hashlib.sha1(f"{etype.value}:{value}".encode()).hexdigest()[:16]


class Finding(BaseModel):
    entity: Entity
    relation: str
    confidence: float
    evidence: dict[str, Any] = Field(default_factory=dict)


class ModuleResult(BaseModel):
    attrs: dict[str, Any] = Field(default_factory=dict)
    findings: list[Finding] = Field(default_factory=list)


class Edge(BaseModel):
    src: str
    dst: str
    relation: str
    module: str
    confidence: float
    evidence: dict[str, Any] = Field(default_factory=dict)


class CaseIn(BaseModel):
    ref: str = Field(min_length=1, description="Your KYC/application reference")
    purpose: str = Field(min_length=5, description="Lawful purpose for processing (POPIA s11)")
    seeds: list[str] = Field(min_length=1, description="Raw values or 'type:value'")
    max_depth: int = Field(default=2, ge=0, le=4)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    max_entities: int = Field(default=300, ge=10, le=2000)
