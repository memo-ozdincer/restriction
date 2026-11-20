# A reusable proof procedure should survive training and compose at a new root

Prospective hypothesis: rewarding an exact proof body for working across several
training contexts will strengthen reusable procedures enough to solve new,
multi-premise composition tasks from an empty proof root. The desired result is
an actual complete proof, not a tactic-diversity score or an oracle prefix.

This is a new training track following D-126/D-127. The historical prefix and
dominant-mode experiments retain their original gates and conclusions. The
cross-context screen passed its reward-contrast gate in three families, but its
rewards match a short-proof ranking for 19 of 20 groups. That confound motivates
the length control below. No related-method survey is used to choose this test.

## Frozen comparison

- Initialize every actor and frozen reference from the pinned pristine
  DeepSeek-Prover-V1.5-SFT 7B bytes, revision
  `e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`.
- Collect one fresh batch: the same 20 training tasks, 16 samples each, seed
  20261120 plus a deterministic task hash, temperature 1, top-p 1, no top-k,
  256 response tokens. Save exact prompt/response token IDs and actual sampled
  token probabilities. Do not retokenize the old screen's decoded proofs.
- Execute each unchanged body in all four contexts in its training family.
  Retain the existing parser, Lean kernel, axiom audit and 60-second timeout.
  Cache only identical complete Lean sources. Unresolved rewards stop training.
- Four arms use identical trajectories, adapter initialization, task order,
  optimizer and candidate passes: local correctness; local correctness times
  the fraction of three peer successes; the same cross-reward multiset assigned
  to locally correct proofs in increasing sampled-token length order; and
  successful-proof replay using the local correctness weights.
- The first three arms use population-standardized group advantages and a
  response-token PPO objective with clip 0.2. Replay uses response-only weighted
  negative log likelihood. All use the same sampled k3 reference penalty with
  coefficient 0.02; this is not an exactly integrated KL divergence.
- LoRA rank 8, alpha 16, q/v projections, no dropout; adapter parameters float32,
  base float32; AdamW learning rate 1e-4, zero weight decay, gradient clip 1.
  Two epochs over all 20 groups produce exactly 40 steps and 640 candidate
  passes per arm. Constant-reward groups remain in the budget with zero actor
  advantage. Each sequence's response loss has equal weight within its group.
- Use one final checkpoint per arm, never evaluation-based checkpoint selection.
  This is one shared on-policy collection followed by two proximal epochs, not
  an online RL campaign run to convergence. Loss, gradients, clipping, sampled
  penalty, actual parameter changes and frozen-reference probes are recorded.

Transformers 4.40.1 SDPA supplies both sampling and training probabilities, with
temperature/top-k defaults explicitly overridden. All model computation uses float32 with TF32 disabled. Cached generation probabilities
must agree with full-sequence scoring to mean absolute 0.05 nats and maximum
0.5 nats per response before updates. Both vectors are archived. These tolerances
recognize bfloat16 execution differences; they do not turn a different sampling
policy into on-policy data. A fresh GenerationConfig excludes checkpoint-specific
sampling warpers. The closing fence can share a sampled token with trailing
characters: retain the full token in the trace and truncate only verifier text
at the fence, matching the established stop-string behavior.

## Evaluation and the concrete result we hope to see

Evaluate all five policies, including the pristine base, with the same HF backend
and seed 20261121 plus task hash, 16 samples per root and 512 response tokens.
No merging into bfloat16 weights: reload float32 adapters and check saved training
probes to maximum absolute 1e-4 nats first.

Every policy receives the 20 training roots for retention and 20 composition
roots. The latter comprise all 16 untouched October tasks (four schemas) plus
four freshly authored tasks (two schemas): paired predicates over binary and
ternary trees, and closure over Nat-by-Nat / List-by-Nat products. There are
640 proposals per policy, 3,200 total. All valid routes count. No extra prefix,
invariant, retrieval result, witness or requested tactic is supplied.

The exciting registered outcome requires all of:

1. Cross-context credit exceeds every trained control by at least 10 percentage
   points in composition sample success, macro-averaged over six schemas.
2. At least two composition roots have base 0/16, cross at least 4/16, and each
   trained control at most 1/16. Publish the actual accepted proofs.
3. Training-root retention loses no more than five macro-averaged percentage
   points versus base, and all evaluation verdicts are resolved.

Correlated variants are not independent discoveries. The four fresh tasks extend
an induction motif already used in training; this is controlled structural
composition, not unrestricted distribution shift or novel mathematics. The old
October authored witnesses are available only to CPU instrument validation;
their four rational namespace repairs are witness-only and pinned by hash.
Training does not consume evaluation tasks, sampled evaluation outputs or witnesses.

A local-control gain that matches length or replay is useful but does not support
distinct cross-context credit. A null outcome at this tiny update budget does not
prove the mechanism impossible. Do not resample to chase the threshold. A passing
outcome would motivate a harder follow-up, not establish a revolutionary paradigm.

## Execution and preservation

One bounded, two-hour, single-H100 allocation under `def-zhijing`, with a Python
keeper and manual SSH execution. The controller releases its own allocation on
completion or failure, reserving three minutes for shutdown. Complete source,
data/config hashes, exact traces, matrix, training metrics, small final adapters,
evaluation outputs and verdicts are publication artifacts. Large base weights
remain excluded. Frozen base files are hashed before loading; disabled-adapter
probes must remain bitwise identical after training. Final adapters are saved
without optimizer state, and are not advertised as exact optimizer resumptions.

The isolated hash-verified PEFT 0.10.0 overlay is used only for this runner. The
shared environment remains unchanged. CPU unit tests check reward matching,
incorrect-source gating, policy-gradient direction, clipping, response masking,
actual adapter updates, unchanged frozen reference and exact save/reload.

## Engineering amendment before any policy update

Attempt 1373078 failed collection on the twelfth task, shear_3: the mean
absolute discrepancy between cached generation and full-sequence scoring
exceeded 0.05 nats (reported maximum 0.3881, below the separate 0.5 maximum).
176 earlier trajectories were saved; the failed group was not written by that
version. No reward matrix, training update or evaluation was performed. The
controller cancelled its allocation after 9m36s. All available traces and logs
are preserved, including this publication gap for the failed group.

Before the replacement attempt, change the frozen base's compute dtype from
bfloat16 to float32 for collection, every arm and every evaluation. Keep TF32
disabled and retain both original probability tolerances. The checkpoint bytes,
tasks, seeds, objectives, budgets and outcome criteria are unchanged. This is
an engineering hypothesis that reducing arithmetic error will reconcile the two
probability paths; the next attempt must demonstrate it. The replacement batch
is not selected for proof success. Also persist every group's exact traces before
checking the gate, so a future numerical failure retains its diagnostic evidence.
