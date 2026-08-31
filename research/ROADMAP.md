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

## Active experiment: pass@128

Evaluate the base, standard-GRPO, and Restriction-RL checkpoints with 128 fresh
proposals per theorem. Measure:

- pass@1 through pass@128;
- exact correct proofs and tactic signatures;
- mode accumulation as sampling increases;
- top-mode concentration and effective mode count; and
- recovery of base-model modes suppressed by standard GRPO.

This directly tests whether Restriction-RL's broader distribution continues to
surface useful alternatives at larger sampling budgets.

## Next training experiments

### StableTopBlock-Restart

Use the registered cross-fitted archive to block only dominant modes that are
stable across discovery folds. This focuses the intervention on repeatable
dominance and reduces sensitivity to finite-sample top-mode selection.

### Matched blocking ablation

Run the Restriction-RL training configuration with blocking disabled. This
isolates the contribution of the blocklist while matching optimizer and KL
settings.

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

Use the pass@128 accumulation curves to choose the next run:

1. If the coverage gap grows with sampling, prioritize StableTopBlock-Restart.
2. If the gap is stable but operationally meaningful, run the matched blocking
   ablation and mode-likelihood analysis.
3. If the gap saturates quickly, move to a workload with richer within-problem
   proof variation before scaling the same experiment.
