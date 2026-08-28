from memory_triage.domain import (
    Criticality,
    MemoryItem,
    MemoryType,
    RetentionPolicy,
    StrategySnapshot,
)
from memory_triage.evaluation import evaluate


def item(item_id: str, memory_type: MemoryType) -> MemoryItem:
    return MemoryItem(
        id=item_id,
        type=memory_type,
        text="canonical fact",
        criticality=Criticality.CRITICAL,
        scope="test",
        provenance="test",
        retention_policy=RetentionPolicy.PIN,
        check_terms=("canonical",),
    )


def test_evaluation_reports_lost_ids_and_weighted_recall() -> None:
    constraint = item("C01", MemoryType.CONSTRAINT)
    episode = item("E01", MemoryType.EPISODE)
    result = evaluate((constraint, episode), StrategySnapshot((constraint,)))
    assert result.recall == 0.5
    assert result.weighted_recall == 5 / 6
    assert result.lost_ids == ("E01",)


def test_matching_id_with_missing_check_term_is_ambiguous() -> None:
    expected = item("C01", MemoryType.CONSTRAINT)
    changed = MemoryItem(
        id=expected.id,
        type=expected.type,
        text="meaning was removed",
        criticality=expected.criticality,
        scope=expected.scope,
        provenance=expected.provenance,
        retention_policy=expected.retention_policy,
        check_terms=expected.check_terms,
    )
    result = evaluate((expected,), StrategySnapshot((changed,)))
    assert result.recall == 0
    assert result.ambiguous_ids == ("C01",)
    assert result.lost_ids == ()
