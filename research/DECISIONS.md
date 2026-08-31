# Decision Log

Record decisions before running the affected experiment.

## D-001 - Repository base

- Date: 2026-07-18
- Decision: use official repository commit
  `ca1cff05ebdf2cfe9737fd416897da838a93e11a`.
- Reason: preserve a reviewable causal diff from the paper implementation.

## D-002 - Primary model

- Date: 2026-07-18
- Decision: use `deepseek-ai/DeepSeek-Prover-V1.5-SFT` for actor and reference
  initialization.
- Reason: exact paper model; changing it would confound the comparison.

## D-003 - Mode detector

- Date: 2026-07-18
- Decision: deterministic tactic/lemma signature, plus exact normalized proof
  hash as a secondary identity.
- Reason: no learned judge, repeatable enforcement, and auditability.
- Risk: this remains a proxy for mathematical strategy.

## D-004 - Blocking threshold

- Date: 2026-07-18
- Decision: dominant share must be greater than 0.50 with at least 4 verified
  correct proposals.
- Reason: simple majority rule and a minimum evidence guardrail.

## D-005 - Compute accounting

- Date: 2026-07-18
- Decision: blocked proposals consume the fixed proposal budget and are not
  resampled for free.
- Reason: avoid giving the intervention extra inference compute.

## D-006 - Track order

- Date: 2026-07-18
- Decision: test the mechanism in the Rewarding the Unlikely Lean/GRPO
  implementation, then open a Rewarding the Rare implementation, and defer STP
  until the small controlled experiment is interpretable.
- Reason: the first implementation supplies deterministic verification, a
  narrow code seam, and the same DeepSeek-Prover base used by STP without
  requiring STP's conjecturer and large iterative data pipeline.

## Open decisions

### Dataset identity

Verify which checked-in parquet files reproduce the paper's 10K main analysis
and approximately 11K final experiment. Record row counts, content hashes, and
the selected primary split here.

### Exact model revision

Resolved from the local Hugging Face cache:

```text
e9a6e6fbb67620d4e9c4944bc51ff7c435af12da
```

### Cluster compatibility patches

List every required environment or compatibility patch. Keep them separate
from the algorithmic commit where possible.

### D-007 - Scratch-local cluster environment

- Date: 2026-07-18
- Decision: reuse `/scratch/memoozd/rl/prime-rl/.venv` as the GPU environment,
  add only Ray, and keep the verifier checkout and uv cache under `/scratch`.
- Reason: this is the tested cluster CUDA/Torch/Transformers/vLLM stack from
  `../Nowak-coordination`; rebuilding it would be slower and less reliable.
- Compatibility note: this repository's historical pins (`transformers<4.48`,
  `vllm<=0.6.3`) are not re-resolved into the shared venv. The choice is an
  environment reuse expedient and must be validated by the unchanged inference
  smoke before any intervention results are trusted.

### D-008 - Bootstrap status and failed shared-venv repair

- Date: 2026-07-17
- Decision: do not claim C0/C1 until Ray and the historical veRL dependency
  stack pass import, verifier, and inference smoke tests.
- Evidence: the shared PRIME venv has the newer Torch/Transformers/vLLM stack,
  but Ray became an incomplete/mixed install during repair and `tensordict` is
  absent. Lean and Lake are now installed under scratch.
- Consequence: the bootstrap record is documented in
  `research/CLUSTER_BOOTSTRAP.md`; no experiment metrics are entered.

### D-009 - Legacy environment and REPL completion

- Date: 2026-07-17
- Decision: use the separately provisioned `.venv-legacy` for this veRL
  release and leave PRIME-RL's environment untouched.
- Evidence: the frozen legacy stack imports successfully; DeepSeek's REPL
  dependency builds successfully at revision
  `c6199a81de2a7e16cb27d6f85f56cff7043cd27f`.
- Consequence: environment setup is complete and the next gate is one Lean
  verifier acceptance test. C0/C1 remain unrun and unreported.

### D-010 - Upstream verifier runtime paths

- Date: 2026-07-17
- Decision: run the unchanged DeepSeek verifier process with
  `HOME=/scratch/memoozd` and its current working directory set to
  `/scratch/memoozd/rl/DeepSeek-Prover-V1.5`.
- Reason: upstream `prover.lean.verifier` resolves Lake as
  `$HOME/.elan/bin/lake` and the Lean workspace as the relative `mathlib4/`.
  The cluster installation instead uses `/scratch/memoozd/.elan` and the
  `mathlib4` checkout resides in the DeepSeek repository. Neither mismatch is
  an algorithmic choice, so this preserves verifier source and semantics.
- Consequence: do not modify the Lean verifier or create a workspace symlink
  in this repository. Launch baseline inference from the DeepSeek checkout
  with `PYTHONPATH` including this checkout.

### D-011 - Pinned Mathlib build artifacts

- Date: 2026-07-17
- Decision: retrieve the cache for the already pinned DeepSeek `mathlib4`
  revision with `lake exe cache get` before verifier or inference runs.
- Reason: the checkout contains neither `.lake/build/lib/lean/Mathlib` nor
  compiled imports; consequently even the upstream verifier's `import Mathlib`
  fails. `lake build REPL` builds only REPL and does not provide Mathlib's
  artifacts.
- Consequence: this is dependency provisioning, not a source or verifier
  change. Record the resulting revision in the bootstrap evidence.

### D-012 - Cache lookup after the REPL update

- Date: 2026-07-17
- Decision: preserve the DeepSeek checkout's dirty `lake-manifest.json` and
  retrieve any upstream Mathlib cache only from a disposable clean worktree at
  the same source revision.
- Reason: `lake update REPL` changed only REPL's resolved commit from
  `3334a97b268ecc67beb36a75787f7e831208a724` to
  `c6199a81de2a7e16cb27d6f85f56cff7043cd27f`. The cache service rejects the
  resulting dirty manifest (0 of 4650 artifacts available), while changing it
  back would discard an existing environment repair.
- Consequence: do not reset or checkout the user's DeepSeek worktree. If a
  clean worktree cache is compatible, copy only the generated build artifacts;
  otherwise build the pinned dirty workspace and report the extra provisioning
  time separately from experiment time.

### D-013 - No cache for the pinned Mathlib source revision

- Date: 2026-07-17
- Decision: build the pinned DeepSeek Mathlib workspace locally before the
  baseline gate.
- Evidence: a clean disposable worktree at
  `2f65ba7f1a9144b20c8e7358513548e317d26de1` also resolved 0 of 4650 cache
  artifacts, so the issue is not the dirty REPL manifest.
- Reason: retaining DeepSeek-Prover-V1.5-SFT is required for the primary
  experiment. Substituting Qwen would be a separate, non-comparable control.
- Consequence: record build wall-clock time as environment provisioning, never
  as experiment time, and do not start C0 or C1 until verifier acceptance
  succeeds.

### D-014 - Base-inference smoke scope

- Date: 2026-07-17
- Decision: use a deterministic one-row derivative of
  `data/mff-lwb-10k-seen.parquet` for the base-model smoke, with the upstream
  proposal count, prompt, verifier, model, and sampling settings unchanged.
- Reason: this gate checks model loading, generation, proof parsing, and Lean
  verification; it is not a C0 result. Limiting only the number of prompts
  prevents a baseline smoke from becoming an unreported training run.
- Consequence: enable the existing `trainer.sample_only` path and stop after
  its one generated batch. The derivative's path and checksum must be saved in
  the smoke run directory and never used for C0/C3 analysis.

### D-015 - vLLM compatibility correction

- Date: 2026-07-17
- Decision: replace legacy-environment `vllm==0.4.1` with the repository-supported
  `vllm==0.4.2` wheel without changing the repository's vLLM adapter.
- Evidence: the base-inference smoke reached the worker import and stopped
  before model loading because `verl.third_party.vllm` explicitly supports
  0.3.1, 0.4.2, 0.5.4, and 0.6.3, but not 0.4.1.
- Reason: 0.4.2 is the nearest explicitly supported release; the correction is
  confined to the legacy environment and does not alter the algorithm,
  verifier, data, model, or sampling settings.
- Consequence: refresh `research/legacy-env-freeze.txt` after installation and
  rerun the identical one-row smoke from a fresh Ray process.

### D-016 - FlashAttention runtime dependency

- Date: 2026-07-17
- Decision: install the FlashAttention extension compatible with the legacy
  Torch/CUDA environment before rerunning the base-inference smoke.
- Evidence: after vLLM compatibility passed, the unchanged FSDP actor import
  stopped at `from flash_attn.bert_padding import ...`; no model weights or
  rollouts were initialized.
- Reason: this is a direct runtime dependency of the upstream actor path, not
  an experimental factor. It was deliberately absent from the initial login
  node freeze pending confirmation that the legacy run required it.
- Consequence: pin the resolved package in `research/legacy-env-freeze.txt`.
  The smoke must restart in a new run directory; no failed attempt is counted
  as a baseline result.

### D-017 - Supported Torch/vLLM binary pair

- Date: 2026-07-17
- Decision: align the legacy environment to vLLM 0.4.2's declared Torch 2.3.0
  binary dependency and replace FlashAttention with the matching prebuilt
  wheel.
- Evidence: vLLM 0.4.2 metadata requires `torch==2.3.0`; the legacy Torch
  2.2.1 build leaves vLLM's `_C` extension with unresolved
  `c10::cuda::ExchangeDevice(signed char)`. This occurs during vLLM GPU
  profiling after the DeepSeek weights load, not in trainer logic.
- Reason: vLLM's compiled extensions require an ABI-matched Torch release.
  Changing source adapters to accept 0.4.1 would not repair that ABI mismatch.
- Consequence: this is the final environment compatibility correction. Verify
  the legacy veRL imports after the upgrade and refresh the complete freeze
  before restarting the smoke in a new directory.

### D-018 - Registered 10K-split C0 data

- Date: 2026-07-17
- Decision: use `data/mff-lwb-10k-seen.parquet` for the registered C0/C1
  ladder, respecting its checked-in `split` column: 9,655 `train` rows and
  223 `valid` rows. Save immutable derived parquet files and SHA-256 values in
  each run directory.
- Evidence: the paper reports approximately 9,600 Dtrain and 200 Dval
  problems, whereas the checked-in paper-associated file has 9,878 rows with
  the above explicit labels. The repository contains no alternate 9,600/200
  source or split manifest.
- Reason: the explicit checked-in split labels are the least-assumptive,
  auditable choice. The 28K file is reserved for the separately described
  larger-scale condition until its 11K relation is resolved.
- Consequence: label C0/C1 as reproduction attempts against this registered
  split, not exact numerical reproductions of the paper's unpublished
  9,600/200 partition.

### D-019 - Resolved base-model revision

- Date: 2026-07-17
- Decision: pin the local cache's `main` reference for
  `deepseek-ai/DeepSeek-Prover-V1.5-SFT` at
  `e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`.
- Evidence: `/home/memoozd/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-Prover-V1.5-SFT/refs/main`.
- Consequence: record this revision in all C0-C3 run metadata.

### D-020 - Cancel incomplete C0 allocation without treating it as data

- Date: 2026-07-17
- Decision: terminate Slurm allocation `17895062` at the user's request after
  preserving its logs and configuration. Mark
  `runs/c0-base-20260717-grpo-default/` as interrupted, not failed or
  completed.
- Evidence: the run directory contains the immutable split derivatives, launch
  script, resolved Hydra configuration, and initialization log, but no proof
  JSONL or completed rollout batch.
- Reason: the allocation must not continue unattended. An incomplete
  initialization has no valid C0 statistic, archive contribution, or training
  sample count.
- Consequence: do not resume this directory as C0. On a new allocation start a
  fresh C0 directory from the exact base checkpoint and retain this directory
  solely as an auditable interrupted-run record.

### D-021 - Reconcile interrupted C0 transient batch

- Date: 2026-07-19
- Decision: retain `runs/c0-base-20260717-grpo-default/` as interrupted and
  exclude it from all C0 metrics and archive construction.
- Evidence: its `run.log` contains one completed sample-only batch (512
  accepted proposals and 187 verifier errors), contradicting the earlier
  statement that no batch completed. It contains no persisted proof JSONL,
  checkpoint, final counts, or immutable archive input.
- Consequence: describe the run accurately as a partial transient batch with
  no auditable rollout artifact. Never use its console metrics, transient
  proofs, or initialization state as C0 evidence.

### D-022 - Node-local DeepSeek verifier workspace for C0

- Date: 2026-07-20
- Decision: stage the existing DeepSeek-Prover-V1.5 workspace, including its
  pinned Mathlib build artifacts, from `/scratch` to a fresh node-local `/tmp`
  directory before the fresh C0 restart.
- Evidence: the active C0's 64 `repl` verifier processes were predominantly in
  uninterruptible `rpc_wait_bit_killable` NFS wait; `/scratch` was 94% full,
  whereas node-local `/tmp` had approximately 1 TB free. GPU generation was
  only about 8--10 seconds per batch, while Lean verification took roughly
  170--200 seconds. With the identical workspace staged to `/tmp`, the first
  five C0 batches took 63--80 seconds each (approximately 54--71 seconds in
  Lean verification), a 2.4--3x end-to-end improvement.
- Reason: this changes filesystem locality only. It copies the same verifier
  source, pinned Mathlib workspace, model, prompts, samples, and Lean
  semantics; it does not alter the experiment's algorithmic factor.
- Consequence: retain the NFS-bound C0 directory solely as an interrupted
  diagnostic record. The registered C0 restarts in a new directory from the
  pristine base model with the staged verifier path recorded in its metadata.
  `/tmp` contains no authoritative experiment artifact: resolved config, logs,
  proof snapshots, metrics, metadata, and the eventual archive are persisted
  under `/scratch/memoozd/rl/restriction/runs/` before allocation teardown.

### D-023 - Remove the artificial per-worker Lean address-space bottleneck

- Date: 2026-07-21
- Decision: retain the upstream DeepSeek verifier and Lean semantics, but make
  its process address-space limit configurable and set it to 32 GB for future
  full C0--C3 runs on the 1-TB allocation.
- Evidence: the node had approximately 1.8 TiB available memory when C0
  stalled after step 156.  The DeepSeek wrapper nevertheless passed
  `memory_limit=10` to every `Lean4ServerProcess`.  One worker then raised
  `MemoryError` while serializing its verifier result through the Python
  multiprocessing manager; the upstream scheduler has no worker-failure
  recovery path, so the trainer waited indefinitely with all GPUs idle.
- Reason: the 10-GB `RLIMIT_AS` is a runtime resource ceiling, not part of the
  model, data, prompt, sampling, Lean correctness condition, or intervention.
  Raising it prevents an infrastructure-only false failure while leaving Lean
  acceptance unchanged.  A result that cannot be serialized is still never
  accepted as correct.
- Consequence: the individual deadlocked batch (steps 151--156) is excluded,
  but the durable `global_step_150.jsonl` contains exactly 32 completed
  rollouts for each of 2,400 unique training theorems.  Continue C0 over the
  disjoint remaining 7,255 theorem rows from the same pristine base, then
  merge the two proof logs only after verifying 32 proposals per theorem.
  Record `DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB=32` and the compact result-handoff
  patch in the continuation metadata.  This preserves the registered model,
  split, proposal budget, and Lean correctness condition without discarding
  completed compute.

### D-024 - Continuation launcher path resolution

- Date: 2026-07-21
- Decision: resolve every C0 run directory to an absolute path before changing
  into the node-local DeepSeek verifier workspace.
- Evidence: the first continuation start used a relative run path. After the
  launcher changed directory to `/tmp/.../DeepSeek-Prover-V1.5-c0-local`, Ray
  could not open `runs/.../train.parquet` and exited during dataloader setup.
  It produced no rollout, verifier result, or proof snapshot.
- Consequence: `launch_c0.sh` now canonicalizes its input path. The prepared
  continuation directory remains fresh and can be launched on the next GPU
  allocation; this failed start is excluded from all C0 accounting.

### D-025 - Final C0 persistence and dataloader padding accounting

- Date: 2026-08-04
- Decision: stop the active final continuation after its durable step-60
  snapshot, run the remaining 535 registered theorem rows as one last pristine
  sample-only continuation, and persist its final non-periodic step before the
  upstream sentinel exit. During aggregation retain the first 32 proposals for
  every registered theorem and report any physically generated padding group
  separately.
- Evidence: the final continuation has 1,495 rows, so its upstream 16-prompt
  dataloader has 94 batches. Proof snapshots are periodic every five steps,
  while the upstream loop raises its `Stop` sentinel at step 94 before reaching
  the end-of-epoch sample-only save. The final seven-row dataloader batch is
  also padded to the four-worker divisor, physically generating one duplicate
  prompt group (32 proposals).
- Reason: neither periodic persistence nor worker-divisibility padding is a
  scientific factor. Saving before the existing sentinel preserves completed
  verifier output without changing generation or acceptance. Selecting the
  first complete 32-proposal group per registered theorem preserves the fixed
  proposal budget; explicitly reporting the excluded duplicate group preserves
  physical compute accounting.
- Consequence: the aggregate C0 validator must require exactly 9,655 disjoint
  registered training theorems, exactly 32 analyzed proposals per theorem,
  and exactly 32 additional padding proposals. It must report both 308,960
  registered proposals and 308,992 physically generated/verified proposals.
  The padding group contributes to neither pass@N nor the dominance archive.

### D-026 - Persist observational per-proposal verifier telemetry

- Date: 2026-08-04
- Decision: beginning at the durable C0 step-60 boundary, persist deterministic
  proposal/theorem/proof identities, response token count, wrapper parse time,
  verifier queue wait, Lean verification time, verdict, failure class, timeout
  flag, verifier worker identity, tactic-prefix signature, and resolved
  config/environment hashes alongside every proof JSONL row.
- Evidence: the upstream verifier already measures `verify_time`, but its
  aggregation wrapper retained only correctness. The process scheduler also
  carries each request's submission timestamp and worker index, so queue wait
  and worker identity can be propagated without altering request order or Lean
  acceptance. Focused tests prove the emitted verdict equals the existing
  `success_indices` result and cover acceptance, Lean rejection, timeout, and
  wrapper parse failure.
- Reason: these fields make individual stragglers and failure modes auditable.
  They are observational only: model, prompts, generation, verifier inputs,
  timeout, correctness semantics, proposal budget, and sampling remain fixed.
- Consequence: the first 261,120 durable C0 proposals retain their existing
  proof/verdict records and batch timing but cannot acquire exact historical
  per-proof latency without re-verification; do not rerun them merely to fill
  telemetry. The remaining 17,120 registered C0 proposals (plus 32 reported
  padding proposals) and all later runs use the extended schema. `parse_time`
  denotes wrapper code-fence extraction, not Lean tactic execution time;
  per-tactic execution time, CPU consumption, and peak memory remain unknown.

### D-027 - Freeze the complete C0 aggregate and dominance archive

- Date: 2026-08-04
- Decision: declare C0 complete only from the four checksummed authoritative
  proof snapshots recorded in
  `runs/c0-base-20260804-seed42-complete/validation.json`, retain the first 32
  proposals for the one padded theorem, and freeze the resulting tactic-mode
  archive for downstream blocklist construction.
- Evidence: the aggregate and an independent second audit both found exactly
  9,655 registered train theorems, 308,960 registered proposals, 308,992
  physically generated and Lean-verified proposals, 32 excluded padding
  proposals, and 168,029 registered correct proposals. The archive contains
  counts for all 7,785 solved theorems; its counts sum to 168,029 and its
  SHA-256 is
  `fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3`.
- Consequence: this archive is the only C0 discovery source for later C3
  blocklist construction. Do not add test rollouts, interrupted transient
  batches, the excluded padding group, or later C1/C2/C3 outputs to it. C0 is
  sample-only and supplies no actor or optimizer checkpoint.

### D-028 - Bound the unchanged C1 engineering smoke to one update

- Date: 2026-08-14
- Decision: run the first 16 registered training rows and first 16 registered
  validation rows, in source order, as the C1 engineering smoke at seed 42.
  Retain 32 proposals per training theorem, the registered C1 optimizer and
  sampling settings, and the unchanged Lean verifier. With
  `problem_batch_size=16`, `train_batch_size=256`, and dynamic updates, this is
  one dataloader step, 512 generated proposals, and exactly one actor update.
- Reason: the smoke tests generation, verification, advantage calculation,
  reference-policy scoring, backpropagation, checkpoint persistence, and fresh
  initialization. Reducing only the number of prompts bounds engineering
  compute without changing proposal count per prompt or the treatment.
- Consequence: label this run as an engineering smoke, never as a C1 result.
  It cannot contribute to scientific metrics, the C0 archive, or any C3
  blocklist. A full C1 run still uses all 9,655 registered training theorems.

### D-029 - Register cross-fitted stable-top blocking as a C4 ablation

- Date: 2026-08-14
- Decision: retain C3 unchanged as the primary registered intervention. Add a
  separate C4 `StableTopBlock-Restart` ablation that blocks exactly one C0
  mode only when candidate indices 0--15 and 16--31 independently have the
  same unique top correct mode, there are at least four correct proposals
  overall, and each half contains at least two correct proposals outside that
  mode. C4 retains the pristine restart, fixed 32-proposal budget, unchanged
  incorrect-rollout treatment, no free resampling, and all-blocked prompt skip.
- Evidence: the checksummed offline report
  `results/c0_crossfit_blocking.json` reconstructs all 9,655 registered C0
  groups from the four frozen snapshots. The per-half alternative-support
  floors 1, 2, and 4 retain respectively 2,425, 2,323, and 1,961 eligible
  theorems. Floor 2 covers 24.06% of training theorems, blocks 27,336 observed
  top-mode correct proposals, and retains 33,678 observed alternative correct
  proposals, or 14.50 alternatives per eligible theorem on average.
- Reason: 32 proposals cannot establish that an unobserved mode does not
  exist. Cross-fitting tests whether both the blocked mode and alternative
  positive support replicate within the fixed C0 sample. Floor 2 retains broad
  coverage while requiring more than a singleton alternative in each held-out
  half.
- Consequence: C4 is exploratory and cannot replace the preregistered C2/C3
  comparison. Build its blocklist only from the frozen C0 training snapshots.
  A later independent pristine-base 32-sample control may calibrate natural
  new-mode discovery, but it must never update either archive.

### D-030 - Persist proposal-level hard-block decisions and run counters

- Date: 2026-08-14
- Decision: before the first C3 smoke, persist `mode_id` and
  `blocked_correct` on every proof record when blocking is enabled, and report
  blocked correct proposals, trained samples, and all-blocked skipped prompts
  in the existing per-step metrics.
- Reason: hard blocking already computed these values to apply the registered
  advantage and skip semantics, but discarded them after the update. The run
  contract requires proposal, verified, correct, blocked, and trained counts
  to be independently auditable.
- Consequence: this is observational telemetry only. It does not change mode
  matching, Lean verdicts, proposal selection, rewards, advantages, prompt
  skipping, sampling, or optimization. Disabled blocking still follows the
  upstream path and reports zero new blocking counters.

### D-031 - Require a 1-TB node-memory request for full training and evaluation

- Date: 2026-08-14
- Decision: request 1000 GB of node memory for full C3 and registered Lean
  evaluation jobs. Execute queued C3 from a node-local archive of the exact
  prepared Git commit, while retaining the allocation with `sleep infinity`
  after training or setup failure.
- Evidence: the first combined held-out C0 evaluation on allocation `19060059`
  completed one 512-proposal batch, then Slurm reported two OOM kills under
  the inherited 256-GB node-memory request. The resulting lost Ray worker
  caused a 600-second NCCL all-gather timeout. D-023 had already established
  the 32-GB per-verifier process ceiling for future runs on a 1-TB allocation.
- Reason: node memory is an infrastructure ceiling, not an experimental
  factor. The model, data, prompts, proposal budget, sampling, verifier,
  rewards, optimizer, and seed remain unchanged. Archiving the prepared commit
  prevents later repository changes from altering a queued scientific run.
- Consequence: the failed evaluation directory is diagnostic only and must not
  contribute metrics. Do not launch full C3 or registered evaluation under the
  existing 256-GB allocation. Preserve the failed log and Slurm OOM evidence.

### D-032 - Prioritize the completed comparison before replication

- Date: 2026-08-16
- Decision: complete and analyze the registered C0/C1/C3 comparison before
  allocating compute to repeat runs. Do not queue additional runs
  merely to establish that a small or operationally irrelevant effect is
  repeatable.
- Reason: the immediate research objective is to determine whether hard
  dominant-mode exclusion produces a material exploration signal. The most
  decision-relevant first evidence is held-out pass@N, correct mode coverage,
  new correct modes relative to C0/C1, block rate, and all-blocked prompt rate
  from the already compute-matched pipeline.
- Consequence: if the comparison shows a material effect, replication becomes
  a confirmation step before a strong scientific claim. If it is null or
  marginal, prioritize mechanism diagnosis or the separately registered C4
  stronger exclusion ablation rather than spending the next allocations on
  identical seeds. Keep C4 exploratory and use the completed comparison to
  select the next mechanism experiment.

### D-033 - Resolve the sample-only evaluation advantage estimator explicitly

- Date: 2026-08-19
- Decision: rerun the registered C0 evaluation in a fresh `retry1` directory
  with `algorithm.adv_estimator=grpo` explicitly resolved. Preserve the failed
  prepared directory and record the operational launcher checksum and resolved
  Hydra config for the retry.
- Evidence: the prepared evaluation launcher omitted an advantage-estimator
  override, so the inherited default resolved to `gae`. Upstream worker
  initialization deliberately raises `NotImplementedError` for `gae`; the run
  stopped before model-worker creation, sampling, or Lean verification. Both
  pinned evaluation commits contain the same omission.
- Reason: evaluation is sample-only and performs no advantage computation or
  optimizer update, but worker construction still requires a supported
  estimator value. `grpo` matches the registered training path and changes no
  model, data, prompt, sampling, verifier, proposal budget, correctness signal,
  or seed.
- Consequence: exclude the failed launch from all metrics. Use the fresh retry
  for C0 and the same explicit estimator for C1/C3 evaluation so every
  checkpoint is evaluated through an identical resolved configuration.

### D-034 - Extend the completed C0/C1/C3 evaluation to pass@128

- Date: 2026-08-20
- Decision: evaluate the pristine C0 actor and the completed seed-42 C1 and C3
  checkpoints with fresh, complete 128-proposal draws on the unchanged 223-row
  registered-valid and 244-row miniF2F-test splits. Do not splice additional
  proposals onto the earlier 32-proposal runs. Reduce the theorem batch from 16
  to 4 so each generation-and-verification batch remains at the already tested
  512 physical proposals.
- Evidence: at pass@32, C3 recovered 481 correct tactic modes relative to C1
  across the two evaluation splits while the theorem identities solved by the
  two models were nearly unchanged. Training-window replay further shows that
  C3 slowed but did not reverse the decline in correct modes per correct
  rollout. The frozen experiment plan already registers pass@128 as a primary
  metric.
- Reason: a larger matched sampling budget tests whether the preserved tail of
  correct modes remains accessible and whether its benefit grows beyond 32
  attempts. Fresh full draws keep candidate accounting and sampling provenance
  simple and auditable.
- Consequence: all three conditions use 128 proposals per theorem, identical
  sampling settings, and no optimizer update or evaluation-time blocking.
  Report pass@1 through pass@128, mode accumulation, rarefied mode coverage,
  and C0 modes suppressed by C1 but retained by C3. This is an extension of
  evaluation, not a new training condition and not evidence that blocking alone
  caused the C1/C3 difference.

### D-035 - Exclude failed pass@128 launches and enforce the worker path

- Date: 2026-08-31
- Decision: exclude jobs `20173754` and `20173755`, cancel the still-pending
  matching C3 job `20173756`, and prepare fresh C0/C1/C3 pass@128 run
  directories after adding `algorithm.adv_estimator=grpo` to the reusable
  evaluation launcher. Add a regression test for the resolved override.
- Evidence: C0 and C1 both stopped before model-worker creation with
  `ray.exceptions.RayTaskError(NotImplementedError)` in
  `ray_trainer.py::init_workers`. Their resolved configurations show
  `algorithm.adv_estimator=gae`; neither run created a proof snapshot. The
  dependent finalizers failed closed because no persisted proofs existed. C3
  was queued with the identical launcher and had not started when cancelled.
- Reason: D-033 already established `grpo` as the required sample-only worker
  initialization path. The pass@128 launcher generalized the proposal budget
  without carrying that operational override into the tracked script.
- Consequence: the failed allocations produce no scientific observations and
  are not combined with any future evaluation. Fresh retries retain the same
  model checkpoints, data, prompts, verifier, seed, sampling settings, and
  59,776-proposal budget per condition.

### D-036 - Transfer the known-working runtime as installed bits

- Date: 2026-08-31
- Decision: package the project under one relocatable top-level directory with
  managed CPython 3.11.4 and the exact installed Python site-packages from the
  completed runs. Include the base model, the final C1 and C3 actors, every run
  record and proof log, datasets, C0 archives, Lean 4.9.0-rc1, and the built
  DeepSeek verifier. Store the full package inventory and a relative-path
  SHA-256 manifest.
- Evidence: the producing environment reports PyTorch 2.3.0 with CUDA 12.1,
  cuDNN 8.9.2.26 and NCCL 2.19.3. A fresh package-index resolution rejects the
  historical Torch/NCCL combination even though those installed bits produced
  the completed experiments and pass the current import checks.
- Reason: resolving again would silently change the runtime during the cluster
  move. Copying the installed files preserves the known-working scientific
  environment and requires no package, model, Lean, mathlib, or verifier
  download at the destination.
- Consequence: the destination requires Linux x86-64, compatible glibc, and an
  NVIDIA driver capable of the bundled CUDA 12.1 runtime. Scheduler account and
  partition directives remain cluster-specific. Transfer verification checks
  registered data/model hashes, exact runtime versions, and optionally every
  file in the bundle manifest.

### D-037 - Destination pass@128 execution on a persistent full H100 node

- Date: 2026-08-31
- Decision: run the already registered C0/C1/C3 pass@128 retries sequentially
  inside one 23-hour `compute_full_node` allocation under `def-zhijing`, using
  all four H100 80-GB GPUs and the node's scheduler-provided 745 GiB of host
  memory. Retain the allocation with `sleep infinity` after the fail-closed
  sequence so intermediate results or infrastructure failures can be inspected
  in place.
- Evidence: destination preflight passed with NVIDIA driver 580.173.02. The
  portable runtime reports the pinned Python, PyTorch, CUDA, cuDNN, NCCL,
  Transformers, vLLM, Ray, FlashAttention, xFormers, and Triton versions. Full
  checksums passed for the registered dataset, C0 archive, base-model shards,
  tokenizer, and configuration. Transfer had dropped executable mode bits from
  the bundled Lean, Elan, and REPL binaries; their contents still match the
  manifest, the owner-executable bits were restored, and a destination Lean
  acceptance proof then passed completely in 6.97 seconds. Preflight and the
  bundle verifier now check these exact executable paths rather than accepting
  an unrelated system `lake`. The destination scheduler does not accept an
  explicit memory request: ordinary four-GPU jobs receive 186 GiB per GPU,
  while `compute_full_node` jobs receive the whole 745-GiB node.
- Reason: the source-cluster jobs did not transfer as live scheduler state.
  One persistent destination allocation allows each condition to be finalized
  and validated before the next begins while preserving the registered models,
  data, prompts, verifier, 59,776-proposal budget, sampling settings, seed, and
  no-update evaluation semantics at commit
  `d031de76343142610036e0e03c216782b10537d9`.
- Consequence: job `868001` is the destination execution record. The three
  source-cluster retry IDs remain historical only. Any host-memory failure on
  the 745-GiB node fails closed and must not contribute scientific results;
  it motivates a separately recorded verifier-concurrency or H200-memory
  infrastructure decision rather than an unlogged change during evaluation.

### D-038 - Freeze the pass@128 accumulation and representation diagnostics

- Date: 2026-08-31
- Decision: before the destination pass@128 results exist, freeze one analysis
  panel that reports observed prefix accumulation and finite-sample expected
  accumulation at proposal counts 1, 4, 8, 16, 32, 64, and 128; paired
  correct-rollout rarefaction; top-mode concentration and effective mode
  counts; C0-mode suppression and C3 recovery; and paired C3-minus-C1 shifts.
  Report the registered ordered tactic-head signature as primary and always
  include sensitivity at five other resolutions: first tactic head, first two
  heads, unordered head set, tactic-head multiset, and normalized exact proof.
- Evidence: the analysis implementation reproduces every finalized pass@32
  pass@K, correct-count, and tactic-mode total, as well as the registered Pratt
  paired-Wilcoxon result (`p = 7.94050299945234e-15`). On that already observed
  pass@32 sample, the C3-minus-C1 direction remains positive at every listed
  representation, including first-head coverage (907 versus 836; paired
  `p = 0.0008603`) and exact normalized proofs (6,675 versus 6,234; paired
  `p = 1.61e-12`). At 16 equalized correct draws, C3 has 10.27 expected tactic
  modes per common eligible theorem versus 9.14 for C1.
- Reason: proposal-level accumulation tests whether C3 preserves accessible
  tail mass as K grows; correct-rollout rarefaction separates mode richness
  from differences in correctness counts; and the full representation panel
  tests whether the result depends on tactic order or fine textual variation.
  Freezing all resolutions prevents selecting a favorable identity after the
  pass@128 results are seen.
- Consequence: none of the sensitivity identities replaces `mode_id_v1` for
  blocking or the registered primary metric. They bound its interpretation;
  no identity is described as semantic mathematical strategy. The analyzer
  must fail closed unless its recomputed pass@K and full-sample counts exactly
  reproduce each run's finalized metrics.
