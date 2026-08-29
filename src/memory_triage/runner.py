from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from memory_triage.domain import MemoryItem
from memory_triage.evaluation import evaluate
from memory_triage.strategies import MemoryStrategy


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    rounds: int = 5
    mode: str = "offline"
    model: str | None = None
    temperature: float | None = None
    seed: int | None = None
    max_tokens: int | None = None

    def __post_init__(self) -> None:
        if self.rounds < 1:
            raise ValueError("rounds must be at least 1")


def run_experiment(
    items: tuple[MemoryItem, ...],
    strategies: tuple[MemoryStrategy, ...],
    config: ExperimentConfig,
) -> dict[str, Any]:
    states = {strategy.name: tuple(items) for strategy in strategies}
    rounds: list[dict[str, Any]] = []
    for round_number in range(1, config.rounds + 1):
        strategy_results: dict[str, Any] = {}
        for strategy in strategies:
            snapshot = strategy.compact(states[strategy.name], round_number)
            states[strategy.name] = snapshot.all_items
            strategy_results[strategy.name] = {
                **evaluate(items, snapshot).as_dict(),
                "active_item_count": len(snapshot.active_items),
                "retrievable_item_count": len(snapshot.retrievable_items),
                "model": snapshot.model,
                "prompt_tokens": snapshot.prompt_tokens,
                "completion_tokens": snapshot.completion_tokens,
                "latency_seconds": snapshot.latency_seconds,
                "active_items": [
                    {"id": item.id, "text": item.text} for item in snapshot.active_items
                ],
                "retrievable_items": [
                    {"id": item.id, "text": item.text} for item in snapshot.retrievable_items
                ],
            }
        rounds.append({"round": round_number, "strategies": strategy_results})
    return {
        "run_id": datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ"),
        "mode": config.mode,
        "settings": {
            "rounds": config.rounds,
            "model": config.model,
            "temperature": config.temperature,
            "seed": config.seed,
            "max_tokens": config.max_tokens,
        },
        "rounds": rounds,
    }
