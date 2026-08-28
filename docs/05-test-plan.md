# Test Plan

## 1. Approach

Separate software tests from experiment runs. Tests verify contracts and invariants; they must not claim that a specific LLM will necessarily forget a rule.

## 2. Priority Unit Tests

| ID | Case | Expected result |
|---|---|---|
| UT-01 | Valid dataset | 30–50 `MemoryItem` objects with unique IDs are created |
| UT-02 | Invalid type or policy | Clear validation error |
| UT-03 | Constraint triage | `pin` is assigned |
| UT-04 | Five triage rounds | Canonical constraint text remains identical |
| UT-05 | Evaluation with all terms | Item is retrieved |
| UT-06 | Missing a term | Item is ambiguous/lost according to configuration |
| UT-07 | Metric by type | Correct numerator and denominator |
| UT-08 | Strategy copies | One strategy does not mutate the other's input |
| UT-09 | Fake compactor | Same input and seed produce the same output |
| UT-10 | LLM error | Error is recorded; it is not recorded as forgetting |

## 3. Integration Tests

- HTTP adapter sends `messages` to `/chat/completions`.
- Timeout and 4xx/5xx codes produce typed errors.
- JSON response fenced in Markdown is normalized or explicitly rejected.
- An offline run generates valid `results.json` and `summary.md`.
- A real run records the model and parameters without including secrets.
- The smoke test queries the model served by vLLM on localhost.

## 4. Acceptance Tests

### AC-01: Full Comparison

**Given** a 40-item dataset, **when** five rounds run with both arms, **then** metrics exist by round, type, and strategy.

### AC-02: Deterministic Constraint

**Given** a critical constraint, **when** triage runs five rounds, **then** its canonical representation retains the same hash.

### AC-03: Loss Traceability

**Given** that an item is lost, **when** the report is created, **then** its ID, type, round, and strategy appear.

### AC-04: Experimental Equality

**When** a round begins, **then** both arms receive the same dataset, noise, and configured budget.

## 5. Review of the Attached Tests

The attached suites serve as smoke-test references, but they will not be copied or become PoC dependencies:

- `test_response_time < 5s` is fragile over VPN, proxy, or a local model; measuring and reporting latency is preferable to failing on a fixed threshold.
- The 100,000-character context test depends on the model limit and may not raise an error.
- Temperature and reasoning tests are nondeterministic.
- Two suites are partially duplicated.
- Instantiating the client with network validation in `setUp` turns unit tests into integration tests.

Recommendation: keep a single adapter integration test marked `integration`, and create unit tests with `FakeCompactor`.

## 6. Target Commands

```bash
pytest -m "not integration"
pytest -m integration
python -m memory_cliff.cli run --offline
```

The `integration` tests require vLLM to be running; the rest must work on a machine without a GPU.

