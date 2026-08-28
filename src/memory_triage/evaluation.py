from __future__ import annotations

from dataclasses import dataclass

from memory_triage.domain import Criticality, MemoryItem, MemoryType, StrategySnapshot


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    recall: float
    weighted_recall: float
    recall_by_type: dict[str, float]
    recovered_ids: tuple[str, ...]
    lost_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "recall": self.recall,
            "weighted_recall": self.weighted_recall,
            "recall_by_type": self.recall_by_type,
            "recovered_ids": list(self.recovered_ids),
            "lost_ids": list(self.lost_ids),
        }


def item_weight(item: MemoryItem) -> int:
    if item.type is MemoryType.CONSTRAINT and item.criticality is Criticality.CRITICAL:
        return 5
    if item.type is MemoryType.DECISION and item.criticality is Criticality.CRITICAL:
        return 4
    if item.type is MemoryType.CONSTRAINT:
        return 3
    if item.type is MemoryType.EVIDENCE:
        return 2
    return 1


def evaluate(original: tuple[MemoryItem, ...], snapshot: StrategySnapshot) -> EvaluationResult:
    available = {item.id: item for item in snapshot.all_items}
    recovered = tuple(item.id for item in original if item.id in available)
    lost = tuple(item.id for item in original if item.id not in available)
    recall_by_type: dict[str, float] = {}
    for memory_type in MemoryType:
        expected = [item for item in original if item.type is memory_type]
        found = [item for item in expected if item.id in available]
        recall_by_type[memory_type.value] = len(found) / len(expected) if expected else 1.0
    total_weight = sum(item_weight(item) for item in original)
    recovered_weight = sum(item_weight(item) for item in original if item.id in available)
    return EvaluationResult(
        recall=len(recovered) / len(original),
        weighted_recall=recovered_weight / total_weight,
        recall_by_type=recall_by_type,
        recovered_ids=recovered,
        lost_ids=lost,
    )
