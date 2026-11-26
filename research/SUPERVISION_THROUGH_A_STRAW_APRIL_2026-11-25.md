# Supervision Through a Straw: APRIL evidence audit

User direction: use published controlled supervision/no-additional-supervision
comparisons to examine whether interventions improve their target while
suppressing other useful reasoning. No new experiments requested.

Primary source: [Wang et al., Learning to Repair Lean Proofs from Compiler Feedback,
arXiv:2602.02990v2, March 13 2026](https://arxiv.org/html/2602.02990v2).
Model cards: [Goedel with explanations](https://huggingface.co/uw-math-ai/gAPRIL-w-exp),
[without explanations](https://huggingface.co/uw-math-ai/gAPRIL-wo-exp).

## What is actually compared

APRIL trains LoRA adapters by supervised fine-tuning, not RL. Its two
interventions are synthetic failure-to-repair supervision and an optional
additional natural-language diagnosis/fix target. Baselines are unchanged
models evaluated using the same failing-proof/diagnostic repair interface.
The base provers are already trained; absence of APRIL does not mean absence
of prior supervision. The repair task is not independent theorem generation.

The study generates 260,125 mutations from 39,492 verified theorems. The
1,835 test instances represent 200 source theorems, with 398 tactic,
200 line, 1,093 theorem-substitution and 144 multi-line mutations
(Table 4, Appendix A). Theorem substitution alone is 59.6% of test instances.
The mutations deliberately preserve a relationship to a known correct proof.
Theorem and tactic explanations are generated with privileged knowledge of
the intended replacement. Natural failures are a different distribution.

## Table 2: joint repair/explanation training versus unchanged model

| Model | Full | Tactic | Line | Theorem | Multi-line |
|---|---:|---:|---:|---:|---:|
| Goedel 8B, unchanged | 15.5 | 19.6 | 20.0 | 12.7 | 19.4 |
| Goedel 8B, APRIL | 34.6 | 41.7 | 18.5 | 36.8 | 20.8 |
| Difference (pp) | +19.1 | +22.1 | -1.5 | +24.1 | +1.4 |
| Kimina 8B, unchanged | 11.1 | 17.3 | 14.5 | 7.9 | 13.9 |
| Kimina 8B, APRIL | 31.9 | 38.9 | 18.5 | 34.1 | 14.6 |
| Difference (pp) | +20.8 | +21.6 | +4.0 | +26.2 | +0.7 |
| Qwen 4B, unchanged | 1.1 | 1.8 | 2.5 | 0.5 | 0.0 |
| Qwen 4B, APRIL | 27.4 | 39.7 | 16.0 | 26.8 | 13.2 |
| Difference (pp) | +26.3 | +37.9 | +13.5 | +26.3 | +13.2 |

All values are percentages. Goedel's line-mutation drop is only 1.5 points
(three of 200 cases net, given reported percentages); paired outcomes and
uncertainty unavailable, so do not claim a resolved suppression effect.
Using test-category counts and rounded Table 2 Goedel deltas, the
theorem-substitution category contributes 14.35 pp of the 19.09 pp weighted
overall gain (75.2%); tactic mutations contribute 4.79 pp. The aggregate
success overwhelmingly reflects designed substitutions; neither this
decomposition nor the line result establishes reduced theorem-proving ability.

## Table 3: the more direct prescriptiveness comparison

Compare repair-only supervision to repair plus explanation supervision:

| Model | Repair-only full | Joint full | Difference (pp) |
|---|---:|---:|---:|
| Goedel 8B | 36.7 | 34.6 | -2.1 |
| Kimina 8B | 36.9 | 31.9 | -5.0 |
| Qwen 4B (section 5.3) | 31.2 | 27.4 | -3.8 |

The 8B error-specific rows in Table 3 describe matched training/evaluation
regimes, not the joint model's Table 2 breakdown. Nine of ten error-specific
and full rows across Goedel/Kimina decrease and one ties (Kimina line).
Do not combine specialized model category numbers into the all-error score.
The model cards reproduce some category comparisons but mix Table 2 joint
values with Table 3 regime-specific values; prioritize the paper's explicit
table caption. The paper attributes the trade-off to interpretability, not
suppression of mathematical capabilities. It also reports a small downstream
demonstration: DeepSeek repair with base Qwen explanations 4% vs 29% with
trained explanations. That is counterevidence to a universal claim that
the additional structure is useless.

## Appendix D: the most conceptually relevant observation

The authors attempted natural-failure mining: Kimina 1.7B generated proofs,
and Goedel V2 8B tried to repair rejected attempts. The latter commonly
generated substantially different proofs instead of editing the prior one;
the pipeline yielded few valid repairs and was excluded as insufficiently
aligned. They also report other artificial corruption schemes that could
not produce realistic or controllable matched failures.

This is a distinction between *not preserving a known proof structure*
and *not being useful at theorem proving*. Re-proving is legitimate under
terminal Lean correctness. Nonetheless, the paper did NOT quantify a
matched resampling comparison for that discarded pipeline, nor show
that the discarded alternative proofs were generally correct. It would
be unfair to call this evidence of suppression by APRIL training.

## Classification for the prospective literature synthesis

- Repair SFT vs unchanged: positive intended-task effect, no independent
  ordinary-proof-generation metric reported. Retention, proof quality,
  unassisted pass@N, loss of alternative strategies unknown.
- Additional explanation supervision vs repair-only: narrow measured
  trade-off in favor of less prescriptive supervision, at the cost of
  interpretability; no proven broader capability loss or RL causal effect.
- Natural failed proofs vs manufactured near misses: conceptual mismatch
  between desired human-readable edit and autonomous proving, motivated
  by Appendix D and our scope-repair data.
- Not admissible as a demonstration that ordinary terminal RL outperforms
  APRIL, that APRIL suppresses a large volume of mathematical work, or
  that any added supervision necessarily harms a prover.

For the thesis, retain this as a qualified example of supervision overhead
and objective mismatch, not a headline falsification of repair training.
A stronger literature candidate is a direct same-model intervention vs
terminal-only RL or instruction-only resampling with a shared external
performance metric. The user's current request is literature analysis only.
