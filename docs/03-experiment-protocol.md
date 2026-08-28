# Experimental Protocol

## 1. Hypotheses

- **H1:** baseline constraint recall will decrease with successive compactions.
- **H2:** triage constraint recall will remain at 100% because constraints are pinned deterministically.
- **H3:** triage will have better weighted recall without requiring the entire history to remain in active context.

## 2. Recommended Dataset: 40 Items

| Type | Count | Example |
|---|---:|---|
| Constraints | 8 | "Do not execute destructive operations without explicit authorization" |
| Decisions | 8 | "SQLite was chosen for offline operation" |
| Evidence | 8 | "Integration test T-17 failed with a timeout" |
| Episodes | 10 | "Yesterday the user ran backtest B-04" |
| Preferences | 6 | "The user prefers clear answers before theory" |

Each item will have a stable ID (`C01`, `D01`, etc.), provenance, criticality, and one to three `check_terms`.

## 3. Compaction Pressure

Before each round, five deterministic noise episodes will be added. Each strategy must then produce active context within the same target budget. Recommended starting value: 700 words; if no loss appears, reduce to 500 and then 350.

The dataset, prompt, and budget must not be changed simultaneously during a comparison.

## 4. Procedure

1. Validate and freeze the dataset; calculate its SHA-256.
2. Create two independent copies.
3. For rounds 1 through 5:
  1. Add the same noise to both arms.
  2. Run baseline compaction.
  3. Run triage policies.
  4. Issue the same retrieval queries.
  5. Evaluate all items and save traces.
4. Repeat the experiment at least three times if the model is not deterministic.
5. Compare mean, minimum, and spread.

## 5. Preservation Evaluation

An item is considered retrieved when:

- its ID appears in the structured representation; and
- all its normalized `check_terms` appear in the retrieved text.

An `ambiguous_items` list will also be generated for manual review when the ID exists but a term is missing. This prevents turning a questionable paraphrase into a false automatic failure.

## 6. Metrics

### Recall by Type

\[
Recall_t = \frac{elementos\ recuperados\ del\ tipo\ t}{elementos\ originales\ del\ tipo\ t}
\]

### Weighted Recall

Initial weights: critical constraint = 5, critical decision = 4, normal constraint = 3, evidence = 2, and everything else = 1.

\[
WeightedRecall = \frac{\sum_i peso_i \cdot recuperado_i}{\sum_i peso_i}
\]

The following will also be recorded:

- active-context words/characters;
- latency and LLM calls;
- parsing or transport errors;
- IDs lost per round;
- cost, if the endpoint returns token usage.

## 7. Minimum Execution Matrix

| Scenario | Strategy | Rounds | Repetitions | Objective |
|---|---|---:|---:|---|
| E1 | Baseline | 5 | 3 | Observe cumulative degradation |
| E2 | Triage | 5 | 3 | Verify pinned constraints |
| E3 | Fake deterministic | 5 | 1 | Validate runner and offline metrics |

## 8. Interpretation

- Do not directly compare local results with the paper's reported percentages without replicating its configuration.
- 100% constraints in triage demonstrates the policy, not that all memory is perfect.
- If active context grows substantially, report the cost alongside recall.
- API failures are excluded from the denominator and presented separately.

## 9. Minimum JSON Output

```json
{
  "run_id": "2026-08-28T150000Z",
  "dataset_hash": "...",
  "model": "...",
  "settings": {"rounds": 5, "target_words": 700},
  "rounds": [
    {
      "round": 1,
      "strategies": {
        "baseline": {"constraint_recall": 0.875, "lost_ids": ["C07"]},
        "triage": {"constraint_recall": 1.0, "lost_ids": []}
      }
    }
  ]
}
```

