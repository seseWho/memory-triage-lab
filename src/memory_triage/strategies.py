from __future__ import annotations

import json
from time import monotonic
from typing import Protocol

from memory_triage.domain import (
    Criticality,
    MemoryItem,
    MemoryType,
    RetentionPolicy,
    StrategySnapshot,
)
from memory_triage.llm import CompletionResult


class MemoryStrategy(Protocol):
    name: str

    def compact(self, items: tuple[MemoryItem, ...], round_number: int) -> StrategySnapshot: ...


class CompletionClient(Protocol):
    def complete_json(self, system_prompt: str, user_prompt: str) -> CompletionResult: ...


BASELINE_SYSTEM_PROMPT = """You compact an agent's monolithic memory.
Return one JSON object with an 'items' array. Every item must contain exactly an existing 'id'
and a concise 'text'. You may merge detail into shorter wording or omit low-value items, but never
invent IDs. Preserve information you judge important. Do not use markdown."""

TRIAGE_SYSTEM_PROMPT = """You compact the COMPACT tier of a typed agent memory.
Return one JSON object with an 'items' array. Every item must contain exactly an existing 'id'
and a concise 'text'. Preserve decisions and high-criticality information when possible. You may
omit low-value episodic detail, but never invent IDs. Do not use markdown."""


class LLMBaselineStrategy:
    name = "baseline"

    def __init__(self, client: CompletionClient) -> None:
        self._client = client

    def compact(self, items: tuple[MemoryItem, ...], round_number: int) -> StrategySnapshot:
        return _compact_with_llm(
            self._client,
            items,
            BASELINE_SYSTEM_PROMPT,
            round_number,
        )


class LLMTriageStrategy:
    name = "triage"

    def __init__(self, client: CompletionClient) -> None:
        self._client = client

    def compact(self, items: tuple[MemoryItem, ...], round_number: int) -> StrategySnapshot:
        pinned = tuple(item for item in items if item.retention_policy is RetentionPolicy.PIN)
        retrievable = tuple(
            item for item in items if item.retention_policy is RetentionPolicy.RETRIEVE
        )
        compactable = tuple(
            item for item in items if item not in pinned and item not in retrievable
        )
        compacted = _compact_with_llm(
            self._client,
            compactable,
            TRIAGE_SYSTEM_PROMPT,
            round_number,
        )
        return StrategySnapshot(
            active_items=(*pinned, *compacted.active_items),
            retrievable_items=retrievable,
            model=compacted.model,
            prompt_tokens=compacted.prompt_tokens,
            completion_tokens=compacted.completion_tokens,
            latency_seconds=compacted.latency_seconds,
        )


def _compact_with_llm(
    client: CompletionClient,
    items: tuple[MemoryItem, ...],
    system_prompt: str,
    round_number: int,
) -> StrategySnapshot:
    payload = {
        "round": round_number,
        "items": [{"id": item.id, "text": item.text} for item in items],
    }
    started = monotonic()
    completion = client.complete_json(system_prompt, json.dumps(payload, ensure_ascii=False))
    latency = monotonic() - started
    active_items = _parse_compacted_items(completion.content, items)
    return StrategySnapshot(
        active_items=active_items,
        model=completion.model,
        prompt_tokens=completion.prompt_tokens,
        completion_tokens=completion.completion_tokens,
        latency_seconds=latency,
    )


def _parse_compacted_items(
    content: str, source_items: tuple[MemoryItem, ...]
) -> tuple[MemoryItem, ...]:
    decoded = json.loads(content)
    raw_items = decoded.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("LLM compaction response requires an items array")
    source_by_id = {item.id: item for item in source_items}
    seen: set[str] = set()
    result: list[MemoryItem] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            raise ValueError("Each compacted item must be an object")
        item_id = raw_item.get("id")
        text = raw_item.get("text")
        if not isinstance(item_id, str) or item_id not in source_by_id:
            raise ValueError(f"LLM returned unknown memory ID: {item_id!r}")
        if item_id in seen:
            raise ValueError(f"LLM returned duplicate memory ID: {item_id}")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"LLM returned empty text for memory ID: {item_id}")
        original = source_by_id[item_id]
        result.append(
            MemoryItem(
                id=original.id,
                type=original.type,
                text=text.strip(),
                criticality=original.criticality,
                scope=original.scope,
                provenance=original.provenance,
                retention_policy=original.retention_policy,
                check_terms=original.check_terms,
            )
        )
        seen.add(item_id)
    return tuple(result)


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
