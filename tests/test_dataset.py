from pathlib import Path

from memory_triage.dataset import load_dataset

DATASET = Path(__file__).parents[1] / "data" / "memory_items.json"


def test_dataset_has_40_unique_items() -> None:
    items = load_dataset(DATASET)
    assert len(items) == 40
    assert len({item.id for item in items}) == 40
