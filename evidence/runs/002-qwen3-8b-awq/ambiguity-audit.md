# Ambiguity audit — Run 002

## Scope and method

This audit compares the original 40-item dataset with the baseline texts generated in rounds 1–5.
The same 17 IDs are ambiguous in every round, so the table uses the stable final representation;
the wording is unchanged across rounds. The evaluator marked an item ambiguous when at least one
configured `check_term` was absent. The classification below is a manual semantic review, not a
replacement metric.

The result's dataset hash is `73c5e720...`. The repository's canonical JSON has a different byte
hash but the same 40 IDs, texts, types, criticalities, policies, and check terms; the discrepancy
is therefore treated as a serialization/line-ending difference and should be normalized in a future
run.

## Classification summary

| Classification | Count | IDs |
|---|---:|---|
| Probable semantic weakening | 6 | C02, C03, C07, D06, V03, V07 |
| Valid paraphrase / lexical false negative | 11 | C01, D01, D03, V04, V05, V06, V08, E01, E09, P02, P06 |
| Confirmed disappearance | 0 | — |

## Item-level review

| ID | Type | Missing terms | Original meaning | Compact text | Classification | Rationale |
|---|---|---|---|---|---|---|
| C01 | Constraint | `never`, `execute`, `destructive` | Destructive operations require explicit authorization | Require explicit authorization for destructive operations | Valid paraphrase | The prohibition is preserved as a requirement for authorization; lexical terms changed. |
| C02 | Constraint | `never`, `expose`, `secrets` | Never expose secrets or credentials in logs | Avoid logging secrets, credentials, or API keys | Probable weakening | “Avoid” is weaker than “never”, and exposure is reduced to logging. |
| C03 | Constraint | `repository` | Stop when repository write permission is unconfirmed | Stop if write permissions are not confirmed | Probable weakening | The repository scope disappears, broadening or changing the operational rule. |
| C07 | Constraint | `silently`, `weaken` | Do not silently weaken an approved safety constraint | Do not relax approved safety constraints | Probable weakening | The silent-change condition is lost and “relax” may be weaker than “weaken”. |
| D01 | Decision | `supported` | Python 3.11 is the minimum supported runtime | Minimum Python version is 3.11 | Valid paraphrase | “Minimum version” expresses the same decision in this context. |
| D03 | Decision | `application` | The application uses an OpenAI-compatible adapter | Use OpenAI-compatible adapter | Valid paraphrase | The subject is implicit in the decision statement. |
| D06 | Decision | `canonical`, `result` | JSON is the canonical result format | JSON is the standard output format | Probable weakening | “Canonical result” becomes a less precise “standard output”. |
| V03 | Evidence | `retrievable` | Triage stores retrievable evidence outside active context | Triage stores evidence outside active context | Probable weakening | The explicit retrievability/lifecycle property is omitted. |
| V04 | Evidence | `every`, `records`, `dataset` | Every run records the dataset SHA-256 hash | Record dataset SHA-256 hash for each run | Valid paraphrase | Imperative wording preserves the operational requirement. |
| V05 | Evidence | `excluded` | Transport errors are excluded from memory-loss metrics | Exclude transport errors from memory-loss metrics | Valid paraphrase | Same rule with a grammatical transformation. |
| V06 | Evidence | `every` | Recall is calculated for every memory type | Recall calculated for all memory types | Valid paraphrase | “All” is equivalent to “every” here. |
| V07 | Evidence | `weighted`, `recall`, `gives` | Weighted recall gives critical constraints weight five | Critical constraints weighted five times higher | Probable weakening | The metric name and exact weighting operation are no longer explicit; “five times higher” is also ambiguous. |
| V08 | Evidence | `round`, `outputs`, `remain` | Raw round outputs remain available for audit | Raw outputs retained for audit purposes | Valid paraphrase | Availability and audit intent remain; “round” is contextual detail. |
| E01 | Episode | `executed` | The user executed smoke test T01 yesterday | User ran smoke test T01 yesterday | Valid paraphrase | “Ran” preserves the event meaning. |
| E09 | Episode | `occurred` | A parser error occurred in a trial response | Parser error in trial response | Valid paraphrase | The noun phrase still asserts the event; “occurred” is implicit. |
| P02 | Preference | `wants` | The user wants solutions ordered by suitability | Solutions ordered by suitability | Lexical false negative | The preference content is retained, while the subject/attitude is implicit. |
| P06 | Preference | `wants` | The user wants important limitations stated explicitly | Important limitations stated explicitly | Lexical false negative | The desired behavior is retained without the explicit “wants” verb. |

## Interpretation

The 17 lexical ambiguities are not 17 confirmed memory losses. The manual audit finds six probable
semantic weakenings, concentrated in constraints and methodological decisions, and eleven likely
valid paraphrases or lexical false negatives. No item disappeared completely.

This changes the interpretation of Run 002: baseline degradation is real as a preservation-contract
failure, but the raw `recall=0.575` overstates semantic loss when read literally. The most important
risks are C02, C03, C07, D06, V03, and V07 because they remove scope, modality, or metric precision.

The audit does not make the run a controlled comparison: retrieval is still credited without an
explicit query and active-context budgets remain unequal. Those controls must be addressed before
global conclusions.

