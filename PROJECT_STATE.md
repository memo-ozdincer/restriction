# Project State

Last updated: 2026-07-18

## Completed

- [x] Forked the official Rewarding the Unlikely repository.
- [x] Pinned upstream commit
  `ca1cff05ebdf2cfe9737fd416897da838a93e11a`.
- [x] Preserved upstream as the `upstream` git remote.
- [x] Added arXiv paper version 2 and its checksum.
- [x] Archived the two earlier papers, literature search, and original
  governing memo with checksums.
- [x] Recorded the thesis, experimental contract, model choice, compute plan,
  staged roadmap, risks, and cluster handoff.

## Next

- [ ] Provision the Lean/veRL environment on the cluster.
- [ ] Record exact cluster hardware and software versions.
- [ ] Run unchanged base-model inference on a small data slice.
- [ ] Reproduce one unchanged GRPO smoke run.
- [ ] Implement deterministic proof-mode signatures.
- [ ] Create and freeze the dominance archive.
- [ ] Implement hard blocking behind a configuration flag.
- [ ] Run unit tests and disabled-feature equivalence tests.
- [ ] Execute C0-C3.
- [ ] Analyze pass@N, correct mode coverage, and compute-normalized discovery.

## Known blockers and ambiguities

- The paper describes a 10K training subset for the main analysis and an 11K
  large-scale experiment, while the checked-in launcher currently defaults to
  `data/mff-lwb-goedel-28k.parquet`.
- The released launcher is configured as the paper's
  GRPO-Unlikeliness-2-style condition (`ppo_epochs=2`, KL `0.10`, rank penalty
  `0.25`), not GRPO-Default.
- The paper reports exact unique proof strings, not a semantic taxonomy of Lean
  strategies. Our tactic/lemma signature is an operational proxy and must be
  labeled as such.
- The upstream repository does not include the paper's toy-environment code.

Resolve these explicitly in `research/DECISIONS.md`.
