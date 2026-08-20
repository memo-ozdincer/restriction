# Results

Commit only reviewed, compact summaries here. Raw generations, checkpoints,
verifier traces, and logs belong under the ignored `runs/` directory or in
cluster object storage.

Every summary must identify the git commit, model revision, dataset hashes,
seed, proposal budget, hardware, wall-clock time, archive checksum, and whether
the run was a smoke test or a registered result.

## Registered seed-42 artifacts

- [`registered_c0_c1_c3_seed42.json`](registered_c0_c1_c3_seed42.json): complete
  C0/C1/C3 training accounting, registered-valid and miniF2F-test pass@N,
  correct tactic-mode coverage, exact-proof coverage, and pairwise deltas.
- [`theorem_selection_c1_vs_c3_seed42.json`](theorem_selection_c1_vs_c3_seed42.json):
  paired C1/C3 theorem identities, exact McNemar tests, paired correct-count
  and mode-count tests, C0-difficulty strata, and exploratory theorem-family
  and numeric-domain strata.
- [`c0_crossfit_blocking.json`](c0_crossfit_blocking.json): frozen C0 cross-fit
  eligibility analysis for the separate exploratory C4 intervention.

The human-readable interpretation, provenance, intermediate execution facts,
and claim boundaries are in
[`research/RESULTS.md`](../research/RESULTS.md).
