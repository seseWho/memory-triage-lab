# Compaction Cliff PoC

A small Python application demonstrating that treating agent memory as a single block loses critical information after successive compactions, while typed memory with differentiated policies preserves it more effectively.

It is an **independent and self-contained** PoC. It does not import code from other projects. It runs the model locally through **vLLM**, exposing its OpenAI-compatible API at `http://localhost:8000/v1`.

## Experimental Question

> Does a `Knowledge Triage` strategy preserve more critical constraints than conventional compaction, using the same items, model, output budget, and number of rounds?

This repository guides an experiment; it does not attempt to fully reproduce the paper or build an enterprise memory platform.

## Documents

1. [01-product-requirements.md](01-product-requirements.md): purpose, scope, requirements, and acceptance criteria.
2. [02-architecture.md](02-architecture.md): architecture, data model, and prioritized decisions.
3. [03-experiment-protocol.md](03-experiment-protocol.md): dataset, procedure, metrics, and controls.
4. [04-implementation-plan.md](04-implementation-plan.md): project structure, tasks, and execution order.
5. [05-test-plan.md](05-test-plan.md): test strategy and essential cases.
6. [06-vllm-local-guide.md](06-vllm-local-guide.md): installation, model selection, and local execution.

## Expected Result

The application will run two arms:

- **Baseline**: all items are serialized as text and compacted with the LLM in each round.
- **Knowledge Triage**: constraints are pinned without compression; episodes are compacted; knowledge remains available for selective retrieval.

After each round, every item will be evaluated using identifiers and verifiable claims. The output will be `results.json` and a console summary with recall by type, constraint recall, approximate context size, and observed failures.

## PoC Success Decision

The hypothesis will be considered demonstrated if, after five rounds:

- Triage preserves 100% of critical constraints by construction.
- The baseline loses at least one constraint in some run or shows lower mean recall.
- Results are repeatable through a seed, versioned dataset, and recorded configuration.

If the baseline does not lose constraints, the experiment remains valid: it should be repeated with more compression pressure without changing the rules between strategies.

## Independence

The four provided Python files were reviewed solely as reference material. They will not be part of the project and will not be needed to install or run it. The new client will be minimal, internal to the PoC, and specific to vLLM/OpenAI-compatible APIs.
