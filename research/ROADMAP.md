# Research Roadmap

## Completed foundation

Restriction-RL now has an end-to-end Lean RLVR implementation with:

- deterministic tactic-signature canonicalization;
- a persistent, checksummed dominance archive;
- hard blocking in rollout verification and advantage computation;
- enforced actor and reference restart from the base checkpoint;
- explicit proposal, verification, blocking, skipping, and update accounting;
- full base, standard-GRPO, and Restriction-RL training runs; and
- held-out evaluation with paired theorem-level analysis.

The completed comparison shows that Restriction-RL substantially preserves
correct proof-mode coverage relative to standard GRPO at matched proposal
budgets.

## Active experiments

### Pass@128 accumulation

Evaluate the base, standard-GRPO, and Restriction-RL checkpoints with 128 fresh
proposals per theorem. Measure:

- pass@1 through pass@128;
- exact correct proofs and tactic signatures;
- mode accumulation as sampling increases;
- top-mode concentration and effective mode count; and
- recovery of base-model modes suppressed by standard GRPO.

This directly tests whether Restriction-RL's broader distribution continues to
surface useful alternatives at larger sampling budgets.

### C3-matched blocking control

Run the Restriction-RL training configuration from the same pristine base with
blocking disabled while matching two PPO epochs, KL 0.10, data, prompts,
optimizer, seed, and the 308,960-proposal budget. This is the required causal
control for separating blocking from the optimizer differences between C1 and
C3. Evaluate the final control checkpoint on the same frozen held-out set.

## Candidate follow-ups

### StableTopBlock-Restart

Use the registered cross-fitted archive to block only dominant modes that are
stable across discovery folds. This focuses the intervention on repeatable
dominance and reduces sensitivity to finite-sample top-mode selection.

### Mode-likelihood dynamics

Measure base-to-final likelihood changes for dominant, recovered, and newly
observed correct modes. This connects rollout-level diversity to the policy's
probability redistribution rather than relying only on sampled counts.

### Broader proof workloads

Evaluate Restriction-RL on workloads where multiple correct proof families are
common, including proof repair and longer verifier-guided trajectories. These
settings provide a natural test of whether dominant-mode blocking preserves
useful alternatives beyond whole-proof theorem sampling.

## Decision rule

Use the matched control for causal attribution and pass@128 for tail behavior:

1. If C3 beats the matched control by at least 10% in training mode coverage,
   has positive equal-correct-draw rarefaction, and retains a held-out
   advantage, treat blocking as materially supported at seed 42. Prefer a
   replication before a strong general claim; use the tail curve and mechanism
   evidence to decide whether StableTopBlock-Restart is also informative.
2. If C3 and the control are within the registered 5% practical-null band, do
   not make blocking the explanation. Use the smallest optimizer or
   likelihood diagnostic that can locate the source of the C1/C3 difference.
3. If the control matches or exceeds C3, treat the current blocking attribution
   as falsified and diagnose before scaling a stronger blocking intervention.
4. Independently, if the mode gap saturates quickly by pass@128, move toward a
   workload with richer within-problem proof variation rather than spending
   the next allocation on more samples of the same benchmark.
