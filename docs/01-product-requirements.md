# Product Requirements

## 1. Purpose

Build a Python console application that compares LLM-compacted monolithic memory with typed memory based on `Knowledge Triage`.

## 2. Target User

Architects and developers who want to understand and demonstrate the risk of degrading rules, decisions, and knowledge when an agent's history is repeatedly summarized.

## 3. MVP Scope

The application must:

1. Load 30 to 50 memory items from JSON.
2. Support five types: `constraint`, `decision`, `evidence`, `episode`, and `preference`.
3. Run two strategies against identical copies of the dataset.
4. Perform five compaction rounds.
5. Apply deterministic perturbations between rounds to simulate context growth.
6. Evaluate which items remain retrievable after each round.
7. Generate structured results and a readable summary.

## 4. Out of Scope

- Web interface, database, embeddings, or vector database.
- Multi-user or distributed memory.
- Semantic evaluation based exclusively on another LLM.
- Exact reproduction of the percentages published in the paper.
- Integration with an agentic framework.

## 5. Functional Requirements

| ID | Requisito | Prioridad |
|---|---|---|
| FR-01 | Load and validate a versioned JSON dataset | Must |
| FR-02 | Run `baseline` and `triage` with identical configuration | Must |
| FR-03 | Pin constraints in the triage strategy | Must |
| FR-04 | Compact episodes using an LLM | Must |
| FR-05 | Keep knowledge/evidence outside the summary and retrieve it through a simple query | Must |
| FR-06 | Run N configurable rounds, defaulting to 5 | Must |
| FR-07 | Measure overall recall and recall by type | Must |
| FR-08 | Record model, temperature, limits, and input hashes | Must |
| FR-09 | Export `results.json` and `summary.md` | Should |
| FR-10 | Support API-free execution through a deterministic fake compactor | Should |

## 6. Non-Functional Requirements

- Python 3.11 o superior.
- Run the LLM locally through vLLM and an OpenAI-compatible API.
- Installable and executable project with no dependencies on other repositories.
- No secrets in code or results.
- `temperature=0` when supported by the provider.
- Explicit timeout and limited retries.
- Domain logic must not depend on `requests` or the LLM provider.
- A failed run must not count as memory loss; it must be recorded as an experimental error.

## 7. Minimum Model

```text
MemoryItem
  id: str
  type: constraint | decision | evidence | episode | preference
  text: str
  criticality: critical | high | normal
  scope: str
  provenance: str
  retention_policy: pin | compact | retrieve
  check_terms: list[str]
```

`check_terms` contains brief canonical facts needed to evaluate preservation without requiring full textual matching.

## 8. Acceptance Criteria

- The same input feeds both arms without shared mutation.
- No constraint with a `pin` policy is sent to the LLM for rewriting.
- Each round produces metrics by strategy and type.
- The lost item can be identified, not just an aggregate percentage.
- Unit tests can run without a network connection.
- Secret configuration is loaded from environment variables.
- Offline test mode requires neither a GPU nor a vLLM server.

## 9. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| The LLM returns unstructured text | JSON contract, defensive parser, and explicit failure |
| A lexical verifier penalizes valid paraphrases | Normalized `check_terms` and manual review of discrepancies |
| The result depends on randomness/provider | Low temperature, multiple repetitions, and recorded configuration |
| Unfair comparison due to different budgets | Same token limit and same compression pressure |
| Pinning "cheats" | Declare it as a deliberate architectural policy and also measure context cost |
