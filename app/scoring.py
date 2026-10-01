import jellyfish
from rapidfuzz import fuzz

from app.models import Entity, EType

NAME_MATCH = 0.45
SURNAME_PHONETIC = 0.2
LOCATION_MATCH = 0.3
EXACT_SEED = 0.6


def noisy_or(*ps: float) -> float:
    out = 1.0
    for p in ps:
        out *= 1.0 - max(0.0, min(1.0, p))
    return round(1.0 - out, 4)


def name_similarity(a: str, b: str) -> float:
    return fuzz.token_sort_ratio(a.lower(), b.lower()) / 100.0


def surname_phonetic(a: str, b: str) -> bool:
    sa, sb = a.split()[-1], b.split()[-1]
    return len(sa) > 2 and len(sb) > 2 and jellyfish.metaphone(sa) == jellyfish.metaphone(sb)


def _location_tokens(address: str) -> set[str]:
    parts = [p.strip().lower() for p in address.split(",")]
    return {p for p in parts if p and not any(c.isdigit() for c in p)}


def corroborate(entity: Entity, seeds: list[Entity]) -> list[tuple[str, float]]:
    hits: list[tuple[str, float]] = []
    name = str(entity.attrs.get("name") or entity.attrs.get("display_name") or "")
    location = str(entity.attrs.get("location") or entity.attrs.get("city") or "").lower()
    linked = {str(v).lower() for v in entity.attrs.get("linked", [])}

    for s in seeds:
        if s.type == EType.name and name:
            sim = name_similarity(name, s.value)
            if sim >= 0.85:
                hits.append((f"name~{s.value} ({sim:.2f})", NAME_MATCH))
            elif surname_phonetic(name, s.value):
                hits.append((f"surname-phonetic~{s.value}", SURNAME_PHONETIC))
        elif s.type == EType.address and location:
            if any(tok in location or location in tok for tok in _location_tokens(s.value)):
                hits.append((f"location~{s.value}", LOCATION_MATCH))
        elif s.value.lower() in linked:
            hits.append((f"links-seed:{s.type.value}", EXACT_SEED))
    return hits


def score(base: float, hits: list[tuple[str, float]]) -> float:
    return noisy_or(base, *(w for _, w in hits))
