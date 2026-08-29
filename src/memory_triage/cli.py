from __future__ import annotations

import argparse
import json
from importlib.resources import files
from os import environ
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from memory_triage.dataset import dataset_hash, load_dataset
from memory_triage.reporting import write_reports
from memory_triage.runner import ExperimentConfig, run_experiment
from memory_triage.strategies import FakeBaselineStrategy, FakeTriageStrategy


def default_dataset() -> Path:
    return Path(str(files("memory_triage").joinpath("data/memory_items.json")))


def check_health(base_url: str, timeout: float) -> int:
    endpoint = f"{base_url.rstrip('/')}/models"
    request = Request(endpoint, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"LLM health check failed: {exc}")
        return 1

    models = payload.get("data", [])
    model_ids = [model.get("id", "<unknown>") for model in models]
    print(f"LLM is healthy at {endpoint}. Models: {', '.join(model_ids) or '<none>'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-triage")
    subparsers = parser.add_subparsers(dest="command", required=True)
    health = subparsers.add_parser("health", help="Check the OpenAI-compatible LLM endpoint")
    health.add_argument(
        "--base-url",
        default=environ.get("LLM_BASE_URL", "http://127.0.0.1:8000/v1"),
    )
    health.add_argument(
        "--timeout",
        type=float,
        default=float(environ.get("LLM_TIMEOUT_SECONDS", "10")),
    )
    run = subparsers.add_parser("run", help="Run the memory experiment")
    run.add_argument("--offline", action="store_true", help="Use deterministic fake strategies")
    run.add_argument("--rounds", type=int, default=5)
    run.add_argument("--dataset", type=Path, default=default_dataset())
    run.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "health":
        return check_health(args.base_url, args.timeout)
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
