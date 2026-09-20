# Base-overlap weighting diagnostic

## Question fixed before execution — September 20, 2026

The existing pooled correct-proposal overlap is larger for C3 than C2.
Hypothesis: this direction survives equal weighting of the same theorems,
rather than arising solely from differing numbers of correct samples on easy
theorems. This is an exploratory check of a specific descriptive claim, not
a new superiority endpoint or a test of semantic retention.

Use the finalized C0/C1/C2/C3 pass@128 logs identified by the symmetric recovery
artifact, rechecking hashes, finalized metrics, sample budgets and datasets.
For tactic modes and normalized exact proofs, compute the fraction of each
condition's correct samples whose theorem-specific ID occurs in C0. Report:

- original pooled fractions over each condition's solved theorems;
- equal-theorem and pooled fractions on the common C1/C2/C3 solved panel;
- paired C3-minus-C2 and C1-minus-C3 differences and positive/negative/tie counts;
- the same summaries separately for validation and miniF2F test.

Do not silently turn undefined fractions on unsolved theorems into zero.
Report their exclusion explicitly. C0-unsolved theorems remain in the common
panel with zero observed base overlap. No resampling, new generation, learned
judge or fresh Lean verification. The source counts are finite samples;
conditioning on observed success and finite C0 coverage remain limitations.
If the direction disappears, revise the descriptive characterization. If it
survives, retain it as a distributional distinction, not a demonstrated benefit.

## Result

The direction survives. On 275 theorems solved by all three trained conditions
(154 validation, 121 test), equal-theorem mean correct-sample overlap is:

| Observed C0 support | C1 GRPO | C2 unlikely | C3 zero-advantage blocking |
|---|---:|---:|---:|
| Tactic patterns | 72.23% | 61.31% | 66.92% |
| Normalized exact proofs | 14.88% | 7.70% | 10.83% |

C3-minus-C2 is +5.61 percentage points for tactic patterns (+4.99 validation,
+6.40 test) and +3.14 for exact proofs (+3.73 validation, +2.38 test).
Tactic overlap is higher for C3 on 208 theorems, lower on 56, tied on 11;
exact overlap is higher on 196, lower on 50, tied on 29.
The pooled calculations reproduce the earlier report's rounded values.
All 467 theorems had 128 attempts per condition: 59,776 registered attempts
each, 239,104 across C0/C1/C2/C3. This diagnostic made no new proof attempts.
The common-solved restriction excludes 192 theorems, not 192 failed attempts.

This rules out unequal weighting by correct-sample counts as the sole
explanation of the observed direction. It does not eliminate other confounds,
prove a population-level effect, or measure forgotten mathematical capability.
C1 remains above C3 by 5.31 points on tactic patterns and 4.05 on exact proofs.
Therefore maximizing this overlap would favor ordinary GRPO, not our method.
No new application superiority claim is justified. A target-domain evaluation
would have to establish a useful benefit separately and include C2; this result
alone does not justify another training run. C5 reward rejection is unmeasured.

## Reproduction and validation

From the repository root:

```bash
PYTHONPATH=. ../environment/venv/bin/python scripts/project/analyze_base_overlap.py \
  --source-manifest results/symmetric_recovery_c0_c1_c2_c3_seed42_pass128.json \
  --output /path/to/new-output.json
```

The committed result is `results/base_overlap_weighting_seed42_pass128.json`.
It includes source hashes and per-theorem overlap/denominator counts. The
driver rejects changed source files and refuses output overwrite. Three new
unit tests cover weighting reversal, unsolved exclusion versus zero overlap,
and an empty common panel. All 82 repository unit tests pass. The analysis
successfully revalidated the four finalized logs and their registered metrics;
these checks are not fresh Lean verification or independent statistical trials.
