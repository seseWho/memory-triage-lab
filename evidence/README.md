# Experimental Evidence

This directory stores reproducible evidence separately from implementation code and global
conclusions.

Each run uses a numbered directory:

```text
evidence/runs/<sequence>-<model>/
├── README.md       # Context, interpretation, and limitations
├── summary.md      # Unmodified generated Markdown summary
└── results.json    # Detailed generated result, when available
```

## Evidence levels

1. **Raw evidence**: generated `summary.md` and `results.json`.
2. **Run conclusion**: interpretation limited to that execution.
3. **Global conclusion**: cross-run analysis produced only after the execution matrix is complete.

Run conclusions must identify the model, dataset hash, number of rounds, configuration, and any
missing artifacts. An incomplete evidence bundle remains useful but must be marked as incomplete.

Metric definitions are maintained in
[`docs/08-metrics-and-reporting.md`](../docs/08-metrics-and-reporting.md).

## Recorded runs

| Run | Model | Rounds | Status | Main observation |
|---|---|---:|---|---|
| [001](runs/001-qwen3-8b-awq/README.md) | `qwen3-8b-awq` | 5 | Exploratory, partial bundle | Application path validated; methodological controls require correction before comparison |
