# Saturated-prompt admission diagnostic

September 21, 2026. CPU-only mechanism diagnostic, not a model-performance
experiment. Hypothesis recorded before test execution: with the registered
`advantage_threshold=True`, all-Lean-correct groups are discarded by C1/C2/C3
before rank weighting, but C5 can retain such a group if it contains both
blocked and alternative proofs. C5 should then give the blocked proofs negative
and alternatives positive policy advantages. With no alternative, the existing
all-blocked skip must still apply.

Motivation: identify a concrete difference from rewarding the unlikely without
mining excluded C5 partial proof-quality outcomes. Test the actual trainer's
selection statements and advantage method on synthetic single-prompt groups.
Use synthetic archive membership and no generation, verifier or actor. This
isolates admission and reward/advantage logic; it cannot establish how often
these situations occur or whether they improve downstream capability.

Discriminating control: disabling only the advantage threshold in synthetic C2
should admit an all-correct group and allow unequal rank weights to produce a
nonzero signal. If so, saturated-prompt learning is not uniquely enabled by hard
blocking; part of the contrast comes from where the inherited admission filter
sits relative to the reward transformation. This is not authorization to change
the registered C2 recipe or silently replace its completed results.

## Observed result

All five controlled tests passed. They execute the production selection block
and `_compute_advantages` method, extracted with AST to avoid initializing Ray
and GPUs; archive membership is synthetic and the verifier is not executed.
The tested methods match frozen C2 `bc282d6` and C5 `a0f1235`: the only trainer
diff at diagnostic revision `9bc4226` is the separate restart-override guard.
Saved resolved C2/C5 configs both set `advantage_threshold: true`; rank penalties
are respectively 0.25 and 0.0, and C5 selects `reject_reward`.

- Four correct proofs, two blocked and two alternatives: C1/C2/C3 select none.
  C5 selects all four, with negative blocked and positive alternative advantages.
- Only blocked correct proofs, with or without incorrect candidates: C3/C5
  skip the prompt. Rejection does not supply an escape signal when no alternative
  was sampled. This statement concerns the task policy-gradient signal, not
  all possible parameter changes from other groups or regularization.
- All-correct proofs with no blocked mode: all four conditions select none.
- C2 with only its admission filter disabled: an all-correct group is retained;
  the synthetic most-likely proof gets negative advantage and least-likely proof
  positive advantage. Unequal likelihood ranks are sufficient here.
- A mixed group with one blocked correct, one alternative correct and two
  incorrect proofs: C3 gives the blocked proof zero advantage; C5 gives it
  negative advantage. Both give the alternative positive and incorrect proofs
  negative advantages.

## Interpretation and next decision

There is a concrete distinction beyond counting output patterns: C5 changes
which correct-saturated prompts enter optimization. C2's soft weighting occurs
after a binary-success-based admission filter; C5's rejection occurs before it.
Consequently, a future C5 effect could combine reward rejection with changed
training-data admission. This is a downstream consequence of the intervention,
not evidence that the registered comparison changed an additional config field.

It is **not an inherent advantage over soft exploration**: the synthetic control
demonstrates that soft weighting also provides a signal on such prompts when
admission accounts for it. Nor does this prove retention, elegant proofs, or
generalization. The test gives no population frequencies or trained-model effect.

Before attributing a future C5 advantage specifically to exclusion, measure
admission strata in eligible complete logs: mixed correctness, all correct with
mixed blocked/alternative modes, all blocked, and no sampled alternatives.
If the effect concentrates in newly admitted saturated prompts, an explicitly
registered admission-aware soft comparator would be a discriminating follow-up.
No new training, comparator modification, or excluded partial quality analysis
is authorized or performed by this diagnostic. The frozen final comparison
still requires a completed eligible C5 run.

Reproduce:

```bash
PYTHONPATH=.:../verifier/DeepSeek-Prover-V1.5 ../environment/venv/bin/python -m unittest discover -s tests -p 'test_saturated_prompt_mechanism.py' -v
```
