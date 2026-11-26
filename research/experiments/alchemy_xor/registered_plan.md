# Alchemy pilot: multi-output XOR synthesis

Registered before running. Hypothesis: native, target-independent random
circuit prefixes expose useful intermediate computations and produce a
better *frozen transferable* gate-efficiency policy than further ordinary
RL, even after ordinary competence. If all learning merely discovers
success faster, or frozen held-out cost is not improved, the stronger
hypothesis fails here.

## Environment and controls

- Independent full-rank five-input/five-output GF(2) maps uniformly sampled
  via rejection of uniformly drawn unordered output sets. No selection by
  cost, motif or intervention success. Fixed generator seed 20261127,
  256 training maps, 128 validation, 256 held-out; disjoint unordered maps.
- All nonzero 5-bit masks are legal symbolic wires. Start with five basis
  masks. Each action chooses a new nonzero XOR of two already available
  masks. Duplicate wires are quotiented out. Policy chooses result mask
  (state transition), legal operand pair selected uniformly; full DAG
  retained. Pair choice is not a learned strategy; structural diagnostics
  refer only to learned choices of new mask. Exact checker validates every
  gate and target set. Complete immediately on correctness with terminal
  reward 1+(20-L)/20, otherwise zero. L counts every gate, including
  prefix and unused gates. All arms have same 20-action total cap.
- Shared small stochastic linear actor with 17 generic per-action features:
  legality from native XOR operation, result membership in target set,
  candidate Hamming weight, number of valid parent pairs, available
  and missing-mask counts bucketed by XOR Hamming distance to candidate;
  plus count of missing-output masks made reachable using candidate and
  existing masks (native one-step action geometry, no solver). Same
  features in all arms, no process reward. Adam, batch-mean terminal
  REINFORCE, no oracle trajectory or output labels.
- Four paired seeds, 42..45. 64 proposals/update. 1200 common ordinary
  updates then competence gate: >=80% validation root success and
  mean reward greater than initialization. Fork shared weights/Adam
  state, same train map sequence, 1800 further updates. Ord root-only,
  uniform native random prefix, and same-depth on-policy prefix (frozen
  sampling during prefix, learning only from suffix). Prefix length
  uniform 0..8, charged against horizon; if accidentally completes
  target, record and exclude from update (no repeated prefix draw).
  Equal episode/padded primitive action slots; record actual native
  moves/policy calls/reset moves as well. Exposure is not a fair
  computational advantage if actual policy/transition budgets differ.
- Frozen held-out from empty root (8 rollouts per map), before and
  after continuation; no extra learning to test. Compare correctness,
  mean terminal reward, mean gate cost conditional on correctness, and
  motif statistics (shared intermediate gate used by >=2 distinct target
  output DAGs; cancellation ancestor whose support is not a subset of
  a downstream target output). Independently replay every evaluation
  gate. Compare motifs within identical gate-count bins; a motif rate
  alone cannot prove causality. Gate optimum not given to policy.
  No special target or selected successful cases. This is a pilot, not
  a novelty claim. No training if common competence fails.

Implementation smoke (three updates/arm, not scientific result) passed
concrete truth-vector replay; found and fixed a moved-from vector in
one-step reachability feature (preserve a fixed legal-result snapshot
before moving action records). No pilot outputs consulted for task
selection/tuning.
