from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_reports(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = ["# Memory Triage Offline Run", ""]
    for round_result in result["rounds"]:
        lines.extend((f"## Round {round_result['round']}", ""))
        for name, metrics in round_result["strategies"].items():
            lines.append(
                f"- **{name}**: recall={metrics['recall']:.3f}, "
                f"weighted_recall={metrics['weighted_recall']:.3f}, "
                f"lost={len(metrics['lost_ids'])}"
            )
        lines.append("")
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
