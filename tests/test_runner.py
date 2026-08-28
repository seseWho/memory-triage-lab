from pathlib import Path

from memory_triage.cli import main


def test_offline_run_writes_reports(tmp_path: Path) -> None:
    result = main(["run", "--offline", "--rounds", "5", "--output", str(tmp_path)])
    assert result == 0
    assert (tmp_path / "results.json").is_file()
    assert (tmp_path / "summary.md").is_file()
