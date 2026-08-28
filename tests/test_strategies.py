from pathlib import Path

from memory_triage.dataset import load_dataset
from memory_triage.domain import MemoryType
from memory_triage.strategies import FakeBaselineStrategy, FakeTriageStrategy

DATASET = Path(__file__).parents[1] / "data" / "memory_items.json"


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
