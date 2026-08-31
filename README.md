# Restriction-RL

Restriction-RL is a hard dominant-mode blocking method for reinforcement
learning with verifiable rewards (RLVR) in Lean. It prevents a policy from
repeatedly learning from its most common verified proof pattern, then restarts
training from the base model so alternative correct behavior can receive the
learning signal.

## Results

Restriction-RL was evaluated with DeepSeek-Prover-V1.5-SFT on 9,655 Lean
theorems. Every training condition used 308,960 proposals and Lean as the
correctness verifier.

| Training condition | Correct tactic signatures | Exact correct proofs | pass@32 |
|---|---:|---:|---:|
| Base model | 73,635 | 133,898 | 80.63% |
| Standard GRPO | 34,336 | 66,515 | 82.15% |
| **Restriction-RL** | **53,825** | **111,570** | **83.67%** |

Compared with standard GRPO, Restriction-RL produced:

- **56.8% more distinct correct tactic signatures** during training;
- **67.7% more exact correct proofs** during training;
- **481 additional correct tactic signatures (+14.0%)** across 467 held-out
  theorems; and
- **273 held-out theorems at pass@32**, versus 271 for standard GRPO.

The distributional shift is strong within the same theorem population.
Restriction-RL produced 1.03 additional correct tactic signatures per held-out
theorem in the paired analysis (`p = 7.94e-15`). At an equalized sample of 16
correct held-out rollouts, it yielded 10.27 expected modes per eligible theorem
versus 9.14 for standard GRPO (`p = 7.20e-15`). Separately, the analogous
on-policy training comparison yielded 5.46 versus 3.64 expected modes.

Restriction-RL also resurfaced correct behavior that disappeared under GRPO.
Among base-model tactic signatures observed at least twice but absent from the
GRPO rollouts, **43.3%** appeared under Restriction-RL. For signatures observed
at least four times in the base distribution, recovery reached **58.8%**.

## How it works

1. Sample and Lean-verify proofs from the base policy.
2. Canonicalize each correct proof into a deterministic tactic signature.
3. Build a persistent archive and identify the dominant correct mode for each
   eligible theorem.
4. Restart the actor and reference from the pristine base checkpoint.
5. During RLVR, give blocked correct rollouts zero policy advantage while
   preserving the original treatment of incorrect and alternative correct
   rollouts.

Blocked proposals remain in physical compute accounting, and prompts with no
trainable alternative are skipped cleanly.

## Held-out evaluation

The final checkpoints were evaluated on two held-out Lean sets with 32 fresh
proposals per theorem:

| Dataset | Theorems | GRPO modes | Restriction-RL modes | GRPO solved | Restriction-RL solved |
|---|---:|---:|---:|---:|---:|
| Registered-valid | 223 | 2,233 | **2,477** | 152 | **154** |
| miniF2F-test | 244 | 1,212 | **1,449** | 119 | 119 |
| **Combined** | **467** | **3,445** | **3,926** | **271** | **273** |

Correctness is determined exclusively by Lean. A mode is a deterministic,
auditable tactic-signature representation of a proof.

## Implementation

The implementation includes:

- deterministic proof canonicalization and tactic signatures;
- a persistent dominance archive built from verified base-policy rollouts;
- hard exclusion integrated into rollout verification and advantage
  computation;
- pristine actor and reference restart enforcement;
- complete proposal, block, skip, verification, and training accounting; and
- behavioral tests for every blocking and disabled-feature path.

The main intervention points are in
`verl/trainer/ppo/ray_lean_trainer.py`, with Lean utilities in `verl/lean/` and
experiment launchers in `scripts/project/`.

## Explore the project

- [Complete findings and statistical analysis](research/RESULTS.md)
- [Machine-readable result artifacts](results/README.md)
- [Experiment specification](research/EXPERIMENT_PLAN.md)
- [Current project state](PROJECT_STATE.md)

## Current work

Fresh pass@128 evaluations of the base, GRPO, and Restriction-RL checkpoints
will measure mode accumulation at larger sampling budgets. A full
blocking-disabled control matched to Restriction-RL's optimizer and KL settings
will test whether the observed diversity gain is caused by blocking. Together,
these results will choose among replication, mechanism diagnosis, a refined
blocking intervention, or a proof workload with richer variation.
