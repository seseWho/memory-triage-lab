# Implementation Plan

## 1. Proposed Structure

```text
compaction-cliff-poc/
├── pyproject.toml
├── requirements-vllm.txt
├── .env.example
├── data/memory_items.json
├── src/memory_triage/
│   ├── cli.py
│   ├── domain.py
│   ├── runner.py
│   ├── evaluation.py
│   ├── reporting.py
│   ├── strategies/baseline.py
│   ├── strategies/triage.py
│   └── llm/{port.py,http_client.py,fake.py}
├── tests/
│   ├── unit/
│   └── integration/
└── results/.gitkeep
```

## 2. Execution Flow

```bash
uv run memory-triage run \
  --dataset data/memory_items.json \
  --rounds 5 \
  --strategies baseline triage \
  --target-words 700 \
  --output results/run-001
```

The server is started separately:

```bash
vllm serve Qwen/Qwen3-4B-Instruct-2507 \
  --host 127.0.0.1 \
  --port 8000 \
  --served-model-name memory-cliff-model \
  --generation-config vllm
```

The model is an initial proposal and must be adjusted to the available GPU. The served name, not the repository identifier, will be the value of `LLM_MODEL`.

The following must also work:

```bash
uv run memory-triage run --offline
uv run pytest
```

## 3. Ordered Backlog

### 1. Domain, Dataset, and Deterministic Evaluator

This is the first priority because it defines what "remembering" means and allows everything to be tested without a network. Without a stable measure, any LLM result would be anecdotal.

**Final consideration:** manually review the `check_terms`; they are part of the measurement instrument.

### 2. Runner and Fake Compactor

This closes a reproducible end-to-end path before introducing external variability.

**Final consideration:** the fake should remove items predictably, not simulate intelligence.

### 3. LLM Baseline

Implement monolithic compaction with a JSON contract and fixed budget.

**Final consideration:** save the prompt and raw response for each round to diagnose losses.

### 4. Knowledge Triage Strategy

Classify, pin constraints, compact episodes, and retrieve knowledge by metadata/terms.

**Final consideration:** the initial classification will be declared in the dataset; automatic classification would be another experiment.

### 5. Reports and Repetitions

Add per-round comparison, aggregates, and auditable artifacts.

**Final consideration:** prioritize JSON and Markdown; a dashboard does not add value yet.

### 6. Optional Extensions

Third arm with a reinforced prompt, LLM judge, embeddings, and UI.

**Final consideration:** add them only after obtaining a clear baseline.

## 4. Rough Estimate

| Block | Approximate effort |
|---|---:|
| Domain + dataset + evaluation | 2–3 h |
| Runner + fake | 1–2 h |
| Baseline + client adapter | 2 h |
| Triage | 2–3 h |
| Reports + execution documentation | 1–2 h |

Estimated total: 8–12 hours for a clean PoC.

## 5. Configuration

```dotenv
LLM_API_KEY=
LLM_BASE_URL=http://127.0.0.1:8000/v1
LLM_MODEL=memory-cliff-model
LLM_TIMEOUT_SECONDS=60
LLM_MAX_TOKENS=1200
```

Never include a real `.env` file in version control.

With local vLLM, `LLM_API_KEY` can be set to a non-secret value such as `local` if the client requires a string.

## 6. Definition of Done

- Offline tests pass.
- Complete real execution with five rounds for both strategies.
- Dataset and configuration are identifiable by hash.
- Results contain losses by ID and recall by type.
- No pinned constraint is modified in triage.
- README includes the exact command and observed limitations.
