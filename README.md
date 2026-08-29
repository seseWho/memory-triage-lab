# Memory Triage Lab

An independent Python PoC for comparing conventional monolithic memory compaction with typed memory and differentiated retention policies.

The first increment is intentionally offline and deterministic. It validates the domain model, the two strategies, metrics, reporting, and a complete five-round run without requiring a GPU or vLLM.

## Quick start

This project uses [uv](https://docs.astral.sh/uv/) to create the virtual environment and manage dependencies. You do not need to activate the environment manually.

Install uv if it is not already available:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

On Linux or macOS, use:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

From the repository root, sync the application and development dependencies:

```bash
uv sync --extra dev
uv run memory-triage run --offline
uv run pytest
```

Use `uv run <command>` for project commands. It runs them in the project's managed environment, so activation is optional.

Results are written to a timestamped directory under `results/` unless `--output` is supplied.

## What the offline run demonstrates

- Both strategies receive independent copies of the same 40-item dataset.
- The baseline fake compactor applies deterministic lossy compaction.
- Triage pins constraints and critical decisions, compacts episodic content, and keeps retrievable knowledge intact.
- Every round reports recall by memory type, weighted recall, and lost item IDs.

The fake compactor is a software-test instrument, not evidence about real LLM behavior. The next increment will add the vLLM adapter and real experimental prompts.

Detailed design and protocol documents are available in [`docs/`](docs/README.md).

## Local vLLM reference profile

The repository includes a Docker profile derived from a previously validated RTX 3060 12 GB setup:

```powershell
Copy-Item .env.example .env
docker compose up -d vllm
./scripts/check-vllm.ps1
```

See [`docs/07-vllm-docker-reference-profile.md`](docs/07-vllm-docker-reference-profile.md) before starting the model. The profile is not considered validated for this PoC until its smoke test is run and recorded here.
