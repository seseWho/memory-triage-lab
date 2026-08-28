from __future__ import annotations

import hashlib
import json
from pathlib import Path

from memory_triage.domain import MemoryItem


def load_dataset(path: Path) -> tuple[MemoryItem, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Dataset root must be a JSON list")
    items = tuple(MemoryItem.from_dict(entry) for entry in raw)
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Dataset contains duplicate memory item IDs")
    if not 30 <= len(items) <= 50:
        raise ValueError("Dataset must contain between 30 and 50 items")
    return items


def dataset_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
