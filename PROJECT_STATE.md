# Project State

Last updated: 2026-08-14

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

- [x] Provision the Lean/veRL environment on the cluster.
- [x] Provisioned `.venv-legacy` with the historical Torch/Transformers/vLLM/
  Ray/TensorDict stack; freeze recorded in `research/legacy-env-freeze.txt`.
- [x] Reused the tested PRIME GPU venv under `/scratch/memoozd/rl/prime-rl`;
  added a scratch-local setup script and removed the hard-coded verifier path.
- [x] Added deterministic proof-mode signatures and a persistent dominance
  archive format with unit-test coverage; the completed C0 archive is now
  frozen and checksummed.
- [x] Added a guarded fresh-C0 initializer and launcher. It persists periodic
  proof snapshots and refuses an existing run directory.
- [x] Added disabled-feature, blocked-advantage, all-blocked prompt, and
  pristine-restart unit coverage; run with
  `python -m unittest tests.test_proof_modes -v` in `.venv-legacy`.
- [x] Documented the scratch bootstrap attempt and current blockers in
  `research/CLUSTER_BOOTSTRAP.md`.
- [x] Record exact cluster hardware and software versions.
- [x] Validated legacy veRL imports and recorded the four-H100 cluster plus
  Lean/Lake versions in the bootstrap notes.
- [x] Fetched and built DeepSeek `REPL`; revision and build evidence are in
  `research/CLUSTER_BOOTSTRAP.md`, and direct Lean acceptance is verified.
- [x] Complete the one-time local build of the pinned DeepSeek Mathlib
  workspace; its upstream cache has no artifacts for this revision. This was
  environment provisioning, not experiment time.
- [x] Run unchanged base-model inference on a one-row deterministic smoke
  slice. The completed run is
  `runs/base-inference-smoke-20260717-vllm042-torch230/`; it generated,
  parsed, and Lean-verified proposals from the pristine DeepSeek base model.
  This is an environment gate, not a C0 metric.
- [x] Reproduce one unchanged GRPO smoke run.
- [x] Added a guarded one-update C1 GRPO-Default smoke preparer and launcher;
  D-028 fixes its deterministic 16-theorem engineering slice and accounting.
- [x] Completed the checksummed C0 16/16 cross-fit safety analysis and
  registered the floor-2 `StableTopBlock-Restart` C4 ablation in D-029;
  C3 remains the primary intervention.
- [x] Completed the one-update C1 GRPO-Default engineering smoke on allocation
  `19060059`; the actor checkpoint, proof snapshot, and resolved config are
  durable under `runs/c1-grpo-default-smoke-20260814-seed42/`. The Slurm step's
  nonzero exit is the upstream post-completion `Exception("Stop")` sentinel.
- [x] Added proposal-level hard-block decisions and required C3 counters before
  the first hard-block smoke; D-030 records the observational-only change.
- [x] Completed the one-update C3 HardBlock-Restart engineering smoke from the
  pristine base model. It blocked 38 correct dominant-mode proposals, skipped
  zero all-blocked prompts, completed one actor update, and saved its checkpoint
  and proof snapshot under
  `runs/c3-hardblock-restart-smoke-20260814-seed42-retry1/`.
- [x] Finalized auditable C1/C3 smoke metrics and reran the focused proof-mode
  and hard-blocking suite after the object-array mask correction: 8/8 tests
  passed.
- [x] Completed and independently validated C0 over all 9,655 registered train
  theorems and 308,960 scientific proposals. The four checksummed source
  snapshots, validation manifest, metrics, and frozen archive are under
  `runs/c0-base-20260804-seed42-complete/`. Physical accounting includes 32
  additional dataloader-padding proposals, reported and excluded.
- [x] Added observational per-proposal telemetry for future proof snapshots:
  deterministic identities/hashes, token count, parse/queue/verification
  latency, verdict/failure/timeout fields, worker ID, tactic-prefix signature,
  and resolved config/environment hashes. Historical per-proof latency is not
  reconstructed or rerun.
- [x] Created and froze the C0 dominance archive; SHA-256
  `fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3`.
- [x] Implement hard blocking behind a configuration flag.
- [x] Run unit tests and disabled-feature equivalence tests.
- [ ] Execute C1-C3; C0 is complete.
- [ ] Analyze pass@N, correct mode coverage, and compute-normalized discovery.

Bootstrap note: the legacy environment, Ray, Lean, Lake, REPL build, and
verifier acceptance work. C0 is complete; C1 remains open. C0 was sample-only:
no optimizer update or checkpoint was produced.

Current execution note: C1 and C3 engineering smokes are complete. The next
scientific run is full registered C3 from the pristine base model on all 9,655
training theorems, followed by held-out evaluation.

C0 result: 168,029/308,960 proposals were Lean-correct, and 7,785/9,655
theorems were solved at pass@32. Pass@1/4/8/16/32 are respectively
0.543854/0.712348/0.752076/0.782069/0.806318. The archive contains 73,635
correct tactic-signature modes and 133,898 exact normalized proofs. These are
operational tactic signatures, not claims of semantic strategy diversity.

C0 used node-local `/tmp` only for a disposable verifier workspace. All
authoritative proofs, logs, resolved configurations, checksums, metrics, and
the archive are durable under shared `/scratch`. See D-022 through D-027 for
the interrupted-partition and padding accounting decisions.
An independently checksummed compressed copy is also under
`/home/memoozd/c0-archives/` (SHA-256
`300ba7b441433aa0676a2e2df5851a7aa51beca2afcaa93d7ab17c59f6edda70`).

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
