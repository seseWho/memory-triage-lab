from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class MemoryType(StrEnum):
    CONSTRAINT = "constraint"
    DECISION = "decision"
    EVIDENCE = "evidence"
    EPISODE = "episode"
    PREFERENCE = "preference"


class Criticality(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"


class RetentionPolicy(StrEnum):
    PIN = "pin"
    COMPACT = "compact"
    RETRIEVE = "retrieve"


@dataclass(frozen=True, slots=True)
class MemoryItem:
    id: str
    type: MemoryType
    text: str
    criticality: Criticality
    scope: str
    provenance: str
    retention_policy: RetentionPolicy
    check_terms: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryItem:
        item = cls(
            id=str(data["id"]),
            type=MemoryType(data["type"]),
            text=str(data["text"]),
            criticality=Criticality(data["criticality"]),
            scope=str(data["scope"]),
            provenance=str(data["provenance"]),
            retention_policy=RetentionPolicy(data["retention_policy"]),
            check_terms=tuple(str(term) for term in data["check_terms"]),
        )
        item.validate()
        return item

    def validate(self) -> None:
        if not self.id.strip() or not self.text.strip():
            raise ValueError("Memory item id and text must not be empty")
        if not self.check_terms or any(not term.strip() for term in self.check_terms):
            raise ValueError(f"Memory item {self.id} requires non-empty check_terms")


@dataclass(frozen=True, slots=True)
class StrategySnapshot:
    active_items: tuple[MemoryItem, ...]
    retrievable_items: tuple[MemoryItem, ...] = ()
    retrieved_items: tuple[MemoryItem, ...] = ()
    model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_seconds: float | None = None

    @property
    def all_items(self) -> tuple[MemoryItem, ...]:
        seen: set[str] = set()
        result: list[MemoryItem] = []
        for item in (*self.active_items, *self.retrieved_items, *self.retrievable_items):
            if item.id not in seen:
                seen.add(item.id)
                result.append(item)
        return tuple(result)
