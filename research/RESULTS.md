# Results

Last updated: 2026-09-01

## Executive finding

Restriction-RL substantially broadens the correct proof distribution produced
by standard GRPO. Across 9,655 training theorems at the same 308,960-proposal
budget, Restriction-RL produces 53,825 distinct correct tactic signatures
versus 34,336 for standard GRPO, an increase of 56.8%.

The effect carries to held-out evaluation and strengthens with deeper
sampling. Across 467 theorems at 128 proposals each, Restriction-RL produces
10,444 correct tactic signatures versus 8,468 for standard GRPO, an increase
of 23.3%, while solving 277 versus 275 theorem/split pairs. At exactly 16
correct draws per common theorem, expected mode coverage is 10.18 versus 8.95
(+13.7%; paired `p = 1.79e-29`). The equal-correct advantage grows to 17.1%
at 32 draws and 20.4% at 64, so the observed tail benefit has not saturated.

## Conditions and fixed components

| ID | Actor initialization | PPO epochs | KL | Rank penalty | Hard blocking |
|---|---|---:|---:|---:|---|
| C0 | Frozen base model | 0 | n/a | 0 | No |
| C1 | Pristine base model | 1 | 0.02 | 0 | No |
| C3 | Pristine base model | 2 | 0.10 | 0 | Yes |

Fixed components:

- Actor and frozen reference: `deepseek-ai/DeepSeek-Prover-V1.5-SFT`
- Model revision: `e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`
- Seed: 42
- Training theorems: 9,655
- Training proposal budget: 32 per theorem, 308,960 registered proposals
- Registered-valid evaluation: 223 theorems
- miniF2F-test evaluation: 244 theorems
- Primary evaluation proposal budget: 32 per theorem, 14,944 registered proposals per condition
- Registered deep evaluation: 128 per theorem, 59,776 registered proposals per condition
- Correctness signal: Lean only
- Response length: 512
- Sampling: temperature 1.0, top-p 1.0, top-k disabled
- Source dataset SHA-256: `56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb`
- Combined evaluation parquet SHA-256: `f9fb4d92b529499fa684f81a01a51249a2b9e1736cf50412ca374f11dbf4d840`

Run commits:

- C1 training: `5ced4c3210381950d51048355fcbd95f50a6004a`
- C3 training: `265aecd7894dc0f751b5a89f299dab59047ca7a0`
- C1/C3 evaluation and finalization code: `45cf5b57a0601115f02eecda55665cc5e620c751`

## C0 archive

C0 was constructed from all 9,655 registered training theorems:

- Registered proposals: 308,960
- Lean-correct proposals: 168,029
- Theorems solved at pass@32: 7,785
- Correct tactic-signature modes: 73,635
- Exact normalized correct proofs: 133,898
- Dominant-mode-eligible theorems used by C3: 1,014 of 9,655
- Frozen archive SHA-256: `fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3`

The archive contains training rollouts only. Test-set rollouts were never used
to construct the blocklist.

## Training-run accounting

These metrics aggregate on-policy proposals observed throughout training.

| Metric | C0 base | C1 GRPO | C3 hard block |
|---|---:|---:|---:|
| Registered proposals | 308,960 | 308,960 | 308,960 |
| Lean-correct | 168,029 | 215,482 | 211,635 |
| Blocked correct | 0 | 0 | 13,906 |
| All-blocked prompts skipped | 0 | 0 | 58 |
| Samples entering update batches | 0 | 109,536 | 151,360 |
| Training pass@1 | 54.39% | 69.74% | 68.50% |
| Training pass@4 | 71.23% | 76.94% | 77.78% |
| Training pass@8 | 75.21% | 79.02% | 80.24% |
| Training pass@16 | 78.21% | 80.70% | 82.14% |
| Training pass@32 | 80.63% | 82.15% | 83.67% |
| Correct tactic-mode coverage | 73,635 | 34,336 | 53,825 |
| Exact correct-proof coverage | 133,898 | 66,515 | 111,570 |

C3 blocked 4.50% of all registered proposals and 6.57% of its correct
proposals. Incorrect proposals retained their upstream treatment. Blocked
correct proposals remained in physical compute accounting and received zero
policy advantage. No free replacement samples were generated.

### Training dynamics and C0-mode recovery

A post-registered replay groups the C1 and C3 on-policy rollouts into 100-step
windows and normalizes mode coverage by the number of correct rollouts. C1's
correct tactic modes per correct rollout fall from 0.325 in steps 1--100 to
0.104 in steps 501--600. C3 begins at a comparable 0.317 but retains 0.229 in
steps 501--600. Thus blocking substantially slows mode collapse but does not
reverse it; C3's own normalized richness is flat to declining late in the run.

Across the complete training sample, C3 has a lower mean top-mode share than C1
(0.519 versus 0.675) and a higher mean Simpson effective-mode count per solved
theorem (3.67 versus 2.49). On the 6,644 theorems with at least 16 correct
rollouts under both conditions, rarefaction to exactly 16 correct draws yields
5.46 expected modes for C3 and 3.64 for C1, a paired mean difference of 1.82.

The frozen C0 archive also permits a direct finite-sample suppression analysis.
Of the 16,515 C0 tactic modes observed at least twice but absent from C1's 32
rollouts, 7,155 (43.3%) appear under C3. At a minimum C0 count of four, C3
recovers 2,900 of 4,931 C1-absent modes (58.8%). The full window metrics,
paired rarefaction, suppression floors, and auditable proof examples are in
[`results/training_dynamics_c1_vs_c3_seed42.json`](../results/training_dynamics_c1_vs_c3_seed42.json).

## Final-checkpoint evaluation

### Registered-valid, 223 theorems

| Metric | C0 base | C1 GRPO | C3 hard block |
|---|---:|---:|---:|
| Correct proposals | 4,099 | 4,560 | 4,349 |
| pass@1 | 57.44% | **63.90%** | 60.94% |
| pass@4 | 65.19% | **67.13%** | 66.48% |
| pass@8 | 66.68% | **67.72%** | 67.65% |
| pass@16 | 67.83% | 68.06% | **68.42%** |
| pass@32 | 68.61% | 68.16% | **69.06%** |
| Solved at 32 | 153 | 152 | **154** |
| Correct tactic modes | **2,591** | 2,233 | 2,477 |
| Exact correct proofs | 3,966 | 3,832 | **4,090** |
| Mean correct modes per theorem | **11.62** | 10.01 | 11.11 |

C3 minus C1:

- pass@1: -2.96 percentage points
- pass@32: +0.90 percentage points, two additional solved theorems
- Correct tactic modes: +244, or +10.9%
- Mean correct modes per theorem: +1.09

### miniF2F-test, 244 theorems

| Metric | C0 base | C1 GRPO | C3 hard block |
|---|---:|---:|---:|
| Correct proposals | 2,257 | **2,762** | 2,658 |
| pass@1 | 28.91% | **35.37%** | 34.04% |
| pass@4 | 40.72% | 43.57% | **43.75%** |
| pass@8 | 43.66% | 45.60% | **46.12%** |
| pass@16 | 45.77% | 47.10% | **47.68%** |
| pass@32 | 47.95% | **48.77%** | **48.77%** |
| Solved at 32 | 117 | **119** | **119** |
| Correct tactic modes | **1,456** | 1,212 | 1,449 |
| Exact correct proofs | 2,240 | 2,402 | **2,585** |
| Mean correct modes per theorem | **5.97** | 4.97 | 5.94 |

C3 and C1 solve the same number of miniF2F theorems at pass@32, but C3
recovers 237 correct tactic modes relative to C1 and nearly returns to C0 mode
coverage.

## Paired theorem-level analysis

Across all 467 evaluation theorems:

- Solved by both C1 and C3: 268
- Solved only by C1: 3
- Solved only by C3: 5
- Solved by neither: 191
- Exact paired McNemar test: `p = 0.727`

There is no statistically detectable difference in pass@32 theorem identity.
The result also shows no detectable heterogeneity among the eight discordant
theorems by the deterministic exploratory strata used here:

- Theorem-name family: `p = 0.292`
- Numeric type/domain: `p = 0.554`
- C0 correct-count difficulty bin: `p = 0.850`

### C3-only pass@32 theorems

| Theorem | Dataset | Family | C0 correct | C1 correct | C3 correct |
|---|---|---|---:|---:|---:|
| `mathd_algebra_493` | registered-valid | mathd algebra | 0 | 0 | 1 |
| `amc12a_2003_p25` | registered-valid | AMC | 2 | 0 | 3 |
| `amc12b_2021_p4` | miniF2F-test | AMC | 1 | 0 | 1 |
| `mathd_algebra_170` | miniF2F-test | mathd algebra | 2 | 0 | 2 |
| `mathd_numbertheory_234` | miniF2F-test | mathd number theory | 0 | 0 | 3 |

### C1-only pass@32 theorems

| Theorem | Dataset | Family | C0 correct | C1 correct | C3 correct |
|---|---|---|---:|---:|---:|
| `numbertheory_notequiv2i2jasqbsqdiv8` | miniF2F-test | number theory | 1 | 1 | 0 |
| `mathd_algebra_215` | miniF2F-test | mathd algebra | 0 | 1 | 0 |
| `mathd_algebra_313` | miniF2F-test | mathd algebra, complex | 1 | 6 | 0 |

### Significant within-theorem shift

The paired distributional result is strong:

- Mean C3 minus C1 correct tactic modes per theorem: +1.03
- Paired Wilcoxon: `p = 7.94e-15`
- Mean C3 minus C1 correct proposal count per theorem: -0.67
- Paired Wilcoxon: `p = 8.58e-11`

The largest mode gain occurs on theorems for which C0 already produced 17 to
31 correct proposals out of 32:

- Mean mode delta: +2.31 per theorem
- Paired Wilcoxon: `p = 1.29e-14`

The largest measured change is therefore broader proof coverage on theorems
that the policy can already solve.

### Robustness to proof representation and correct-count imbalance

The empirical pass@32 distributions show the expected head-to-tail tradeoff.
For draws without replacement from each theorem's 32-proposal sample, the
combined expected tactic-mode accumulation is:

| Draws per theorem | C1 modes | C3 modes | C3 versus C1 |
|---:|---:|---:|---:|
| 1 | 228.8 | 219.0 | -4.3% |
| 4 | 732.1 | 741.7 | +1.3% |
| 8 | 1,257.8 | 1,320.1 | +5.0% |
| 16 | 2,109.5 | 2,301.2 | +9.1% |
| 32 | 3,445.0 | 3,926.0 | +14.0% |

C3 therefore sacrifices probability mass at the one-draw head, crosses C1 by
four draws, and accumulates an increasingly broad sampled tail through 32.
These are finite-sample rarefaction estimates, not fresh pass@K runs; the
pending pass@128 evaluation tests whether the advantage continues beyond the
observed 32-proposal support.

The held-out diversity result persists after equalizing the number of correct
draws and after changing how proofs are grouped. Among the 209 theorems with
at least 16 correct proposals in C0, C1, and C3, rarefaction to exactly 16
correct draws gives 10.27 expected tactic modes for C3 and 9.14 for C1, a
paired mean increase of 1.13 modes or 12.4% (`p = 7.20e-15`). This rules out
the raw number of correct proposals as the explanation for the coverage gain;
C3 has fewer correct proposals than C1 in the full held-out sample.

The C3-over-C1 coverage direction is also positive at all six frozen
representations:

| Proof representation | C1 coverage | C3 coverage | C3 change | Paired p-value |
|---|---:|---:|---:|---:|
| First tactic head | 836 | 907 | +8.5% | `8.60e-4` |
| First two tactic heads | 2,125 | 2,381 | +12.0% | `4.12e-8` |
| Unordered head set | 2,813 | 3,167 | +12.6% | `2.07e-9` |
| Head multiset | 3,327 | 3,797 | +14.1% | `7.81e-15` |
| Ordered head sequence | 3,445 | 3,926 | +14.0% | `7.94e-15` |
| Exact normalized proof | 6,234 | 6,675 | +7.1% | `1.61e-12` |

The finding is therefore not specific to ordered tactic signatures. These
representations remain syntactic summaries, however, and are not evidence
that every counted item is a semantically distinct proof strategy. The frozen
pass@32 panel and source hashes are in
[`results/registered_c0_c1_c3_seed42_pass32_accumulation.json`](../results/registered_c0_c1_c3_seed42_pass32_accumulation.json).

## Deep pass@128 evaluation

All three conditions use the identical frozen 467-theorem panel, seed,
sampling configuration, 16-worker Lean verifier bound, and 59,776 registered
proposals. Padding remains in physical compute accounting but is excluded from
the registered 128-per-theorem panel.

| Metric, combined splits | C0 base | C1 GRPO | C3 hard block |
|---|---:|---:|---:|
| Registered proposals | 59,776 | 59,776 | 59,776 |
| Lean-correct proposals | 25,310 | **29,172** | 27,997 |
| Theorem/split pairs solved at 128 | 276 | 275 | **277** |
| Correct tactic modes | **11,477** | 8,468 | 10,444 |
| Exact correct proofs | 23,965 | 21,505 | **25,421** |
| Mean tactic modes per theorem | **24.58** | 18.13 | 22.36 |

C3 therefore retains essentially the same theorem-solving coverage as both C0
and C1 while moving probability mass from repeated correct proofs into a much
broader correct tail. Relative to C1, C3 has 4.0% fewer correct proposals but
23.3% more tactic modes and 18.2% more exact normalized proofs.

### Split-level pass@128

| Dataset | Metric | C0 | C1 | C3 |
|---|---|---:|---:|---:|
| miniF2F-test | pass@128 | **50.41%** | 49.59% | **50.41%** |
| miniF2F-test | solved | **123** | 121 | **123** |
| registered-valid | pass@128 | 68.61% | **69.06%** | **69.06%** |
| registered-valid | solved | 153 | **154** | **154** |

### Equal-correct-draw depth curve

Rarefaction within each theorem removes C3/C1 correctness-count imbalance.
The diversity advantage increases monotonically over the decision-relevant
tail:

| Correct draws per common theorem | C1 expected modes | C3 expected modes | C3 change | Paired p-value |
|---:|---:|---:|---:|---:|
| 8 | 5.36 | 5.88 | +9.7% | `6.01e-27` |
| 16 | 8.95 | 10.18 | +13.7% | `1.79e-29` |
| 32 | 14.77 | 17.29 | +17.1% | `3.20e-29` |
| 64 | 23.64 | 28.47 | +20.4% | `2.34e-27` |

At the full 128-proposal sample, C3 adds 4.23 tactic modes per theorem on
average (`p = 4.21e-32`), increases the mean Simpson effective-mode count by
4.76 (`p = 4.81e-30`), and lowers mean top-mode share by 0.064
(`p = 8.54e-22`). C3 has higher mode coverage on 224 theorems, C1 on 43, with
200 ties.

### Recovery relative to the base model

Ordinary GRPO suppresses many modes that are repeatedly visible under C0.
Among C0 modes absent from C1, C3 recovers:

- 502 of 1,170 modes seen at least twice under C0 (42.9%);
- 117 of 165 modes seen at least four times (70.9%); and
- 23 of 28 modes seen at least eight times (82.1%).

C3 still remains below C0's total tactic-mode coverage, so hard exclusion
substantially mitigates but does not eliminate policy collapse. At 16 correct
draws, C3 recovers about 54% of C1's expected-mode deficit relative to C0.

### Representation robustness at pass@128

The C3-over-C1 direction is positive at all six frozen syntactic resolutions:

| Proof representation | C1 coverage | C3 coverage | C3 change | Paired p-value |
|---|---:|---:|---:|---:|
| First tactic head | 1,118 | 1,249 | +11.7% | `2.87e-9` |
| First two tactic heads | 3,960 | 4,707 | +18.9% | `2.57e-20` |
| Unordered head set | 6,262 | 7,407 | +18.3% | `4.00e-24` |
| Head multiset | 7,993 | 9,771 | +22.2% | `6.96e-32` |
| Ordered head sequence | 8,468 | 10,444 | +23.3% | `4.21e-32` |
| Exact normalized proof | 21,505 | 25,421 | +18.2% | `7.22e-41` |

These findings support broader syntactic proof exploration, not semantic
mathematical-strategy diversity. The frozen artifacts and complete source
hashes are in
[`results/registered_c0_c1_c3_seed42_pass128.json`](../results/registered_c0_c1_c3_seed42_pass128.json)
and
[`results/registered_c0_c1_c3_seed42_pass128_accumulation.json`](../results/registered_c0_c1_c3_seed42_pass128_accumulation.json).

## Intermediate engineering and execution facts

- Upstream base-model inference and unchanged C1 engineering smoke completed
  before hard blocking was enabled.
- Focused mode/archive/blocking coverage passed 8 of 8 tests, including
  disabled-feature equivalence, unchanged incorrect advantages, zero blocked
  advantages, all-blocked skipping, and pristine restart enforcement.
- The first registered C0 evaluation attempt inherited a 256-GB node-memory
  ceiling, completed one batch, then suffered two OOM kills and an NCCL
  timeout. It is excluded. Full runs and evaluations used high-memory
  allocations.
- Full C3 completed 604 of 604 steps and saved its final actor checkpoint. The
  Slurm allocation later reached its 23-hour limit only because the launcher
  intentionally retained it with `sleep infinity`; the training payload was
  already complete.
- Full C1 and all evaluations completed inside a single 8-H100, 1.5-TB,
  23-hour workbench allocation. C1 and evaluation workloads used disjoint
  four-GPU halves.
- The upstream trainer intentionally ends completed sample-only and training
  runs with `Exception("Stop")`. Finalizers classify this only as success when
  the expected final proof snapshot and counts are present.
- The prepared evaluation launcher inherited unsupported `gae` worker
  initialization and stopped before sampling. D-033 records the repair:
  sample-only evaluation explicitly resolves `algorithm.adv_estimator=grpo`.
  This affects worker construction only; evaluation computes no advantages or
  optimizer updates. The operational launcher SHA-256 for all successful
  evaluations is
  `a4ebe495720dbf8b8be92f8d979d456c4398202fc04cbeaaae961409ab387b97`.
- Evaluation verifier-infrastructure failure counts were 133 for C0, 96 for
  C1, and 134 for C3 out of 14,944 registered proposals per condition. These
  failures remain in proposal accounting and were not silently rerun.

## Active discriminating experiments

1. Complete pristine blocking-disabled matched-control retry 3 (`872222`),
   which excludes only the two nodes rejected by pre-result runtime gates, with
   exactly C3's two PPO epochs, KL 0.10, data, seed, optimizer, and proposal
   budget; frozen training analysis `872223` and 16-worker held-out evaluation
   `872224` are dependency-bound to it.
2. Complete pristine C5 reward-rejection retry 5 (`872448`), which excludes
   only the three nodes rejected by pre-result runtime gates, then apply
   the frozen diversity/concentration/correctness decision rule against C3.
3. Choose any later experiment only from those two discriminating outcomes;
   do not add seeds, C2, or larger repeats merely to polish significance.

## Artifacts

- Registered comparison:
  [`results/registered_c0_c1_c3_seed42.json`](../results/registered_c0_c1_c3_seed42.json)
- Paired theorem analysis:
  [`results/theorem_selection_c1_vs_c3_seed42.json`](../results/theorem_selection_c1_vs_c3_seed42.json)
- Pass@32 accumulation and representation baseline:
  [`results/registered_c0_c1_c3_seed42_pass32_accumulation.json`](../results/registered_c0_c1_c3_seed42_pass32_accumulation.json)
- Pass@128 registered comparison:
  [`results/registered_c0_c1_c3_seed42_pass128.json`](../results/registered_c0_c1_c3_seed42_pass128.json)
- Pass@128 accumulation, rarefaction, recovery, and robustness panel:
  [`results/registered_c0_c1_c3_seed42_pass128_accumulation.json`](../results/registered_c0_c1_c3_seed42_pass128_accumulation.json)
- C0 cross-fit blocking analysis:
  [`results/c0_crossfit_blocking.json`](../results/c0_crossfit_blocking.json)
- Decision log: [`research/DECISIONS.md`](DECISIONS.md)
- Execution state: [`PROJECT_STATE.md`](../PROJECT_STATE.md)

Raw proof logs, checkpoints, resolved Hydra configs, hardware records, and
verifier traces remain under ignored `runs/` directories on cluster storage.
