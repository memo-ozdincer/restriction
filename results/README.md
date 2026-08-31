# Results

Commit only reviewed, compact summaries here. Raw generations, checkpoints,
verifier traces, and logs belong under the ignored `runs/` directory or in
cluster object storage.

Every summary records the git commit, model revision, dataset hashes, seed,
proposal budget, hardware, wall-clock time, archive checksum, and run type.

## Experiment artifacts

- [`registered_c0_c1_c3_seed42.json`](registered_c0_c1_c3_seed42.json): complete
  C0/C1/C3 training accounting, registered-valid and miniF2F-test pass@N,
  correct tactic-mode coverage, exact-proof coverage, and pairwise deltas.
- [`theorem_selection_c1_vs_c3_seed42.json`](theorem_selection_c1_vs_c3_seed42.json):
  paired C1/C3 theorem identities, exact McNemar tests, paired correct-count
  and mode-count tests, C0-difficulty strata, and exploratory theorem-family
  and numeric-domain strata.
- [`training_dynamics_c1_vs_c3_seed42.json`](training_dynamics_c1_vs_c3_seed42.json):
  100-step C1/C3 mode-collapse trajectories, correct-rollout rarefaction,
  concentration metrics, and finite-sample recovery of C0 modes absent from C1.
- [`registered_c0_c1_c3_seed42_pass32_accumulation.json`](registered_c0_c1_c3_seed42_pass32_accumulation.json):
  frozen pass@32 accumulation baseline, held-out correct-draw rarefaction,
  concentration, C0-mode recovery, and proof-representation robustness panel.
- [`c0_crossfit_blocking.json`](c0_crossfit_blocking.json): frozen C0 cross-fit
  eligibility analysis for the separate exploratory C4 intervention.

The human-readable findings, provenance, intermediate execution facts, and
statistical analyses are in
[`research/RESULTS.md`](../research/RESULTS.md).
