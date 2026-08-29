from __future__ import annotations

import argparse
from importlib.resources import files
from pathlib import Path

from memory_triage.dataset import dataset_hash, load_dataset
from memory_triage.llm import LLMError, OpenAICompatibleClient
from memory_triage.reporting import write_reports
from memory_triage.runner import ExperimentConfig, run_experiment
from memory_triage.settings import LLMSettings
from memory_triage.strategies import FakeBaselineStrategy, FakeTriageStrategy


def default_dataset() -> Path:
    return Path(str(files("memory_triage").joinpath("data/memory_items.json")))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-triage")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="Run the memory experiment")
    run.add_argument("--offline", action="store_true", help="Use deterministic fake strategies")
    run.add_argument("--rounds", type=int, default=5)
    run.add_argument("--dataset", type=Path, default=default_dataset())
    run.add_argument("--output", type=Path)
    subparsers.add_parser("health", help="Validate the configured local vLLM server")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "health":
        settings = LLMSettings.from_env()
        try:
            models = OpenAICompatibleClient(settings).health()
        except LLMError as error:
            print(f"vLLM health check failed: {error}")
            return 1
        print(f"vLLM ready: model={settings.model}; available={','.join(models)}")
        return 0
    if args.command == "run" and not args.offline:
        raise SystemExit("Only --offline is implemented in this increment")
    items = load_dataset(args.dataset)
    result = run_experiment(
        items,
        (FakeBaselineStrategy(), FakeTriageStrategy()),
        ExperimentConfig(rounds=args.rounds),
    )
    result["dataset_hash"] = dataset_hash(args.dataset)
    output = args.output or Path("results") / result["run_id"]
    write_reports(result, output)
    print(f"Completed {args.rounds} rounds. Reports: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
