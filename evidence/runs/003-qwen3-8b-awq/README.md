# Run 003 — qwen3-8b-awq

Run 003 was executed on 29 August 2026 after the explicit retrieval accounting change. It uses the
40-item synthetic dataset, five rounds, temperature `0.0`, seed `0`, and `max_tokens=4096`.

Artifacts:

- [`summary.md`](summary.md): generated Markdown summary.
- [`results.json`](results.json): generated results with per-round settings and tier traces.

## Run-level conclusion

The result is stable across all five rounds:

| Strategy | Recall | Weighted recall | Active | Retrieved | Ambiguous | Lost |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 0.575 | 0.530 | 40 | 0 | 17 | 0 |
| Triage | 1.000 | 1.000 | 32 | 8 | 0 | 0 |

The new trace confirms that triage's eight `RETRIEVE` items are explicitly returned and scored;
they are no longer credited merely because they are stored outside active context. Triage also uses
about 36% fewer prompt tokens and about 36% lower latency in this run.

This is still a PoC result, not a global conclusion. The retrieval oracle requests every item in the
`RETRIEVE` tier rather than answering a task query, and the active-context budgets are not equal.
The baseline's 17 ambiguous items should be interpreted together with the manual audit from Run 002.
