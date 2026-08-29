# Memory Triage Lab

An independent Python PoC for comparing conventional monolithic memory compaction with typed memory and differentiated retention policies.

The project supports both a deterministic offline run and a real five-round experiment against a local OpenAI-compatible vLLM server.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
memory-triage run --offline
pytest
```

Results are written to a timestamped directory under `results/` unless `--output` is supplied.

## What the offline run demonstrates

- Both strategies receive independent copies of the same 40-item dataset.
- The baseline fake compactor applies deterministic lossy compaction.
- Triage pins constraints and critical decisions, compacts episodic content, and keeps retrievable knowledge intact.
- Every round reports recall by memory type, weighted recall, and lost item IDs.

The fake compactor is a software-test instrument, not evidence about real LLM behavior. Use the vLLM mode to obtain experimental evidence from the configured local model.

## Run the real vLLM experiment

Start vLLM and verify the application-level connection:

```powershell
uv run memory-triage health
```

Then run both real strategies for five rounds:

```powershell
uv run memory-triage run --rounds 5
```

The baseline sends the LLM a monolithic list containing only IDs and text. Typed triage applies
the lifecycle policies first: `PIN` items remain verbatim in active context, `RETRIEVE` items move
to the retrievable tier, and only `COMPACT` items are sent to the LLM. Reports include recall by
memory type, weighted recall, token usage, latency, ambiguous items, and lost IDs for every round.

Use `--offline` when you only want to validate the pipeline without a GPU:

```powershell
uv run memory-triage run --offline --rounds 5
```

Detailed design and protocol documents are available in [`docs/`](docs/README.md).

## Local vLLM reference profile

The repository includes a Docker profile derived from a previously validated RTX 3060 12 GB setup:

```powershell
Copy-Item .env.example .env
docker compose up -d vllm
./scripts/check-vllm.ps1
```

See [`docs/07-vllm-docker-reference-profile.md`](docs/07-vllm-docker-reference-profile.md) before starting the model. The model catalog, structured JSON response, and Python application adapter have been validated with `qwen3-8b-awq`. The first real multi-round result remains to be recorded.
