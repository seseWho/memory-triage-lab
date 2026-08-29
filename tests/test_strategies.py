import json
from pathlib import Path

import pytest

from memory_triage.dataset import load_dataset
from memory_triage.domain import MemoryType
from memory_triage.llm import CompletionResult
from memory_triage.strategies import (
    FakeBaselineStrategy,
    FakeTriageStrategy,
    LLMBaselineStrategy,
    LLMTriageStrategy,
)

DATASET = Path(__file__).parents[1] / "data" / "memory_items.json"


class StubClient:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[tuple[str, str]] = []

    def complete_json(self, system_prompt: str, user_prompt: str) -> CompletionResult:
        self.calls.append((system_prompt, user_prompt))
        return CompletionResult(self.content, "test-model", 10, 5)


def test_triage_preserves_all_constraints_after_five_rounds() -> None:
    original = load_dataset(DATASET)
    state = original
    strategy = FakeTriageStrategy()
    for round_number in range(1, 6):
        state = strategy.compact(state, round_number).all_items
    expected = {item.id for item in original if item.type is MemoryType.CONSTRAINT}
    assert expected <= {item.id for item in state}


def test_baseline_is_deterministic_and_lossy() -> None:
    items = load_dataset(DATASET)
    strategy = FakeBaselineStrategy()
    first = strategy.compact(items, 1)
    second = strategy.compact(items, 1)
    assert first == second
    assert len(first.active_items) < len(items)


def test_llm_baseline_rebuilds_items_and_records_usage() -> None:
    items = load_dataset(DATASET)[:2]
    client = StubClient('{"items":[{"id":"C01","text":"Never execute destructive actions"}]}')
    snapshot = LLMBaselineStrategy(client).compact(items, 1)
    assert [item.id for item in snapshot.active_items] == ["C01"]
    assert snapshot.active_items[0].type is items[0].type
    assert snapshot.prompt_tokens == 10
    assert snapshot.completion_tokens == 5
    request = client.calls[0][1]
    assert '"type"' not in request


def test_llm_triage_never_sends_pinned_or_retrievable_items() -> None:
    items = load_dataset(DATASET)
    compactable = [item for item in items if item.retention_policy.value == "compact"]
    response = {"items": [{"id": item.id, "text": item.text} for item in compactable]}
    client = StubClient(json.dumps(response))
    snapshot = LLMTriageStrategy(client).compact(items, 1)
    sent_ids = {entry["id"] for entry in json.loads(client.calls[0][1])["items"]}
    protected_ids = {
        item.id for item in items if item.retention_policy.value in {"pin", "retrieve"}
    }
    assert sent_ids.isdisjoint(protected_ids)
    assert protected_ids <= {item.id for item in snapshot.all_items}


def test_llm_strategy_rejects_unknown_ids() -> None:
    items = load_dataset(DATASET)[:2]
    client = StubClient('{"items":[{"id":"UNKNOWN","text":"invented"}]}')
    with pytest.raises(ValueError, match="unknown memory ID"):
        LLMBaselineStrategy(client).compact(items, 1)
