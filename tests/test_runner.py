from pathlib import Path

import pytest

from memory_triage.cli import main
from memory_triage.dataset import load_dataset
from memory_triage.runner import ExperimentConfig, run_experiment
from memory_triage.strategies import FakeBaselineStrategy


def test_offline_run_writes_reports(tmp_path: Path) -> None:
    result = main(["run", "--offline", "--rounds", "5", "--output", str(tmp_path)])
    assert result == 0
    assert (tmp_path / "results.json").is_file()
    assert (tmp_path / "summary.md").is_file()


def test_generated_run_ids_are_collision_safe() -> None:
    from memory_triage.cli import default_dataset

    items = load_dataset(default_dataset())
    config = ExperimentConfig(rounds=1)
    first = run_experiment(items, (FakeBaselineStrategy(),), config)
    second = run_experiment(items, (FakeBaselineStrategy(),), config)
    assert first["run_id"] != second["run_id"]


def test_run_persists_auditable_item_text_and_settings() -> None:
    from memory_triage.cli import default_dataset

    items = load_dataset(default_dataset())
    config = ExperimentConfig(
        rounds=1,
        mode="vllm",
        model="test-model",
        temperature=0.25,
        seed=42,
        max_tokens=512,
    )
    result = run_experiment(items, (FakeBaselineStrategy(),), config)
    baseline = result["rounds"][0]["strategies"]["baseline"]
    first_item = baseline["active_items"][0]
    assert set(first_item) == {"id", "text"}
    assert first_item["id"]
    assert first_item["text"]
    assert baseline["retrieved_item_count"] == 0
    assert result["settings"] == {
        "rounds": 1,
        "model": "test-model",
        "temperature": 0.25,
        "seed": 42,
        "max_tokens": 512,
    }


def test_invalid_health_configuration_returns_controlled_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "invalid")
    assert main(["health"]) == 1
    assert "health check failed" in capsys.readouterr().out
