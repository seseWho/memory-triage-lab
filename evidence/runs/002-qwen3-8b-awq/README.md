# Run 002 — qwen3-8b-awq

This is the first fully traceable real vLLM run. It was executed on 29 August 2026 with five rounds,
temperature `0.0`, seed `0`, and `max_tokens=4096`.

Artifacts:

- [`summary.md`](summary.md): generated Markdown summary.
- [`results.json`](results.json): generated results with per-round item text and settings.
- [`ambiguity-audit.md`](ambiguity-audit.md): manual review of the 17 baseline ambiguous IDs.

The audit finds six probable semantic weakenings and eleven valid paraphrases or lexical false
negatives. There are no confirmed disappearances. This is still an exploratory result because the
retrieval tier is credited without an explicit query and the arms do not yet share an equal total
active-context budget.

