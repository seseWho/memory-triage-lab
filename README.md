# Memory Triage Lab

An independent Python PoC for comparing conventional monolithic memory compaction with typed memory and differentiated retention policies.

The first increment is intentionally offline and deterministic. It validates the domain model, the two strategies, metrics, reporting, and a complete five-round run without requiring a GPU or vLLM.

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

The fake compactor is a software-test instrument, not evidence about real LLM behavior. The next increment will add the vLLM adapter and real experimental prompts.

Detailed design and protocol documents are available in [`docs/`](docs/README.md).

