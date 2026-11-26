# APRIL repair supervision versus unassisted RLVR

## Question

Does explicit feedback-conditioned SFT primarily improve local correction,
whereas outcome-only RLVR improves the probability of executable reasoning
without a failed-proof prompt? These capabilities need not coincide.

[Wang et al., Learning to Repair Lean Proofs from Compiler Feedback (v2)](https://arxiv.org/html/2602.02990v2)
constructs failures by mutating already verified proofs, trains via LoRA SFT
on erroneous code, local state and compiler diagnostics, and evaluates
single-shot conditional repair. Failure categories are theorem/lemma
substitution, tactic substitution, single-line replacement and suffix
replacement. The initial correct targets are from Herald, Lean Workbook and
NuminaMath-Lean, verified in Lean 4.22.0-rc4. Theorem-level splitting
is reported; these are not natural model failure distributions.

## Reported Goedel V2 8B results

| Mutation | Base | Joint repair + explanation | Repair only |
|---|---:|---:|---:|
| Overall | 15.5 | 34.6 | 36.7 |
| Tactic | 19.6 | 41.7 | 48.5 |
| Line | 20.0 | 18.5 | 25.5 |
| Theorem | 12.7 | 36.8 | 37.5 |
| Multi-line | 19.4 | 20.8 | 24.3 |

Percent accuracy, paper Table 2 and [released repair-only model card](https://huggingface.co/uw-math-ai/gAPRIL-wo-exp).
The gains are concentrated in tactic/theorem substitutions; the joint
model actually drops 1.5 points on the line category. The paper's Table 3
contains category-specific training results, so avoid conflating its single
category experiments with the joint model. Qwen3-4B goes 1.1→27.4 overall,
and Kimina-8B 11.1→31.9. Explanation training is not required for most gains.
No reported unassisted theorem-generation control, or proof-body preservation
measurement for generated repairs, was found. The scores are conditional on
being given the flawed proof plus true feedback, unlike our held-out C0/C1
unassisted generation comparison. No numerical head-to-head is warranted.

## Dataset readback, hypothesis

Download the four published holdout files and model cards only. Hypothesis:
APRIL reference corrections are predominantly local and observation of
one-line matched pairs is structurally enriched relative to natural rollout
failures by construction. Measure exact source-line opcodes, changed line
counts, and the locality of source edits. This describes dataset targets,
NOT what repair-trained models actually output. Full source includes header
and declaration: do not equate retained source lines with retained proof
steps. No generation or verifier run.

| Held-out reference mutation | Rows | Exactly one line changed | Multi-line changes | Identical splitlines |
|---|---:|---:|---:|---:|
| Theorem | 1093 | 1093 | 0 | 0 |
| Tactic | 398 | 198 | 200 | 0 |
| Line | 200 | 142 | 56 | 2 |
| Multi-line | 144 | 7 | 137 | 0 |
| Total | 1835 | 1440 (78.5%) | 393 | 2 |

25 rows lack retrieved proof state under the explicit field check; all
contain error text. Exact-line equality ignores line ending differences;
two identical cases need independent verifier audit if used experimentally.
No new Lean judgments were made.
See [reference audit](experiments/april_comparison_20261125/reference-edits.json)
and [download inventory](experiments/april_comparison_20261125/inventory.json).
Actual per-example predictions for pre/post models were not located in
the cited HF dataset/model trees or targeted repository search. The released
test files and weights are available, but test reference corrections cannot
substitute for measured generated edits. We did not download bulk weights.

## Independent deployed repair evidence

[Deng et al., Fix, Not Just Resample (October 2026)](https://arxiv.org/html/2610.26942v1)
deploys gAPRIL-wo-exp as a separate bounded repair module in tactic search.
At K=8 and R=1, 5,543 of 89,634 rejected tactics transition to a valid
successor (6.2%). Rates by failure category are 14.6% no-progress/simp,
13.2% apply/exact, 11.0% rfl, 5.4% unknown identifiers, 4.7% rewrite,
2.0% typeclass/synthesis and parse, 1.8% type mismatch, and 0.8% unsolved/timeout.
These are tactic-state recoveries, not full accepted proofs. This independent
result supports localized execution repair; it doesn't show a general
reasoning limitation of the model. Raw run logs were not located. The paper
reports gain over sampling-only search, including under matched time budgets,
but the added repair model and search resources differ from our RL protocol.

## Implication and proposed discriminating test

Our own C0-to-C1 exact recurrence improved despite no failure or diagnostic
being included during held-out generation. Yet broader multi-line scaffold
coverage declined relative to same-model resampling. This supports learning
reliable execution patterns, but doesn't identify internal representations
or establish abstraction/generalization. APRIL shows direct training can
produce strong conditional repair, especially close substitution failures.
It has not established transfer to independent theorem completion or
preservation of the original reasoning body.

A decisive prospective experiment would compare Goedel-V2-8B (released
parent) vs both published repair-specialized checkpoints on:
1. Unassisted theorem completion with identical prompt and sampling.
2. A natural failed-proof panel from that very parent, with diagnostic,
   withheld-diagnostic, and instruction-only resampling controls.
3. The same exact/scaffold outcome measures and verified minimal edit
   distances, stratified by mistake type on disjoint theorem identities.
This distinguishes correcting the supplied execution from improving its
unassisted probability, and correction from wholesale regeneration.
Use the same Lean 4.22.0-rc4 environment and authenticate actual prompt
formats; no claim is made that these prospective results already exist.
