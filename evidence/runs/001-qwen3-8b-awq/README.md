# Run 001 — qwen3-8b-awq

## Status

Exploratory real vLLM evidence. The generated Markdown summary is preserved unchanged. This run
validates the application path but is not a controlled comparison. The detailed `results.json` was
not supplied with this evidence bundle, so item-level inspection, dataset hash verification, and
confirmation of all effective settings remain pending.

## Known configuration

| Field | Value |
|---|---|
| Mode | `vllm` |
| Model | `qwen3-8b-awq` |
| Strategies | Monolithic baseline and typed triage |
| Rounds | 5 |
| Dataset size | 40 memory items |
| Generated artifact | [`summary.md`](summary.md) |
| Detailed artifact | `results.json` pending |

## Observations

### 1. Triage reported all automatically verifiable information as available

Triage reported `recall=1.000`, `weighted_recall=1.000`, no ambiguous IDs, and no lost IDs in all
five rounds. Pinned items are protected from LLM transformation. However, the current evaluator
also credits every item in the `RETRIEVE` tier without executing a retrieval query, so this score
must not be interpreted as measured retrieval effectiveness.

### 2. Baseline degraded 17 items without deleting their IDs

Baseline reported `recall=0.575`, which corresponds to 23 automatic passes on the 40-item dataset.
The remaining 17 IDs were ambiguous and none were lost. The lower weighted recall (`0.530`) suggests
that higher-value information was affected slightly more than ordinary information.

This is a lexical result. The missing `results.json` prevents manual classification of the 17
ambiguous items as genuine semantic losses or acceptable paraphrases.

### 3. Triage used fewer LLM tokens and less inference time

| Total over five rounds | Baseline | Triage | Triage reduction |
|---|---:|---:|---:|
| Prompt + completion tokens | 8,251 | 5,134 | 37.8% |
| Latency | 95.97 s | 60.55 s | 36.9% |

This measures only the LLM calls. The two arms do not yet enforce an equal final active-context
budget: triage appends pinned items outside the generation ceiling. Token and latency reductions
are useful operational observations but are not yet a fair quality-versus-budget comparison.

### 4. The run did not show a cumulative compaction cliff

Baseline reached the same `0.575` recall in round 1 and retained it through round 5. Completion size
also remained at 781 tokens. The model appears to have reached a stable representation after the
first compaction rather than losing more information on every round.

## Run-level conclusion

This execution validates the real vLLM integration, five-round orchestration, report generation,
and deterministic protection of pinned items. It observes immediate lexical degradation in the
baseline and a stable representation thereafter. Because retrieval is credited without querying,
the active-context budgets are unequal, generation settings are not fully recorded, and detailed
item traces are absent, this run does not establish comparative superiority or a global claim.

## Required follow-up

1. Persist generated item text and every effective generation setting in `results.json`.
2. Add explicit retrieval queries and score only retrieved items.
3. Enforce the same total active-context budget after pinned items are included.
4. Manually review all 17 ambiguous baseline items.
5. Repeat the corrected configuration before varying compaction pressure or model.

See [`docs/08-metrics-and-reporting.md`](../../../docs/08-metrics-and-reporting.md) for metric
definitions and interpretation rules.
