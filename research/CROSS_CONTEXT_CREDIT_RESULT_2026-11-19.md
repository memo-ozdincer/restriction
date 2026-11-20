# Cross-context credit supplies a learning signal after local success saturates

The registered screen passed: induction, rational cancellation, and shear
identities each contain locally correct samples with different verified peer
coverage. Three source tasks were solved in all 16 attempts, giving constant
local correctness rewards, while cross-context rewards varied. This supplies
a concrete candidate learning signal beyond source-task success. It is **not
a trained-model result**; no research parameters were updated.

| Training family | Samples | Locally correct | Correct, ≥2 peers | Correct, ≤1 peer |
|---|---:|---:|---:|---:|
| Nonzero extraction | 64 | 8 | 8 | 0 |
| Witness extraction | 64 | 1 | 0 | 1 |
| Shear identity | 64 | 62 | 59 | 3 |
| Rational cancellation | 64 | 64 | 62 | 2 |
| Induction/case closure | 64 | 55 | 6 | 49 |

Every candidate was checked unchanged against its four family contexts. All
1,280 logical judgments are resolved by 540 unique complete-source Lean checks;
there were zero parser rejections, missing verdicts, or verifier system errors.
Exact-source caching accounts for the difference, not discarded samples.
The independent audit reconstructs all source/peer code, checks every kernel
acceptance and axiom audit, and reproduces all rewards and the registered gate.

For natural-number closure, both of these sampled continuations are correct:

```lean
  intro n; induction n with
  | zero => exact h0
  | succ n ih => exact hs n ih
```

```lean
  intro n; induction n <;> simp_all
```

The constructor-specific sample passes zero peers; the generic sample passes
two. Both receive local reward 1, but cross rewards 0 and 2/3 respectively.
The latter delegates constructor-specific reasoning to Lean tactics; this is
portable procedure behavior, not proof that the model invented induction.
Five source groups separate local-success candidates by peer validity:
`induction_0`, `induction_1`, `rational_2`, `shear_2`, `shear_3`.
Local reward is constant and cross reward varies in `induction_0`, `rational_2`,
and `shear_2`.

## A material alternative explanation: shorter proofs

A post-screen diagnostic assigns each group's **same cross-reward multiset**
to its locally correct samples ordered by shorter generated-token length,
breaking ties by sample ordinal. This reproduces the cross rewards exactly
for 19/20 source groups. Only four assignments in `shear_3` differ. Thus this
screen does not distinguish rewarding portability from preferring shorter
correct proofs. A length-matched reward control is required in the training
comparison; local-versus-cross alone cannot support a semantic-credit claim.
This diagnostic does not alter the registered gate or erase the measured
reward contrast. It limits its interpretation and changes the next experiment.

## Compute and preservation

Job 1372689 used one H100 under def-zhijing, was held by the Python keeper, and
was launched manually over SSH in the allocation. The driver completed in
437.8 seconds; the entire retained allocation lasted 12m55s and was automatically
released. Generation used 6,258 output tokens and 27,696 supplied tokens counted
per proposal. Forty-two CPU validation calls and two separately logged import
warmups are additional to the 540 candidate checks: 584 physical Lean calls in
total. Warmups used 300 seconds maximum; all scientific checks used 60 seconds.

The raw archive `cross-context-credit-evidence.tar.gz` contains 39 files,
1,450,718 uncompressed bytes: candidates, all edges, complete checked sources,
verdicts, frozen code/panel/registration, model hashes, terminal accounting,
independent/length audits, and the isolated adapter runtime check. Per-file
hashes and a download-verification receipt are in
`experiments/cross_context_credit_20261119/`. Research model weights remain
excluded. The only adapter in this archive is a tiny random-model CPU fixture.

## Next training requirements

Freeze a matched policy-improvement comparison from the pristine base with
local credit, cross-context credit, and length-matched credit. Before attributing
a promising gain to a distinct RL mechanism, include same-information verified
replay. All arms must receive the same bank and verification information, with
compute and optimized tokens reported. Cross-context credit is gated on source
correctness; unresolved judgments cannot become negative rewards.

The screen stored decoded completions and token counts, **not exact sampled
token IDs**. Do not reconstruct those strings and silently call them on-policy
trajectories. A training rollout collector must preserve prompt/response token
IDs, stopping behavior, sampling settings, and old-policy probabilities before
policy updates. Fresh collection for training is necessary instrumentation, not
a repeat of this screen for another chance to pass its gate.

Freeze a fresh root-level composition evaluation, optimizer/budget, and final
checkpoint rule before training. Keep the October multi-edge graph panel
evaluation-only and the already-inspected November recurrence targets outside
held-out claims. The older prefix/frontier studies' gates are unchanged.
The goal remains a generalizable training mechanism; passing this signal screen
alone does not satisfy it.
