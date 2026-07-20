# Project State

Last updated: 2026-07-19

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
- [x] Provisioned `.venv-legacy` with the historical Torch/Transformers/vLLM/
  Ray/TensorDict stack; freeze recorded in `research/legacy-env-freeze.txt`.
- [x] Reused the tested PRIME GPU venv under `/scratch/memoozd/rl/prime-rl`;
  added a scratch-local setup script and removed the hard-coded verifier path.
- [x] Added deterministic proof-mode signatures and a persistent dominance
  archive format with unit-test coverage; the archive cannot be populated or
  frozen until completed C0 proof logs exist.
- [x] Added a guarded fresh-C0 initializer and launcher. It persists periodic
  proof snapshots and refuses an existing run directory.
- [x] Added disabled-feature, blocked-advantage, all-blocked prompt, and
  pristine-restart unit coverage; run with
  `python -m unittest tests.test_proof_modes -v` in `.venv-legacy`.
- [x] Documented the scratch bootstrap attempt and current blockers in
  `research/CLUSTER_BOOTSTRAP.md`.
- [ ] Record exact cluster hardware and software versions.
- [x] Validated legacy veRL imports and recorded the four-H100 cluster plus
  Lean/Lake versions in the bootstrap notes.
- [x] Fetched and built DeepSeek `REPL`; revision and build evidence are in
  `research/CLUSTER_BOOTSTRAP.md`. One proof verification remains.
- [x] Complete the one-time local build of the pinned DeepSeek Mathlib
  workspace; its upstream cache has no artifacts for this revision. This was
  environment provisioning, not experiment time.
- [x] Run unchanged base-model inference on a one-row deterministic smoke
  slice. The completed run is
  `runs/base-inference-smoke-20260717-vllm042-torch230/`; it generated,
  parsed, and Lean-verified proposals from the pristine DeepSeek base model.
  This is an environment gate, not a C0 metric.
- [ ] Reproduce one unchanged GRPO smoke run.
- [ ] C0 frozen-base rollout is not complete. The registered 9,655-row run in
  `runs/c0-base-20260717-grpo-default/` was interrupted at the user's request
  during model initialization, before rollout artifacts or C0 metrics existed.
  It must be restarted in a fresh run directory on a later allocation.
- [ ] Create and freeze the dominance archive.
- [x] Implement hard blocking behind a configuration flag.
- [x] Run unit tests and disabled-feature equivalence tests.
- [ ] Execute C0-C3.
- [ ] Analyze pass@N, correct mode coverage, and compute-normalized discovery.

Bootstrap note: the legacy environment, Ray, Lean, Lake, REPL build, and
verifier acceptance now work. The one-row base-inference gate completed; C0
and C1 remain open. No C0/C1 training or evaluation metric has been claimed.

Compute note: the current login host has no usable NVIDIA driver, so the
fresh C0 must be started on the requested GPU allocation. Prepare with
`scripts/project/prepare_c0_run.py <new-run-dir>` and launch with
`scripts/project/launch_c0.sh <new-run-dir>`.

Current C0 diagnostic: the first fresh run on `g28` was NFS-bound in Lean
verification despite all four GPUs being active. A fresh node-local-verifier
restart is required; see D-022 before interpreting any partial C0 snapshot.
The restarted C0 uses the same verifier workspace staged to node-local tmpfs;
its first five batches took 63--80 seconds rather than the NFS-bound
169--211 seconds. Only the disposable verifier copy is in `/tmp`; every run
artifact remains under `runs/` on scratch.

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
