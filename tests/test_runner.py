from pathlib import Path

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
