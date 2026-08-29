# Metrics and Reporting Guide

This document defines every field used by Memory Triage Lab reports. The definitions are part of
the experimental contract: results from different runs should not be compared if their evaluator
or metric definitions have changed without being explicitly versioned.

## Preservation rule

Every original memory item has a stable ID and one or more `check_terms`. An item is automatically
recovered only when:

1. the same ID exists in the strategy snapshot; and
2. every normalized `check_term` occurs in the resulting text.

Normalization lowercases the text, extracts word characters, and collapses whitespace. The
evaluator is deterministic and lexical; it does not ask another LLM to judge semantic equivalence.

## Core preservation metrics

### `recall`

The fraction of all original items automatically recovered:

\[
Recall = \frac{|recovered\_ids|}{|original\ items|}
\]

A value of `1.0` means every item passed the ID and `check_terms` rule. A value of `0.575` on the
40-item dataset means 23 items passed it.

### `weighted_recall`

Recall adjusted so that losing critical information matters more than losing ordinary history:

\[
WeightedRecall =
\frac{\sum_i weight_i \cdot recovered_i}{\sum_i weight_i}
\]

Current weights are:

| Memory item | Weight |
|---|---:|
| Critical constraint | 5 |
| Critical decision | 4 |
| Other constraint | 3 |
| Evidence | 2 |
| Everything else | 1 |

When `weighted_recall` is lower than ordinary `recall`, the failures disproportionately affect
higher-value memories.

### `recall_by_type`

Recall calculated independently for each memory type: `constraint`, `decision`, `evidence`,
`episode`, and `preference`. It reveals which classes are most vulnerable even when overall recall
looks acceptable.

### `recovered_ids`

IDs that exist after compaction and retain all expected `check_terms`. These are automatic passes,
not proof that every nuance of the original text remains.

### `ambiguous_ids` / `ambiguous`

IDs that still exist but whose text is missing at least one expected `check_term`. `ambiguous` in
the Markdown summary is the number of entries in `ambiguous_ids`.

Ambiguous does **not** automatically mean forgotten. It may indicate:

- genuine loss or weakening of an essential detail;
- a negation or obligation that disappeared;
- a valid paraphrase using synonyms that the lexical evaluator cannot recognize.

Every ambiguous item should therefore be inspected manually before being classified as a semantic
failure.

### `lost_ids` / `lost`

Original IDs that no longer exist in either active or retrievable memory. `lost` in the Markdown
summary is the number of entries in `lost_ids`. Unlike an ambiguous item, a lost item cannot be
recovered by ID from the produced snapshot.

## Memory placement metrics

### `active_item_count`

Number of items placed directly in active context after the round.

### `retrievable_item_count`

Number of items kept outside active context in the retrievable tier. The current PoC counts these
items as available to the evaluator; it does not yet measure retrieval ranking or query quality.

## Cost and performance metrics

### `prompt_tokens`

Input tokens reported by vLLM for that strategy and round. This includes instructions and the
memory payload sent to the model.

### `completion_tokens`

Output tokens reported by vLLM for that strategy and round.

### `latency_seconds`

Wall-clock time spent obtaining and parsing that compaction completion. It is affected by the
model, GPU, server load, prompt size, generation length, and local environment.

### `model`

Model identifier returned by the OpenAI-compatible endpoint.

## Run metadata

### `mode`

- `offline`: deterministic fake strategies validate the pipeline but provide no LLM evidence.
- `vllm`: real prompts are executed against the configured local vLLM endpoint.

### `run_id`

Unique UTC timestamp-based identifier used to separate report directories.

### `dataset_hash`

SHA-256 of the dataset file. Matching hashes demonstrate that runs used identical source data.

## Interpretation rules

1. Never equate `ambiguous` with confirmed memory loss without inspecting the detailed text.
2. Report weighted recall alongside ordinary recall.
3. Compare token cost and latency alongside preservation quality.
4. A triage score of 100% demonstrates the retention policy, not perfect end-to-end memory.
5. A flat score across rounds indicates a stable compaction fixed point, not a cumulative cliff.
6. API, parsing, or transport failures must be reported separately and never counted as memory loss.
7. Treat one run as initial evidence; use repeated runs for global conclusions.

