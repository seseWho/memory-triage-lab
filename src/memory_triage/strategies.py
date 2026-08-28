from __future__ import annotations

from typing import Protocol

from memory_triage.domain import (
    Criticality,
    MemoryItem,
    MemoryType,
    RetentionPolicy,
    StrategySnapshot,
)


class MemoryStrategy(Protocol):
    name: str

    def compact(self, items: tuple[MemoryItem, ...], round_number: int) -> StrategySnapshot: ...


class FakeBaselineStrategy:
    """Deterministic lossy compactor used only to test the experiment pipeline."""

    name = "baseline"

    def compact(self, items: tuple[MemoryItem, ...], round_number: int) -> StrategySnapshot:
        keep_count = max(1, len(items) - (round_number * 3))
        return StrategySnapshot(active_items=items[-keep_count:])


class FakeTriageStrategy:
    name = "triage"

    def compact(self, items: tuple[MemoryItem, ...], round_number: int) -> StrategySnapshot:
        pinned = tuple(
            item
            for item in items
            if item.retention_policy is RetentionPolicy.PIN
            or item.type is MemoryType.CONSTRAINT
            or (item.type is MemoryType.DECISION and item.criticality is Criticality.CRITICAL)
        )
        retrievable = tuple(
            item for item in items if item.retention_policy is RetentionPolicy.RETRIEVE
        )
        compactable = tuple(
            item for item in items if item not in pinned and item not in retrievable
        )
        drop_count = min(len(compactable), round_number * 2)
        active_compacted = compactable[drop_count:]
        return StrategySnapshot(
            active_items=(*pinned, *active_compacted), retrievable_items=retrievable
        )
