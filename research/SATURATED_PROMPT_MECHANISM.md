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

## Pre-analysis follow-up: occurrence in completed training samples

Before reading the aggregate admission counts, ask whether all-correct groups
with both frozen-archive blocked and alternative modes actually occur in the
eligible completed C2/C3 logs. Reuse the finalized training comparison's source
hashes, 9,655 theorems and first 32 proposals per theorem; exclude the one padded
group per run. Apply the original C0 archive (threshold >0.5, minimum four
verified proofs) to both conditions, without changing it. C2 archive membership
is counterfactual, not an intervention that occurred during its run.

Report exhaustive correctness/mode strata, counts eligible under each admission
rule on the same saved groups, and the names of groups newly admitted by reward
rejection relative to zero-advantage blocking. Also report groups lost relative
to soft weighting because all observed correct proofs are blocked. Validate
C3 reconstructed blocked counts against its telemetry and finalized metrics.
No significance threshold, performance ranking, or C5 trajectory extrapolation
is intended. The decision is whether this mechanism merits explicit admission
accounting in a future C5 comparison; zero occurrences would weaken that
motivation, while nonzero counts establish exposure only, not utility.

## Completed-log result

The exposure is nonzero in both completed runs. Each panel contains 9,655
theorem groups of 32 proposals (308,960 registered attempts); 1,014 theorems
are eligible under the frozen archive. The extra physical padding group is
excluded in each condition. Source metrics, proof hashes, resolved configs,
training parquet equality, correctness totals and C3 per-theorem blocking
telemetry all passed validation.

On **C2's saved samples**, 275 all-correct groups contain both blocked-mode and
alternative proofs: 2.85% of all theorem groups, or 27.12% of archive-eligible
groups. The admission rules select 5,885 groups under soft weighting, 5,871
under zero-advantage blocking, and 6,146 under reward rejection. Relative to
soft weighting, rejection adds those 275 saturated groups but loses 14 mixed-
correctness groups whose correct proofs are all blocked (net +261 groups).

On **C3's saved samples**, the corresponding newly admitted count is 347:
3.59% of all groups, or 34.22% of archive-eligible groups. Soft, zero-advantage
and rejection rules select 4,762, 4,730 and 5,077 groups respectively. Rejection
adds 347 relative to zero-advantage blocking; relative to soft weighting, it
also loses 32 mixed-correctness groups with no unblocked correct proof (net
+315 groups). The 13,906 archive-matching correct proofs exactly reproduce
the finalized C3 registered block count. Its 26 fully-correct/all-blocked plus
32 mixed-correctness/only-blocked groups account for 58 skipped prompts.

The C3 admitted count times 32 reproduces 151,360 logged update-batch samples.
The registered C2 count gives 188,320, versus 188,352 logged physical samples;
the 32-sample difference equals its excluded padding allowance. The admission
analysis deliberately reports registered groups, not physical optimizer work.

Conclusion: saturated-prompt admission is a material diagnostic to include in
future C5 interpretation, particularly inside the archive-eligible subset.
These counts **do not predict C5's future distribution**, prove capability
retention, or establish an advantage over admission-aware soft weighting.
All-correct groups with no blocked mode are much more numerous (1,961 in C2,
2,943 in C3); rejection would still discard those. This reinforces the need
to distinguish selective mode-based admission from merely keeping more
all-correct training groups.

The complete compact artifact, including qualifying theorem names and counts,
is `results/training_admission_c2_c3_seed42.json`, SHA-256
`5d2b66a11953d3f8eb5d562635a0c9bf5d2c19f09ebc0778aaf1b1a1a2f9abe2`.
All 93 project tests pass. No new proof attempts, optimizer steps or changes
to training recipes were made.

```bash
PYTHONPATH=.:../verifier/DeepSeek-Prover-V1.5 ../environment/venv/bin/python scripts/project/analyze_training_admission.py --source-manifest results/c2_unlikeliness_vs_c3_training_seed42.json --output /path/to/new-output.json
```
