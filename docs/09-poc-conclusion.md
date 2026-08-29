# PoC Conclusion

## Scope

This PoC tests whether a typed-memory lifecycle can preserve more information than a monolithic
compactor over five repeated rounds. It is an implementation demonstration, not a reproduction of
the paper's production study and not evidence for enterprise-scale performance.

The conclusion is based on the real vLLM Run 003, using `qwen3-8b-awq`, the 40-item synthetic
dataset, five rounds, temperature `0.0`, seed `0`, and `max_tokens=4096`.

## Observed result

| Strategy | Recall | Weighted recall | Active items | Explicitly retrieved | Ambiguous | Lost |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 57.5% | 53.0% | 40 | 0 | 17 | 0 |
| Knowledge Triage | 100% | 100% | 32 | 8 | 0 | 0 |

The values were unchanged across all five rounds. Triage used an average of 554 prompt tokens per
round versus 869.2 for baseline (36.3% fewer) and an average latency of 12.02 seconds versus
18.85 seconds (36.2% lower).

## Interpretation

The experiment demonstrates the intended PoC concept: separating pinned constraints, compactable
memory, and retrievable evidence prevents the baseline's lexical preservation failures in this
dataset. Explicit retrieval accounting also shows that information outside active context can be
scored without treating storage alone as recovery.

The baseline's 17 ambiguous items are not 17 confirmed semantic losses. The Run 002 audit classified
six as probable semantic weakenings and eleven as valid paraphrases or lexical false negatives.
This means the result is strongest as evidence of a preservation-contract difference, not as a
literal estimate of semantic memory loss.

## Limitations

1. Retrieval is a deterministic oracle that requests every `RETRIEVE` item; it does not measure
   query formulation, ranking, precision, or recall.
2. The strategies do not yet have equal active-context budgets: triage keeps 32 active items while
   baseline keeps 40.
3. The evaluator is deterministic and lexical. It can miss valid synonyms and does not fully model
   modality, scope, or numerical equivalence.
4. This is one model, one dataset, one seed, and one five-round run. No statistical generalization
   is justified.

## Final PoC decision

**The hypothesis is supported for this controlled demonstration, with important qualifications.**
Typed memory and differentiated lifecycle policies preserved all evaluated items while reducing
active payload and observed latency. The result should not be presented as proof that Knowledge
Triage universally outperforms monolithic compaction.

## Recommended next step

The most valuable extension is a budget-matched run in which both strategies receive the same active
context allowance. Query-driven retrieval and a semantic evaluator can then be added if a stronger
research result is needed. They are outside the scope of this small PoC.

Evidence: [Run 002 audit](../evidence/runs/002-qwen3-8b-awq/ambiguity-audit.md) and
[Run 003](../evidence/runs/003-qwen3-8b-awq/README.md).
