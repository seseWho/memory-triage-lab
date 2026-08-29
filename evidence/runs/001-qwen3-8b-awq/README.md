# Run 001 — qwen3-8b-awq

## Status

Initial real vLLM evidence. The generated Markdown summary is preserved unchanged. The detailed
`results.json` was not supplied with this evidence bundle, so item-level inspection, dataset hash
verification, and confirmation of all effective settings remain pending.

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

### 1. Triage preserved all automatically verifiable information

Triage reported `recall=1.000`, `weighted_recall=1.000`, no ambiguous IDs, and no lost IDs in all
five rounds. This supports the architectural claim that deterministic lifecycle policies protect
critical memory from repeated LLM transformation.

### 2. Baseline degraded 17 items without deleting their IDs

Baseline reported `recall=0.575`, which corresponds to 23 automatic passes on the 40-item dataset.
The remaining 17 IDs were ambiguous and none were lost. The lower weighted recall (`0.530`) suggests
that higher-value information was affected slightly more than ordinary information.

This is a lexical result. The missing `results.json` prevents manual classification of the 17
ambiguous items as genuine semantic losses or acceptable paraphrases.

### 3. Triage used fewer tokens and less time

| Total over five rounds | Baseline | Triage | Triage reduction |
|---|---:|---:|---:|
| Prompt + completion tokens | 8,251 | 5,134 | 37.8% |
| Latency | 95.97 s | 60.55 s | 36.9% |

In this run, the better preservation score did not require higher inference cost.

### 4. The run did not show a cumulative compaction cliff

Baseline reached the same `0.575` recall in round 1 and retained it through round 5. Completion size
also remained at 781 tokens. The model appears to have reached a stable representation after the
first compaction rather than losing more information on every round.

## Run-level conclusion

This execution provides initial evidence that typed triage can protect lexically verifiable memory
while reducing inference cost. It also demonstrates immediate baseline degradation. It does not
yet demonstrate progressive multi-round degradation, and it is not sufficient for a global claim.

## Required follow-up

1. Add the generated `results.json` and manually review all 17 ambiguous baseline items.
2. Repeat the same configuration to assess determinism and reproducibility.
3. Add controlled compaction pressure without changing multiple variables at once.
4. Compare results across budgets, repetitions, and—later—additional models.

See [`docs/08-metrics-and-reporting.md`](../../../docs/08-metrics-and-reporting.md) for metric
definitions and interpretation rules.

