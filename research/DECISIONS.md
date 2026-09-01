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

### D-039 - Run the full C3-matched no-blocking causal control

- Date: 2026-08-31
- Decision: run one full seed-42 control from the pristine base model with
  C3's complete optimizer and sampling configuration but with hard blocking
  disabled. It uses all 9,655 registered training theorems, 32 proposals per
  theorem, two PPO epochs, KL coefficient 0.10, rank penalty zero, a fresh
  optimizer and empty rollout buffer, and the unchanged Lean verifier. No C0
  archive is loaded or consulted.
- Motivating finding: C3 produced 56.8% more on-policy correct tactic
  signatures than C1 and a robust held-out mode-coverage gain at pass@32, but
  C1 uses one PPO epoch and KL 0.02 whereas C3 uses two epochs and KL 0.10.
  Pass@128 can characterize the accessible tail but cannot isolate blocking
  from those optimizer differences. This control remains decision-relevant
  regardless of whether the pass@128 gap grows or saturates.
- Hypothesis: at the same 308,960-proposal budget, C3 will retain materially
  greater correct tactic-mode coverage than the matched control, together with
  higher paired correct-draw rarefaction and lower within-theorem
  concentration. A C3 advantage of at least 10% in total correct tactic modes
  with a positive paired rarefaction shift is treated as operationally
  material; a difference within plus or minus 5% is treated as practically
  null pending the held-out evaluation. If the control matches or exceeds C3,
  the current diversity result cannot be attributed specifically to blocking.
- Reason: this is the smallest full-scale run that identifies the causal
  contribution of the blocklist without changing data, model, prompts,
  verifier, sampling, proposal accounting, optimizer, seed, or training
  duration. A short subset run would be an engineering check and would not
  resolve the scientific confound.
- Consequence: the control launcher is mechanically tested against the C3
  launcher after removing `lean.hard_blocking.*` arguments; every remaining
  trainer argument must be identical. The control must persist zero blocked
  proposals, zero all-blocked skips, and a pristine-base lineage. After a
  complete training run, evaluate its final checkpoint on the same frozen
  held-out set and proposal budget used for the C0/C1/C3 comparison before
  making a blocking-specific held-out claim. Destination job `868049` runs the
  committed control at `4d435f29a011f8524e649cb388aed7a5d8a957ec` through
  operational runner SHA-256
  `1126ed1d0efbaac0846bd28bbef26631c13de8c9dda9ff2dc49b7e5f47e56aff`.

### D-040 - Freeze the C3-versus-control training analysis before results

- Date: 2026-08-31
- Decision: analyze the full matched control with a fail-closed, frozen panel:
  total correct tactic modes and exact proofs; paired theorem-level correct,
  mode, exact, top-mode-share, and effective-mode shifts; correct-rollout
  rarefaction at 1, 2, 4, 8, and 16 correct draws; 100-step training windows;
  C0-mode suppression and C3 recovery relative to the control; and separate
  results for the 1,014 C0-archive-eligible versus 8,641 ineligible theorems.
  Apply the D-039 10% material-support and 5% practical-null thresholds
  mechanically.
- Evidence: before control data exists, the analyzer was run end-to-end with
  C1 substituted only as a validation fixture. It exactly reproduced the known
  C1/C3 correct tactic totals (34,336 and 53,825), relative delta (56.76%),
  paired 16-correct-draw rarefaction delta (1.824), and the frozen archive's
  1,014 eligible theorem count.
- Reason: equal-correct-draw rarefaction separates richness from correctness
  count, concentration tests the proposed redistribution mechanism, and the
  archive stratum tests whether effects align with direct intervention
  eligibility while still allowing global policy spillovers. Freezing the
  complete panel prevents metric selection after seeing the control.
- Consequence: the surrogate validation is not scientific evidence about the
  matched control. The analyzer refuses mismatched theorem identities, an
  archive with any eligible count other than 1,014, reused output paths, or
  incomplete finalized runs. A training classification remains explicitly
  provisional until the matched control checkpoint is evaluated held out.

### D-041 - Freeze the matched held-out C3-versus-control analysis

- Date: 2026-08-31
- Decision: make `c3_matched_control` a first-class preparation and
  finalization condition for the unchanged Lean evaluation pipeline. Compare
  its final checkpoint with C3 on the identical frozen 467-theorem parquet and
  proposal budget, reporting expected and observed accumulation through every
  available K; paired correct-draw rarefaction; exact McNemar solved-theorem
  discordance; paired correct, tactic-mode, exact-proof, concentration, and
  effective-mode shifts; and all six D-038 representation resolutions.
- Evidence: before the control checkpoint or its evaluation exists, the held-
  out analyzer was validated end to end with C1 substituted only as a fixture.
  It exactly reproduced the registered pass@32 C3-minus-C1 mean tactic-mode
  delta (1.02998), Pratt-Wilcoxon p-value
  (`7.94050299945234e-15`), discordant theorem counts (3 C1-only and 5 C3-only),
  exact McNemar p-value (0.7265625), and 3,445 versus 3,926 ordered-head modes.
- Reason: the training control identifies the intervention during on-policy
  learning, while the held-out comparison tests whether that causal effect
  persists in the final policy. Freezing accumulation, correctness, richness,
  concentration, theorem identity, and representation sensitivity together
  prevents selecting only a favorable endpoint.
- Consequence: evaluation still performs no blocking, advantage computation,
  or optimizer update. The analyzer fails closed on a condition mismatch,
  theorem mismatch, proposal-budget mismatch, parquet mismatch, incomplete
  finalization, or any failure to reproduce finalized pass@K and full-sample
  counts. The result identifies seed 42 within the C3 configuration and does
  not by itself establish multi-seed generality. The prepared pass@128 control
  evaluation uses commit `5ed24b985f2897709e25556579bf97f3d63d51a9` and may be
  attached to retained job `868049` only after the finalized training metrics
  and `global_step_604` checkpoint exist. The fail-closed operational runner
  SHA-256 is
  `81361510a6f5776b8c15cd239ef4f53145a32ceff3d26fbd8d72d0eaef4b32ee`.

### D-042 - Use the destination's complete 770-GB H100 node

- Date: 2026-08-31
- Decision: run destination jobs `868001` and `868049` on exclusive
  `compute_full_node` allocations with all 96 CPUs, all four H100s, and the
  scheduler's full 770,000-MiB physical-memory resource. Monitor live memory
  and Slurm OOM state once each payload starts. Preserve the existing
  fail-closed finalization rules and exclude any incomplete or OOM-affected
  run from scientific analysis.
- Evidence: `scontrol` reports both jobs requesting
  `cpu=96,mem=770000M,gres/gpu=4` with `OverSubscribe=NO`; every node in the
  destination partition reports `RealMemory=770000`. The earlier excluded
  evaluation failed under a 256-GB limit, while the source-cluster rule in
  D-031 requested 1 TB. A literal 1-TB allocation is therefore unavailable on
  this destination, but these jobs receive roughly three times the known
  failing memory ceiling and the destination's entire node.
- Reason: node memory is an infrastructure ceiling, not an experimental
  factor. Cancelling and resubmitting cannot obtain more memory in this
  partition, whereas the retained allocation allows live inspection and a
  clean stop if memory proves insufficient.
- Consequence: the destination runs keep model, data, prompts, proposal
  accounting, verifier, optimization, seed, and analysis unchanged. Success
  requires the same completed snapshots and finalized metrics as before; the
  full-node request alone is not evidence that the payload completed safely.

### D-043 - Materialize the frozen pass@32 robustness baseline

- Date: 2026-08-31
- Decision: before destination job `868001` starts, execute the complete D-038
  accumulation and representation panel on the already finalized C0/C1/C3
  pass@32 artifacts. Commit the result as
  `results/registered_c0_c1_c3_seed42_pass32_accumulation.json`; do not treat
  it as pass@128 evidence.
- Evidence: the analyzer from commit
  `4cffa92b4467efe2d47781c502bdf683bf26248d` (script SHA-256
  `50e410fa4db84cb993ef32d404b981183ee46cbb1820d414727914f438f6cc86`)
  reproduces 3,445 C1 and 3,926 C3 ordered-head modes and the registered paired
  mean delta 1.02998 with `p = 7.94050299945234e-15`. At 16 equalized correct
  draws, C1 has 9.1403 expected modes and C3 has 10.2722, a paired mean delta
  of 1.1319 (`p = 7.20420168297625e-15`). The C3-minus-C1 coverage direction
  is positive at all six frozen representation resolutions. Expected
  all-proposal mode accumulation moves from -4.3% C3 versus C1 at one draw to
  +1.3%, +5.0%, +9.1%, and +14.0% at 4, 8, 16, and 32 draws. Result SHA-256:
  `5691cc3fb22d8cb4cb52c575628efa1512a2cac2035e87b2909d703dc50fede6`.
- Reason: this gives pass@128 a fixed, directly comparable pass@32 baseline
  and tests whether the existing diversity result depends on correctness
  count or one syntactic mode definition. Running it before any destination
  pass@128 output preserves the prospective status of the larger-sample
  analysis.
- Consequence: equal-correct-draw rarefaction and the representation panel
  strengthen the seed-42 distributional finding, but tactic signatures remain
  syntactic rather than semantic proof strategies. Causal attribution still
  requires the matched control, and sampling-tail claims still require the
  pending pass@128 results.

### D-044 - Make registered analysis inputs fail closed before results

- Date: 2026-08-31
- Decision: before jobs `868001` or `868049` starts, require every training and
  evaluation analyzer input to reproduce the finalized condition,
  classification, completion marker, registered and physical proposal counts,
  padding count, and proof-log hash. Evaluation inputs must also reproduce the
  frozen parquet hash. The matched control must record zero logical and
  physical blocked proposals, zero all-blocked skips, and no blocking archive;
  C3 must record the supplied C0 archive hash. Report separately when the
  control matches or exceeds C3 even if the difference also lies inside the
  registered practical-null band.
- Evidence: commit `bf1e026b9dd54cbc02e43cff21882201e1f4b34c` adds boundary
  and contamination tests. All 34 project tests pass. Replaying the hardened
  loaders on the completed artifacts exactly reproduces 34,336 versus 53,825
  training modes, the paired 16-correct-draw training delta 1.823625, and 3,445
  versus 3,926 held-out ordered-head modes with paired mean delta 1.029979.
- Reason: a valid expensive payload can still support a false conclusion if an
  analyzer accepts the wrong condition, incomplete output, modified proof log,
  or a contaminated control. These checks strengthen provenance and decision
  enforcement without changing any registered metric, threshold, sampling
  rule, or queued experimental payload.
- Consequence: future result generation aborts before statistical analysis on
  any invariant mismatch. The primary 5% practical-null classification remains
  unchanged; an orthogonal attribution status makes the preregistered
  control-matches-or-exceeds-C3 falsification rule explicit.

### D-045 - Split pass@128 before launch to fit the allocation ceiling

- Date: 2026-08-31
- Decision: before any destination pass@128 output exists, supersede D-037's
  three-condition sequential execution only at the scheduling layer. Run C1
  followed by C3 in existing job `868001`, and run C0 independently in new job
  `868076`. Keep the exact prepared directories, models, commit
  `d031de76343142610036e0e03c216782b10537d9`, seeds, prompts, verifier,
  sampling parameters, per-condition 59,776-proposal budget, finalizers, and
  frozen joint analysis. The C1/C3 operational runner SHA-256 is
  `db36ae3bf87502431eec969b74c0f9f3c12bc79cdd7f6dc049508576a8242c6c`;
  the C0 runner SHA-256 is
  `d65e6ee2a6aba5fa2687e3157447540fb13e7c79f6cf7cb643a20a22ac90cf36`.
- Evidence: the three completed pass@32 conditions took 2.133, 2.029, and
  2.126 hours from hardware record to finalized metrics. Pass@128 preserves a
  512-proposal generation batch while increasing each condition from 14,944 to
  59,776 registered proposals, so the direct fourfold forecast is roughly
  8.1--8.5 hours per condition and 24.3--25.6 hours for three, before repeated
  model initialization. That exceeds the 23-hour allocation. Both destination
  jobs request identical exclusive four-H100, 96-CPU, 770,000-MiB nodes; at
  submission, `868001` and `868076` are pending and have produced no run files.
- Reason: splitting before launch prevents a predictable timeout from
  preferentially censoring the last condition. Keeping C1 and C3 together
  preserves the central contrast on one hardware allocation, while C0 is an
  unchanged independent no-update baseline.
- Consequence: node and wall-clock records remain condition-specific and are
  reported in the joint artifact. The scientific comparison remains paired by
  theorem and proposal budget, not by process lifetime. The matched-control
  pass@128 evaluation should use a fresh allocation unless its completed
  training job has at least ten hours remaining; the attached runner must not
  be started merely because the checkpoint exists.

### D-046 - Recover the transferred Ray executables inside the retained allocation

- Date: 2026-08-31
- Decision: exclude each C1 attempt in destination job `868001` that fails
  before a proof snapshot, preserve its directory as operational-failure
  evidence, restore user execute permission only on standalone native programs
  that the transferred environment left non-executable, and require a small
  compiled-GPU smoke before another fresh retry. Continue to C3 only after a
  fresh C1 finalizes and validates. Add explicit native-runtime checks to the
  repository preflight and to the still-pending matched-control and C0
  workbenches.
- Evidence: the first C1 process exited at 21:20:37 during `ray.init` with
  `PermissionError` on `gcs_server`; its fail-closed finalizer found no proof
  snapshot. The preserved `retry1` directory has no model-worker output,
  proof archive, or metrics. Both transferred native files were mode `0644`;
  restoring them to `0744` did not change their SHA-256 hashes
  (`85558423c1152b348c6080dd6d98f418036879569fc397e5e0ef399ff79febb0`
  for `gcs_server` and
  `3cec71f9a2b56c3be743e1d7817774762e281acf19d9df19553994d36215bb97`
  for `raylet`). A short-path node-local Ray smoke then started and shut down a
  local instance successfully. Fresh `retry2-rayexecfix` crossed Ray startup,
  loaded the 6.91B actor and reference on all four H100s, and reached its first
  forward pass, where it failed at 21:31:27 because Triton's bundled `ptxas`
  was also mode `0644`; its fail-closed finalizer likewise found no proof
  snapshot. A complete file-type scan found Triton's three CUDA tools and a
  small explicit set of other package-native programs as the only remaining
  non-executable standalone ELF files; all were restored to `0744` without
  content changes. The relevant SHA-256 values are
  `eb8d520a3df252220ffde7434832c32ba73b2c7912305f083ab1d52f16bb9704`
  (`ptxas`),
  `3376a2b29d52bf8db84f404eaa19f7ac8f763f42be2847019c1dea0f529087ae`
  (`cuobjdump`),
  `bf1ae1c2e724d4f238fd143696277385a20aab12ea3c107fd5b8749cfd95484b`
  (`nvdisasm`), and
  `0e0df3403ba4748f392b8cc5eb565d153b4ede5c938742f57f1565f5240cf16b`
  (`torch_shm_manager`). A node-local `torch.compile` GPU smoke then completed
  a Triton-compiled kernel successfully using the allocation's GCC 12 toolchain.
  Fresh `retry3-nativeexecfix` generated normally, but its first three batches
  each returned 512 verifier system errors. The run was stopped immediately
  after comparison with pass@32 showed that two first-batch theorems previously
  had 30/32 and 15/32 correct proofs. The frozen `d031de7` launcher hardcodes
  verifier home `/scratch/memoozd`, which had no `.elan` on the destination,
  while the pinned runtime was staged allocation-locally. A checked symlink
  from that legacy home to the bundled pinned Elan tree restored the frozen
  path contract. The upstream verifier's own known-correct one-process smoke
  then returned `pass: true`, `complete: true`, and no system error. The
  retry-4 attached runner SHA-256 is
  `1231faf9464c747a5bab032e98c6aa093e438940ccf6084de41f2b93e0460661`;
  the final hardened pending control and C0 runner SHA-256 values are
  respectively
  `7df38267a19e690bb288edb0e395b158988272f84941f62c92c4e2fb79f5b9a3`
  and `69b5d003401e4cd298eb2455eddee8317d2615f657e3e6d85c175ea289af8215`.
- Reason: file modes are transfer/runtime infrastructure, not an experimental
  factor. Reusing the failed output directory would blur provenance, while
  discarding the healthy 23-hour allocation would add delay without changing
  the payload. The retained workbench permits a visible smoke test and fresh
  retry after a failure that occurred before scientific computation.
- Consequence: at the time of this decision, retry 4 was the only eligible
  next C1 directory; failed `retry1`, `retry2-rayexecfix`, and the deliberately
  stopped `retry3-nativeexecfix` were already permanently excluded. D-047
  subsequently excludes retry 4 as well after its independent destination
  memory failure. This native-runtime recovery changes no scientific factor or
  analysis rule.

### D-047 - Cap Lean verification at 32 workers on 770-GiB destination nodes

- Date: 2026-08-31
- Decision: permanently exclude C1 pass@128
  `retry4-verifiersmoke`, add a validated operational
  `RESTRICTION_LEAN_MAX_WORKERS` launcher override, and set it to 32 for every
  remaining destination training and evaluation condition. Run C1, C3, C0,
  and the C3-matched no-blocking control in separate 23-hour full-node
  allocations rather than placing C1 and C3 sequentially in job `868001`.
  Preserve every scientific factor: model checkpoint, dataset, theorem order,
  seed, prompts, proposal count, sampling configuration, verifier and its
  per-proof 32-GiB limit, metrics, finalizers, and frozen analyses. Only the
  number of concurrently resident verifier processes changes.
- Evidence: retry 4 completed its first three 512-proposal batches with normal
  generation and verified-proof counts, then reached approximately 753 of 755
  GiB during batch 4. Ray explicitly reported four model workers killed due to
  memory pressure at 21:57:19; the run was stopped at 21:57:54 without a final
  proof snapshot or metrics. A discovery-only replay then selected the same
  128 frozen C1 pass@32 proofs from theorem positions 12--15, the batch-4
  failure neighborhood, and verified them with 32 workers. It completed in
  247.34 seconds, reproduced the frozen per-theorem correct counts exactly as
  `[0, 32, 9, 17]`, and classified all 128 proofs as 58 correct or 70 Lean
  rejections with no parser or verifier exception. Peak standalone memory was
  483,643,088 KiB (461.2 GiB), leaving 308,625,988 KiB (294.3 GiB) available.
  Adding the approximately 90-GiB model/Ray increment observed in retry 4
  still leaves more than 200 GiB of projected headroom. The replay log and
  memory trace SHA-256 values are respectively
  `c9f904d5151613706b2d2e23b42f6ede6583b2664f1d82ceec69598a967eac5e`
  and
  `c43096bc561ffede287d2141c08f2601613b57554f04f7db6bcb92025a9b26fe`;
  the replay program and runner SHA-256 values are
  `20d4d22e63cf8161967895cfd823486e2032a096b57d1730f2fdf4f37a0987bf`
  and
  `43c281c2d9cb6885eeeac5ea70d336338ef0ddadebe33f350e4804d8884b03d7`.
- Reason: the destination's complete physical node is smaller than the source
  node, and 64 simultaneous Lean processes can consume effectively all memory
  for proof-dependent pathological batches. Concurrency affects throughput
  and resident memory, not the deterministic Lean verdict. The targeted replay
  directly verifies verdict equivalence at 32 workers while preserving enough
  headroom for the four model workers. Separate allocations prevent the lower
  verifier throughput or one condition's tail behavior from censoring a later
  condition under the 23-hour ceiling.
- Consequence: no scientific result may use retry 4 or any prior C1 recovery
  directory. All remaining destination runners must record
  `lean_max_workers=32`, their execution commit, and their own checksum in a
  fresh run directory. The default remains 64 for environments that do not set
  the override; its positive-integer validation fails closed. C3 and its
  matched control receive the identical operational override, so intervention
  status remains their only launcher-level scientific difference. The exact
  execution snapshot is commit
  `8dc756385e70002b6d47de598f563f6eedf2fa77`. C1 uses retained job `868001`;
  C0, control, and C3 use jobs `868076`, `868049`, and `868228`. Their fresh
  32-worker runner SHA-256 values are respectively
  `043c1a082e9719b394ea6203d612ed62eb86cf47d12b3cd2bf51b7c96a9ffeb5`,
  `a2d1c6625c68d4221976b511b3a5709d98d17e685fdb6f8a23a91358ebcd0166`,
  `2fe8bdf5564481fffb513922498f4f6ea042a3949cfc07c9de3b76c420145609`,
  and
  `ee9055c679a98e9c3e77d5d967aa3b5b6a72a1135f5046a373394db58e4c78a3`.
  The separately prepared, fail-closed matched-control pass@128 evaluator has
  runner SHA-256
  `86e48e0d175470614a3e6978dae8c2c6fe1b51811c1b68fafb25f4ddc09b5405`;
  it may attach to retained job `868049` only after finalized training and only
  with enough remaining time to avoid censoring the evaluation.
  The real C1 retry subsequently crossed the original failure boundary: its
  fourth 512-proposal batch completed in 890.985 seconds with 239 correct
  proofs, zero blocking, and no worker death or memory-pressure report. The
  15-second monitor measured a 558.285-GiB peak, leaving approximately 197 GiB
  available. This in-situ result confirms the replay-based concurrency choice;
  it does not make the still-incomplete C1 run eligible for analysis early.
  Independent C0 then crossed the same theorem-position boundary: its fourth
  512-proposal batch completed in 648.638 seconds with 188 correct proofs, no
  system error, and a 548.775-GiB peak leaving approximately 207 GiB
  available. Agreement across two policy distributions supports concurrency,
  rather than checkpoint-specific proof content, as the controlling recovery.

### D-048 - Test dominant-mode rejection as a distinct exploration intervention

- Date: 2026-08-31
- Decision: implement a separate C5 `RewardReject-Restart` experiment. Preserve
  C3's base model, frozen C0 archive, data, theorem order, prompts, proposal
  budget, optimizer, KL, PPO epochs, seed, Lean verifier, and pristine restart.
  Change exactly one factor: a Lean-correct rollout whose tactic signature
  matches the archived dominant mode is not accepted as a successful training
  outcome. Preserve the original Lean verdict in telemetry, assign the blocked
  rollout binary training reward zero, and compute ordinary group-relative
  advantages from that modified reward vector. Do not zero its advantage after
  normalization. Continue to skip a prompt when every Lean-correct rollout is
  blocked, and do not generate free replacements.
- Hypothesis: treating the dominant mode as unsuccessful in the training
  environment will exert stronger exploration pressure than C3's neutral
  zero-advantage exclusion. Relative to C3 at the same proposal budget, C5
  should reduce dominant-mode concentration and increase equal-correct-draw
  tactic-mode coverage; it may trade away raw correct-rollout rate or pass@1.
- Pre-run evidence: replaying the frozen C3 training snapshot through the C5
  acceptance rule finds 859 theorems with both blocked and alternative correct
  rollouts. These groups contain 12,405 blocked correct rollouts, 11,598
  alternative correct rollouts, and 3,485 incorrect rollouts. Under the C5
  reward vector, the blocked rollouts would have mean standardized advantage
  -0.686 while the alternatives would have mean advantage +0.913. Another 347
  all-Lean-correct groups contain both modes and would become trainable under
  C5; 58 groups with no observed correct alternative remain skipped.
- Guardrail: `correct` continues to mean Lean correctness everywhere in saved
  proofs and scientific evaluation. Add a separate
  `training_accepted_correct` field and separate reward-rejection accounting.
  Never describe a blocked proof as mathematically invalid, and never use the
  intervention during held-out evaluation.
- Decision rule: first require unit coverage and a one-update engineering smoke
  that demonstrates negative blocked advantages, positive alternative
  advantages, unchanged incorrect rewards, and complete accounting. Only then
  launch a fresh full C5 run from a committed snapshot. Compare its training
  dynamics and final checkpoint directly with C3; do not pool it with C3 or
  retroactively relabel the existing 56.8% and 14.0% results.
- Execution status: all 44 project tests and the destination preflight pass.
  Commit `0b8c70c` prepares an engineering-only slice of 16 theorems selected
  from the frozen training archive for strong observed support of both the
  blocked and alternative modes. Before any smoke output exists, that slice
  contains 269 archived dominant-mode and 240 archived alternative correct
  proofs; every theorem has at least 15 alternatives, and archived dominant
  shares range only from 0.516 to 0.531. Job `868254` is queued for one hour
  on one four-H100 full node with 32 verifier workers. Its runner SHA-256 is
  `3d4274499301f7f7fa28a3e5bb6e4d68cae07ffc4df6e42891a905f728b0b4a9`.
  The runner validates the signed per-category advantages and separate Lean
  correctness/reward-rejection counters, requires a real optimizer update, and
  parses Ray-prefixed telemetry before accepting the smoke. The first
  scheduler submission attempt created no job because Trillium rejects an
  explicit full-node memory directive; removing that scheduler-only directive
  yielded the automatic full-node 745-GiB allocation request used by job
  `868254` and changed no scientific setting. Pending job `868247` was
  cancelled before allocation and before writing any run artifact when the
  hardened shared workbench runner became available; job `868254` supersedes
  it.
  Historical C1 and C3 one-update smokes completed in 429 and 216 seconds,
  respectively. The pending C5 scheduler ceiling was therefore reduced from
  three hours to one hour to improve backfill eligibility while retaining a
  large setup and finalization margin; this changes no experimental payload.

### D-049 - Give the matched-control held-out evaluation a separate allocation

- Date: 2026-08-31
- Decision: do not attach pass@128 evaluation to matched-control training job
  `868049`. Queue a separate delayed 23-hour full-node workbench using the
  already prepared, still-pristine control evaluation directory and the exact
  `8dc7563` evaluation snapshot. Its runner waits fail-closed for finalized
  training metrics and `global_step_604` for at most six hours, validates zero
  intervention counters and complete 308,960-proposal training, then runs the
  unchanged 59,776-proposal held-out payload with 32 verifier workers. Preserve
  model, data, seed, prompts, sampling, verifier, finalizer, and D-041 analysis.
- Evidence: after 17 completed control updates, observed mean step time was
  114.945 seconds, including startup-tail variation. The remaining 587 updates
  project to 18.742 hours, leaving only about 3.5 hours in job `868049` even if
  that mean remains stable. D-045 requires at least ten hours before attaching
  a pass@128 evaluation. In contrast, conservative observed-mean projections
  left about 7.0 hours for C1 and 11.2 hours for C0, both inside their existing
  allocations; only the control evaluation requires another node.
- Reason: starting held-out evaluation with insufficient retained time would
  preferentially censor its later theorems and compromise the blocking-specific
  comparison. A delayed independent allocation separates training-tail risk
  from evaluation completeness while changing no scientific factor.
- Consequence: the old job-`868049`-bound attached runner is superseded and
  must not be launched. The separate runner SHA-256 is
  `1ab99c316de081b9eb49ed22766c3fa1222d9130976094e7804403567a9646cb`.
  Delayed full-node job `868264` is eligible to start at
  2026-09-01T17:00:00-04:00 and provides a new 23-hour ceiling.
  It refuses any non-finalized or contaminated training dependency, any reused
  evaluation directory, and any output that fails registered pass@128
  finalization.

### D-050 - Preserve sparse Mathlib files in tmpfs-backed verifier staging

- Date: 2026-08-31
- Decision: permanently exclude C1 pass@128 `retry5-workers32` and replay the
  complete condition in a fresh directory inside retained job `868001`.
  Preserve the validated 32-worker verifier cap. Change only node-local
  staging: copy the pinned verifier with sparse-file preservation and fail
  before sampling if its physical footprint exceeds 10 GiB. Apply the same
  fail-closed operational invariant to the not-yet-started C3 evaluation,
  matched-control evaluation, and C5 smoke. Give every pending runner a short
  Ray temporary prefix so its generated sockets remain under Linux's 107-byte
  AF_UNIX limit. Do not reuse any retry5 or retry6 proof or partial state.
- Evidence: retry5 completed 31 batches, then Ray killed its main task during
  batch 32 at 754.64/755.57 GiB node memory. After the failure, the inherited
  verifier workspace occupied 566 GiB under a `/dev/shm`-backed
  `SLURM_TMPDIR`, whereas the authoritative source occupied 4.3 GiB. Removing
  only that ephemeral expanded copy reduced node use from 587 GiB to 20 GiB
  and restored approximately 734 GiB available. In contrast, the independently
  fresh C0 and matched-control verifier workspaces each occupy 4.4 GiB and
  their 32-worker payloads continue normally. Retry5's earlier batch-4 peak
  and the frozen replay therefore remain valid concurrency evidence; they did
  not cover the separate sparse-file expansion defect.
- Reason: the Mathlib build cache contains large sparse files. Expanding their
  holes into tmpfs consumes physical RAM without changing verifier behavior,
  eventually starving Ray and Lean. Sparse preservation affects only the
  physical representation of the same checksummed verifier files. It changes
  no model, theorem, proof, seed, proposal, timeout, Lean verdict, or analysis
  factor. Reducing worker count alone would leave the accumulating 566-GiB
  staging defect intact and unnecessarily increase runtime.
- Consequence: retry6's sparse staging passed at 4,549,392 KiB, then Ray failed
  before worker creation because the generated plasma-store socket path
  exceeded 107 bytes. It is excluded without scientific output. Fresh C1
  retry7 uses the short job-local Ray prefix `/dev/shm/r868001r7` and runner
  SHA-256
  `4d193fe3cd1e18fcecde35aad5a7ea166dffeea5b6bd8a4409cd9ff8fbb2c826`.
  The still-pending C3 evaluation, C5 smoke, and delayed matched-control
  evaluation runners now have SHA-256 values
  `b4c65d7364ab2d7633c2823221d0c5e770bb41f3bb1cedbf0846f54b20bef48e`,
  `490d1ef3ac33ddd92fb708c0d8dd0c96a98a2dd6753db17e9fb8215e2e4ce304`,
  and `f7570e1401b01d9a78415587700bb357745cfd32f975357e38d350347c78a6f3`.
  Each records its own executed runner hash and staged physical size. Retries
  5 and 6 remain retained only as excluded failure evidence.

### D-051 - Advance reward rejection past the one-update gate

- Date: 2026-09-01
- Decision: the C5 engineering gate has passed. Prepare and queue one complete
  fresh `RewardReject-Restart` seed-42 training run with the same pristine base
  actor/reference, frozen C0 archive, theorem order, prompts, 308,960-proposal
  budget, two PPO epochs, KL 0.10, optimizer, seed, verifier, 32-worker cap,
  checkpoint policy, and no-resume semantics as C3. Change only the registered
  hard-blocking intervention from `zero_advantage` to `reject_reward`. Keep C5
  exploratory and secondary: it does not replace the matched no-blocking
  causal control, C0/C1/C3 pass@128 evaluation, or their decision rules.
- Evidence: one-hour H200 backfill job `868506` completed the frozen
  16-theorem smoke and finalized successfully in 438.785 seconds. Across all
  512 proposals it recorded 230 blocked correct, 254 alternative correct, and
  28 incorrect rollouts. Their mean standardized advantages were -0.9676,
  +0.9809, and -0.9504 respectively. All 230 blocked correct rollouts were
  separately marked reward-rejected; none was relabeled Lean-incorrect or
  zeroed after normalization. The update batch contained 512 samples, actor
  gradient norm was 0.9803, and `global_step_1` was saved. Metrics SHA-256 is
  `5d3e79e06f5f87829749f54e16f7a98370873ac623734dd9fd14e3a21b9ab98d`;
  proof-log SHA-256 is
  `2790fb3c64db5dbce300166d0ca1616b5348f66168c0f9c0b196faaf643acccd`.
- Reason: the smoke demonstrates the intended on-policy learning signal and
  unchanged Lean-correctness accounting, resolving the only preregistered
  engineering uncertainty before scale. A full run is now the smallest test
  of whether stronger negative pressure changes the policy distribution; the
  counterfactual replay alone cannot answer that question.
- Consequence: prepare the full run in a new directory and freeze its runner
  before submission. Prefer an H100 full-node allocation to match C3 hardware;
  if a different accelerator is used for scheduling reasons, record that as a
  limitation rather than presenting C5 as a single-factor causal contrast.
  Do not launch held-out C5 evaluation or select further ablations before the
  full training result exists and passes finalization. The available H200 node
  is used under that limitation and the run is classified
  `exploratory_full_seed42_h200`; H100 and H200 share Hopper architecture, but
  hardware-specific sampling or numerical effects are not assumed away. The
  frozen execution snapshot is `a0f1235`, the fresh directory is
  `c5-reward-reject-full-20260901-seed42-a0f1235-workers32`, and the fail-closed runner
  SHA-256 is
  `e1c2238c375c6b05a936e098ef9a211c33569c9943f0cb0e4d224c7dc4d9faf9`.
  It requires 604 telemetry summaries, 308,960 registered and 308,992 physical
  proposals, complete reward-rejection accounting, signed aggregate category
  advantages, and a valid `global_step_604` actor checkpoint. H200 full-node
  job `868543` is queued with that exact runner.

### D-052 - Exclude the slow H200 attempt and rerun C5 on matched H100 hardware

- Date: 2026-09-01
- Decision: permanently exclude H200 full-scale C5 job `868541` after two
  completed training steps, cancel duplicate pending H200 job `868543` before
  allocation, and restart the complete condition from the pristine base actor
  in a new H100 directory. Reuse no rollout, actor state, optimizer state,
  buffer, or node-local state from the H200 diagnostic.
- Evidence: the first two seeded H200 batches took 153.891 and 153.164 seconds
  for generation and 245.550 and 231.617 seconds end to end. The active
  destination H100 matched control generated the same first two batches in
  21.757 and 16.107 seconds; response-length means and maxima were identical,
  confirming like-for-like seeded payloads. Projecting the observed H200 mean
  step time across 604 steps gives about 40.0 hours, while the partition hard
  limit is 23 hours. Job `868541` was cancelled after 13 minutes 8 seconds and
  1,024 proposals, before the step-604 proof snapshot or actor checkpoint, and
  has no finalized metrics. Job `868543` was cancelled with zero runtime and
  no allocated node.
- Diagnostic only: H200 step 2 independently retained the intended mechanism:
  all eight blocked Lean-correct proofs were reward-rejected with mean
  advantage -0.521; 227 alternative correct proofs averaged +0.509 and 85
  incorrect proofs averaged -1.311. These partial observations may diagnose
  execution but may not enter any full-run comparison.
- Consequence: fresh directory
  `c5-reward-reject-full-20260901-seed42-a0f1235-h100-workers32` was prepared
  from clean execution snapshot `a0f1235`, with identical data and archive
  hashes and no pre-existing artifacts. It uses C3-matched H100 hardware, 32
  verifier workers, the complete 604-step payload, and the same fail-closed
  signed-advantage and physical-accounting gate. Runner SHA-256 is
  `3c92fc48c205c50e387c2e97f79e3c26daf294d0d822fb4ec6535d4b9473608e`.
  Full-node H100 job `868606` was queued as the only eligible full C5 run.
  Pending request `868603` was cancelled with zero runtime and no allocation
  solely to bind the submitted batch to an immutable, checksum-named runner
  path; this changed no payload or scheduler resource.

### D-053 - Move materializing verifier workspaces out of tmpfs

- Date: 2026-09-01
- Decision: permanently exclude C0 pass@128 retry2 and C1 pass@128 retry7,
  then replay both complete frozen conditions in fresh directories inside
  their retained allocations. Keep the validated 32-worker Lean cap and short
  Ray socket paths, but stage each sparse verifier tree on disk-backed `/tmp`
  rather than the allocation's tmpfs-backed `SLURM_TMPDIR`. Apply the same
  disk-staging invariant to the not-yet-started C3 pass@128, matched-control
  pass@128, and full C5 runners. Reuse no partial proof or model state.
- Evidence: C0 retry2 began with a 4,555,536-KiB sparse verifier tree and
  completed 31 batches. During step 32, Ray killed the main task at
  718.46/755.64 GiB against its 0.950795 memory threshold and the verifier
  reported `No space left on device`. The same job-local verifier tree then
  occupied 566 GiB under `/dev/shm`; removing only that exact ephemeral copy
  returned the node from 588 GiB to about 16 GiB used. This independently
  reproduces retry5's 566-GiB expansion and shows that a successful initial
  sparse-size gate does not bound later physical allocation. C1 retry7 had
  completed nine batches without error but was stopped before reaching the
  known failure region, so it has no eligible final snapshot. Its exact
  temporary trees were also removed, returning that node to about 16 GiB used.
- Reason: D-056 supersedes this initial sparse-hole mechanism interpretation.
  Sparse Mathlib artifacts can allocate their holes as verifier access
  proceeds. On tmpfs that allocation is charged to node memory; on the node's
  566-GiB disk-backed overlay it is ordinary local disk usage. This operational
  relocation changes no verifier bytes, Lean verdict, worker cap, model, data,
  prompt, seed, proposal budget, or analysis factor. Lowering concurrency would
  neither eliminate the accumulating staging defect nor preserve the required
  throughput within the 23-hour allocation.
- Consequence: fresh C1 retry8 and C0 retry3 use runner SHA-256 values
  `4a53a037576a325aceecea8afaaea137567d959f38f478f9b2eeac39db2b2772`
  and `8d975b5dcd54a30abf678a0089fc3bbd5a140d77bb0d446b6781b48de739d3b0`
  in retained jobs `868001` and `868076`. Both staged at 4,555,536 KiB on
  disk-backed `/tmp` with roughly 555 GiB free and entered the frozen
  evaluation payload. C1's first completed batch reproduced 318 verifier errors
  and 428 unique proofs exactly; C0's reproduced 333 errors and 508 unique
  proofs exactly. Both verifier trees remained 4.4 GiB and the nodes remained
  near 110 GiB used. Pending C3 evaluation, matched-control evaluation, and
  C5 runners have SHA-256 values
  `dc4090d46f2537aae1c9742232941b97d8dde2d43529b9224c95b8edf1806f1d`,
  `2dbc8208e357cd3dd6cdd48e69cec2f98ee2752cacacaca3652eb4de21f39eff`,
  and, after D-055's telemetry-denominator correction,
  `0683a7c6eb8b97b0713015027f61d39d5328188c7f9a7085288e497a0c56b07b`.
  The active matched-control training run remains unchanged because it is
  healthy and already past the observed failure boundary; its verifier tree
  and node memory continue to be monitored. Jobs `868228` and `868264` are
  watched by persistent self-attach processes bound to immutable copies of
  their respective checksummed runners, preserving the requested retained
  `sleep infinity` workbench behavior while preventing an unattended start
  from losing useful allocation time.

### D-054 - Freeze the C5-versus-C3 training analysis before full C5 output

- Date: 2026-09-01
- Decision: analyze the eligible complete C5 run directly against finalized
  C3 with a new fail-closed script, `scripts/project/analyze_c5_training.py`.
  Freeze the panel before any eligible C5 proof snapshot exists: overall raw
  correct tactic-signature and exact-proof coverage; paired theorem-level
  correct, mode, concentration, and effective-mode differences; rarefaction at
  1, 2, 4, 8, and 16 correct draws; archived-dominant-mode concentration;
  archive-eligible and ineligible strata; 100-step chronological windows; C0
  modes absent from C3 but observed in C5; blocked/reward-rejected counts,
  skipped prompts, and update volume.
- Input gate: require the frozen C0 archive, finalized registered full C3, and
  finalized `exploratory_full_seed42_h100` C5. Both training runs must contain
  308,960 registered and 308,992 physical proposals with identical theorem
  identities and the upstream completion marker. Require C3 to contain
  positive zero-advantage blocking and no reward rejection; require every C5
  blocked correct proposal to be reward-rejected and none to be zeroed after
  normalization. Refuse to overwrite an existing analysis artifact.
- Material-support rule: classify stronger exploration as materially supported
  only if C5 improves expected tactic-mode coverage by at least 5% at exactly
  16 correct draws, reduces paired archived-dominant share by at least 0.05,
  and loses no more than 0.05 absolute correct rate. Positive rarefied coverage
  and negative dominant-share deltas below those thresholds count only as
  directional support. A nonpositive rarefied delta or nonnegative dominant-
  share delta does not support the stronger intervention.
- Evidence: four focused C5-analysis tests cover delta direction, archived-mode
  suppression, intervention contamination, and decision boundaries. All 49
  project tests pass. Generalizing the existing training loader to accept one
  explicit expected classification preserves its registered default and
  reproduces the complete committed C1/C3 overall, rarefaction, and C0-recovery
  panels exactly.
- Consequence: after job `868636` passes full finalization, write the frozen
  output to `results/c5_vs_c3_training_seed42.json` and report the rule's
  classification before deciding whether held-out C5 evaluation is warranted.
  Training-rollout findings alone do not establish held-out improvement, and
  tactic-head signatures remain operational proxies rather than semantic
  mathematical methodologies. Dependent job `868637` pins analysis commit
  `39ba50d` and runner SHA-256
  `9d9f013486f90ebdff9957b8b286f77809eea1b48ccdb8d7f128332f429c418b`;
  its `afterok:868636` dependency prevents any artifact if full C5 finalization
  or validation fails.

### D-055 - Correct the C5 telemetry denominator before allocation

- Date: 2026-09-01
- Decision: correct the full-run terminal gate before the queued job receives
  hardware. Keep proof-level finalization responsible for all physical proposal
  and blocked-proof accounting; compare the per-step `[HARD_BLOCKING]`
  categories with `update_batch_samples`, the population on which those
  advantages are computed. Continue to require 604 summaries, all three
  learning categories, reward rejection for every physically blocked correct
  proof, no post-normalization zeroing, and the expected advantage signs.
- Evidence: trainer control flow removes uniform prompt groups before
  concatenating the update batch and computing advantages. In the excluded
  H200 diagnostic, step 1 generated 512 physical proposals but its telemetry
  categories summed to 416, exactly the retained update volume; step 2 summed
  to 320 against 512 physical proposals, again exactly the retained update
  volume. The prior wrapper's comparison with 512 would therefore reject a
  scientifically valid completed run after training.
- Consequence: pending jobs `868606` and `868631` were cancelled with zero
  runtime and no allocated node, so the eligible directory remained pristine.
  Full run `868636` uses corrected immutable runner SHA-256
  `0683a7c6eb8b97b0713015027f61d39d5328188c7f9a7085288e497a0c56b07b`;
  dependent frozen-analysis job `868637` is bound by `afterok:868636`. This
  changes only validation of already-emitted telemetry, not the model, data,
  seed, optimizer, intervention, proposal budget, or analysis rule.

### D-056 - Disable verifier core dumps and retain disk containment

- Date: 2026-09-01
- Decision: set the core-file limit to zero for every live process in C0
  retry3, C1 retry8, and matched-control training, including the Ray main tasks
  and existing Lean workers. Make pending C3 and matched-control evaluators
  inherit the same zero limit through their persistent self-attach wrappers.
  Attach a fail-closed watcher to pending C5 job `868636` that reapplies the
  limit to all job processes throughout staging and initialization, before any
  Lean worker can start. Retain disk-backed `/tmp` staging as an independent
  containment layer.
- Evidence: the authoritative verifier occupies about 4.3 GiB and its largest
  tree, `mathlib4`, is about 4.0 GiB by apparent size; the `.lake` tree is only
  about 3.9 GiB apparent. An initially 4.4-GiB copy therefore cannot become
  566 GiB by filling pre-existing sparse holes, superseding D-053's causal
  interpretation. On all three active nodes, `Max core file size` was instead
  `unlimited`, the kernel core pattern was `core.%h.%e`, PID suffixing was
  enabled, and Lean REPL workers occupy multiple GiB each and are repeatedly
  terminated or restarted by the verifier pool. Accumulated process dumps are
  therefore a mechanism consistent with both the location and scale of the
  removed job-local trees. The failed trees were deleted before this audit, so
  no surviving filename directly proves the mechanism; the limit is a
  fail-safe against the identified risk, not a relabeling of inference as fact.
- Safety check: `prlimit` updated 341 processes in C1, 339 in C0, and 279 in
  the matched control. `/proc/<pid>/limits` then reported zero soft and hard
  core size for each sampled Ray main task and Lean REPL. The running verifier
  trees remained 4.4 GiB, first-batch scientific outputs stayed exactly
  reproducible, and no model or verifier process was restarted.
- Consequence: C3 and matched-control watcher SHA-256 values are
  `51e9ea5d7e7efd6508f6ebd0ffb61a96148419e490e96ff19e693842545bb8ce`
  and `5176e7b1b8f0e641ae8e874004f8fc74f8abec6e4fd1772715cae4a2a12aa55f`;
  both launch their existing immutable runners under `prlimit --core=0:0`.
  C5 core-limit watcher SHA-256 is
  `cf6a05f6406bfb1e473a6a0ede7683c495c86b976f1e8972c9ba0b1fd3186b85`.
  Core dumps are crash diagnostics only: disabling them changes no Lean
  verdict, timeout, worker count, model, data, seed, optimizer, proposal, or
  registered analysis factor.
- Post-change stress boundary: C1 retry8 completed batch 4 with the exact
  historical 273 verifier errors and 1,659 cumulative unique proofs, peaking
  at 583,052,864 KiB used before returning to about 109 GiB. C0 retry3 completed
  batch 4 with the exact historical 1,998 cumulative unique proofs and one
  timing-sensitive verifier-error difference, 323 versus 324, peaking at
  545,911,400 KiB before returning to about 111 GiB. Neither verifier tree
  exceeded 4.4 GiB and neither run emitted a Ray, socket, or space error. This
  is operational recovery evidence, not a substitute for complete registered
  finalization.
- Former failure boundary: C1 retry8 subsequently completed batch 32 in
  534.5 seconds with 395 verifier errors and 12,501 cumulative unique proofs,
  peaking at 530,529,524 KiB used. C0 retry3 completed batch 32 in 545.7
  seconds with 499 verifier errors and 15,830 cumulative unique proofs, peaking
  at 474,690,440 KiB used. Both returned near 110 GiB used; both verifier trees
  remained exactly 4,555,536 KiB allocated/apparent; sampled Lean workers
  retained zero core limits; and both logs contained zero fatal, space, or OOM
  signatures. This directly crosses the prior retry boundary without changing
  scientific inputs, but complete finalization remains required.

### D-057 - Trigger the frozen pass@128 analysis from finalized artifacts

- Date: 2026-09-01
- Decision: wait for eligible finalized C0 retry3, C1 retry8, and C3 retry2
  pass@128 artifacts, then run the unchanged D-038 comparison and accumulation
  panel from execution snapshot `8dc7563`. Publish
  `results/registered_c0_c1_c3_seed42_pass128.json` and
  `results/registered_c0_c1_c3_seed42_pass128_accumulation.json` only after
  both analyses succeed and their terminal invariants pass. This is execution
  of the preregistered panel, not a new experiment or post-result metric.
- Reason: the three evaluations finalize inside retained `sleep infinity`
  allocations, so their Slurm jobs do not provide usable `afterok` completion
  semantics. A result-driven watcher removes avoidable analysis latency without
  changing or observing the panel before the result exists.
- Guards: require a zero runner exit and finalized `metrics.json` for every
  condition. The frozen accumulation loader independently checks condition,
  `registered_evaluation_128` classification, upstream completion sentinel,
  59,776 registered proposals, 59,904 physical proposals, excluded padding,
  proof-log hash, evaluation-parquet hash, theorem identity, and recomputed
  pass@K/full-sample metrics. The wrapper additionally requires 128 samples per
  theorem and the registered combined-parquet SHA-256, writes both outputs to
  temporary paths, and moves neither into place unless all checks succeed.
- Evidence: before any required run had finalized, the runner exited 2 on the
  first missing `metrics.json` and created neither target artifact. Frozen
  runner SHA-256 is
  `5a38c0527cb60b196bf0dd8680e513b7717c38e29b0596dc5f546fc657594316`;
  persistent watcher SHA-256 is
  `d4c4b33b2cd3e131fe6715d3f11de896e026188c0b8bf9bf3fe13ba45cd20837`.

### D-058 - Trigger both frozen matched-control panels from finalization

- Date: 2026-09-01
- Decision: execute the unchanged D-040 training panel as soon as matched-
  control training finalizes, and execute the unchanged D-041 held-out panel
  once both C3 and matched-control pass@128 evaluations finalize. Use analysis
  snapshot `8dc7563` and publish atomically to
  `results/c3_vs_matched_control_training_seed42.json` and
  `results/c3_vs_matched_control_heldout_seed42_pass128.json`. These watchers
  execute preregistered decision rules; they add no experiment or metric.
- Training guards: require zero execution status and finalized metrics for the
  control and completed C3, identical theorem identities, complete registered
  full-run accounting, zero control intervention counters and archive, the
  frozen C3 archive hash, and exactly 1,014 archive-eligible theorems. Validate
  the registered decision classification before moving the temporary output.
- Held-out guards: require zero execution status and finalized metrics for
  both evaluations, matched theorem identities, 128 samples per theorem,
  identical registered parquet hash, and exact recomputation of pass@K and
  full-sample metrics. Validate all three dataset panels and source conditions
  before moving the temporary output.
- Evidence: with control training and control held-out metrics still absent,
  both runners exited 2 at their first missing finalized input and created no
  target artifact. A subsequent pre-start audit caught that file-form
  `mktemp` would pre-create the temporary output and trigger the analyzers'
  overwrite refusal; both wrappers now create a private directory and pass a
  nonexistent child path, preserving atomic publication. Corrected training
  and held-out runner SHA-256 values are
  `6578b1f5f97a2e47e512190e14f01a954c77b6fe836f957ddcd190edff14a828`
  and `b1a25cfa3470bfe831ef68e85ec29d3cb5d329ae0b4bb4cd9d41edf68bf2dec7`;
  their restarted persistent watcher SHA-256 values are
  `5a7baddc73009fb85644874dbfd2128134b8c4ef3f8818cef3fe45289e66ab0a`
  and `2acb4f88321646aa9d43573d50fec2ce52e8e041f2d99f67eee8c38e0b193ee2`.

### D-059 - Publish the frozen C5 analysis atomically at its registered path

- Date: 2026-09-01
- Decision: supersede dependency-blocked C5 analysis job `868637` before
  allocation. Continue to execute analysis snapshot `39ba50d` only after full
  C5 job `868636` succeeds, but write first to a private temporary directory,
  run the terminal source/classification/archive checks there, and move the
  result and log into place only after the entire pipeline succeeds. Publish
  the result to the D-054-registered path
  `results/c5_vs_c3_training_seed42.json`, not the C5 run directory.
- Reason: the prior wrapper passed the final output path directly to the
  analyzer before the wrapper's terminal assertions. An assertion failure
  could therefore leave a valid-looking but ineligible JSON file and block a
  clean retry. It also targeted the run directory despite the registered
  repository result path. Neither issue affects the frozen analysis itself.
- Evidence: the corrected runner fails closed with exit 2 while finalized C5
  metrics are absent and creates neither final result nor final analysis log.
  Old job `868637` was cancelled with zero runtime and no node. Corrected
  immutable runner SHA-256 is
  `5416e9f6dc8225fd06acd1e2f9f298b77611b73146fcc8fd03ac486241cba062`;
  submission-script SHA-256 is
  `178e80a93ebe839d78d47cee2b827e0947b7f6b7dad7e16407fe475ed282987e`.
  Replacement job `868700` is dependency-bound by `afterok:868636`.
- Scope: this changes only output transactionality and path consistency. The
  C0 archive, C3/C5 inputs, metrics, material-support thresholds, analysis
  snapshot, and full C5 experiment are unchanged.

### D-060 - Continue C5 after a measured step-20 runtime gate

- Date: 2026-09-01
- Decision: keep full C5 job `868636` running unchanged after measuring its
  first 20 completed optimizer steps. Do not restart, change verifier workers,
  reduce timeouts, alter checkpoint cadence, or change any scientific setting.
  Continue monitoring the rolling completion margin against the existing
  23-hour allocation.
- Motivating observation and question: through step 7, C5's matched batch
  positions were consistently 15--26 seconds slower than the no-blocking
  control, leaving little projected wall-time margin. The control also had a
  357.6-second verifier tail at step 18. The preselected operational question
  was whether C5 would traverse that stress position and retain a positive
  completion margin by step 20.
- Evidence: C5 completed step 18 in 137.1 seconds and step 20 in 128.2 seconds.
  Across steps 1--20, mean time was 131.46 seconds, median time was 130.34
  seconds, maximum time was 158.0 seconds, and the last-ten mean was 129.30
  seconds. At job runtime 49 minutes, the all-step mean projected 21.33 hours
  for the remaining 584 steps against about 22.18 allocation hours remaining,
  a roughly 51-minute wall-clock margin. The last-ten estimate provided a
  larger margin. An attempted scheduler-only extension to the partition's
  24-hour ceiling was permission-denied and changed no job state.
- Scientific and safety gate: all 20 completed telemetry records matched their
  corresponding metrics. Blocked-correct equaled reward-rejected in every
  batch; intervention-category counts summed to the update volume; every
  nonempty blocked-correct mean advantage was negative; and every nonempty
  alternative-correct mean advantage was positive. The checkpoint accounts for
  7,840 update rollouts and 418 blocked correct rollouts. No fatal log signature
  appeared, and the disk, memory, and zero-core safeguards remained healthy.
- Consequence: continuing the already-valid trajectory is less disruptive and
  better supported than restarting from a runtime projection. No full C5
  scientific result exists until all 604 steps and finalization gates pass.

### D-061 - Pre-register a fail-only 24-hour C5 operational retry

- Date: 2026-09-01
- Decision: leave valid primary C5 job `868636` completely unchanged, but
  prepare one fresh 24-hour retry that Slurm may release only if the primary
  exits unsuccessfully. Job `869096` is dependency-bound by
  `afternotok:868636`; it is not a parallel replicate and cannot consume an
  allocation after primary success. If released, restart the identical frozen
  condition from the pristine base actor in a new directory with no rollout,
  optimizer, actor, buffer, verifier, or node-local state from the primary.
- Trigger evidence: step 25 reached the registered 300-second Lean verifier
  tail and completed in 385.799 seconds, comparable with the matched control's
  397.892-second maximum. It remained scientifically valid: all 15 blocked
  correct rollouts were reward-rejected, blocked mean advantage was negative,
  alternative-correct mean advantage was positive, and no resource or fatal
  error appeared. This single tail does not justify interrupting the valid
  trajectory, but it demonstrates that ordinary verifier variance can consume
  the primary's measured sub-hour completion margin.
- Frozen retry: directory
  `c5-reward-reject-full-20260901-seed42-a0f1235-h100-workers32-retry1-24h`
  contains only prepared metadata and fresh copies of the registered train,
  validation, and archive inputs with SHA-256 values
  `502d3216ced1829a996869fe31400cece726ac83e0fb469bda0cd9d79961382a`,
  `05f6176ec4ca85bff8368c64a09049c0e0dad84b1dd3741ace1f8e7de1b35b15`,
  and `fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3`.
  It pins execution snapshot `a0f1235`, 604 steps, 308,960 registered
  proposals, four H100s, 32 verifier workers, `reject_reward`, disk-backed
  verifier staging, zero inherited core limits, and runner SHA-256
  `f3173640a30f7cdcada9a74dfbc66b364c5164c56c70dc2f9b333e98176717dd`.
  A no-allocation preflight exits 2 before writing any run artifact.
- Analysis routing: primary analysis job `868700` remains `afterok:868636`.
  Fallback analysis job `869097` is `afterok:869096`, pins unchanged analysis
  snapshot `39ba50d` through runner SHA-256
  `1225a33f3a84fa531ff7a5ca5445dc067378d68f5f6af75e17cf5700c84ec264`,
  and publishes the same registered result atomically. Its preflight exits 2
  while fallback metrics are absent and creates no result or log. Never
  combine primary and retry samples or select between two completed runs:
  Slurm's mutually exclusive success/failure dependencies predesignate which
  single path is eligible.

### D-062 - Validate C5 intervention telemetry by optimizer update

- Date: 2026-09-01
- Observation: dynamic update buffering does not perform an optimizer update
  on every dataloader step. In the live primary, step 28 retained 224 proofs,
  below the 256-proof update threshold. Step 29 retained another 480 and made
  one 704-proof optimizer update. The log therefore correctly contained 29
  data-step records but only 28 `[HARD_BLOCKING]` summaries. The original
  operational wrapper's requirement for exactly 604 summaries was false and
  would reject a scientifically complete run after finalization. Its second
  equality was also too broad when the last step leaves a sub-threshold buffer:
  finalized `update_batch_samples` counts all retained samples, while telemetry
  describes only samples actually passed to an optimizer update.
- Decision: leave primary training job `868636`, its process tree, execution
  snapshot, and scientific configuration untouched. Validate telemetry by
  reconstructing ordered `Step train batch size` and `Update train batch size`
  events. Require every update to consume the full accumulated buffer, exactly
  one intervention summary per optimizer update, exact three-category coverage
  of each update, all 604 retained-sample steps, agreement between retained
  samples and finalized metrics, and at most 255 samples in a final unoptimized
  residual buffer. Preserve the signed aggregate-advantage gates.
- Evidence: validator snapshot `5a9ef4a` has focused tests for the observed
  224-plus-480 buffering case, excess summaries, and incomplete category
  accounting. Eleven targeted validation, intervention-telemetry, and frozen
  C5-analysis tests pass. Applied to the growing primary log, it reconstructs
  update and residual volumes exactly. This changes no proof, reward,
  advantage, optimizer update, or scientific result.
- Recovery routing: superseded fail-only jobs `869096` and `869097` were
  cancelled at zero runtime. Replacement job `869132` remains dependency-bound
  by `afternotok:868636`. If the primary reaches the step-604 checkpoint,
  proof snapshot, finalized metrics, and every corrected validation gate but
  exits nonzero only at its stale wrapper assertion, the replacement writes an
  atomic `recovery_validation.json` and exits without retraining. If those
  gates fail, it starts the already-registered pristine retry. Dependent
  replacement analysis job `869143`, dependency-bound by `afterok:869132`,
  selects the primary only through a validated recovery record; otherwise it
  analyzes the retry. The immutable training/recovery and
  analysis runner SHA-256 values are
  `e248e119027232670fb0dbea124714c8a36565b7c6872e9d7eb6c6bcc261caa6`
  and `e075e4bd70aeaaca202dccf5ad1f5d17009be09cb0d72c675229eeeaa0a9da27`.
  Primary success still routes normally through analysis job `868700`.

### D-063 - Continue C5 after the step-40 runtime and mechanism gate

- Date: 2026-09-01
- Decision: continue primary job `868636` unchanged. Preserve the 23-hour
  allocation, four H100s, 32 Lean workers, 300-second verifier timeout,
  checkpoint cadence, seed, proposal budget, and C5 intervention. Keep
  fail-only recovery/retry job `869132` and analysis jobs `868700`/`869143`
  dependency-blocked exactly as registered.
- Runtime evidence: steps 1--40 averaged 134.678 seconds with a 127.592-second
  median and one 385.799-second timeout tail. At 1:35 elapsed, applying the
  all-step mean to the remaining 564 steps projected about 21.10 additional
  hours against about 21.42 hours remaining, a roughly 18-minute margin. The
  last-ten mean was 124.426 seconds and projected about 19.49 additional hours,
  a roughly 1.9-hour margin. The last five steps averaged 122.292 seconds.
- Mechanism evidence: 40 dataloader steps produced 39 optimizer updates because
  one sub-threshold step was correctly buffered into its successor. All 14,912
  optimized samples reconciled exactly with 39 telemetry summaries. The 808
  blocked correct proofs had weighted mean advantage -0.656, 9,280 alternative
  correct proofs had +0.543, and 4,824 incorrect proofs had -0.935. No fatal
  log signature appeared, and node memory still had about 587 GiB available.
- Interpretation: the intended exploratory pressure is active and signed in
  the required direction, while the primary remains scientifically and
  operationally valid. These are runtime gates, not a full C5 result or a
  substitute for the frozen D-054 comparison after step 604.

### D-064 - Protect matched-control completion and accept the registered sentinel

- Date: 2026-09-01
- Observation: matched-control job `868049` completed 116/604 steps in 4.63
  measured step-hours and 4.77 allocation hours. Its 143.8-second mean cannot
  be extrapolated uniformly because the completed seed-42 C1/C3 runs had
  materially faster remaining schedules: their steps 117--604 averaged 115.4
  and 115.8 seconds. However, scaling those schedules by the observed
  destination 32-worker slowdown left only roughly 10--20 minutes of primary
  allocation margin. A second audit found that the frozen training-analysis
  wrapper incorrectly required process status zero even though completed C1
  and C3 both record exit `1` as the upstream post-completion sentinel.
- Decision: do not interrupt or alter the valid primary. Submit one 24-hour
  training-only fallback, job `869225`, dependency-bound by
  `afterany:868049`. When released, it must first validate a completed primary
  through analysis snapshot `8dc7563`, including condition, classification,
  completion marker, exact 308,960 registered and 308,992 physical proposals,
  proof-log hash, theorem coverage, zero intervention counters, no archive,
  and a `global_step_604` actor. A valid primary produces an atomic recovery
  record and exits before retry setup; only failed validation starts the same
  control from the pristine base actor in fresh directory
  `c3-matched-control-full-20260901-seed42-8dc7563-workers32-retry1-24h`.
- Resume exclusion: the released FSDP checkpoint writer persists actor weights
  and tokenizer files but not optimizer or scheduler state. Cross-allocation
  resume would therefore change the training trajectory and is scientifically
  ineligible. The fallback is a complete fresh replay, not a continuation or
  pooled replicate.
- Frozen factors and guards: the retry pins execution snapshot `8dc7563`, seed
  42, pristine base actor/reference, registered train/validation hashes
  `502d3216...` and `05f6176e...`, 308,960 proposals, four H100s, 32 Lean
  workers, unchanged optimizer/configuration, disk-backed 4.3-GiB verifier
  staging with a 10-GiB gate, zero core limits, and 24-hour maximum wall time.
  Runner SHA-256 is
  `2120c329c85ffa12bc0b43a50dfc9bc8069771b90c2e3631e0221e256dd06430`;
  submission-script SHA-256 is
  `0868ca140ca11adff7da3e19ed5cdde3b578268e5eb10f7fe5c016183cb4073a`.
  Its no-allocation preflight exits 2 without writing a run artifact.
- Analysis gate correction: replace the stale persistent training-analysis
  watcher with a version that treats exit `1` as the exact registered sentinel,
  waits for `metrics.json`, and then executes the unchanged atomic D-040 panel.
  Corrected analysis runner and watcher SHA-256 values are
  `da060659458061d812aeb09e6e2753682bdd85a879ac03d7eb2cc92b6ae6e069`
  and `bb1babac837a1c74ff490d8866e3a872c6351aa26886d0093d8aa542e8cf4dc2`.
  This changes no analysis metric or decision rule. If the fresh retry becomes
  necessary, its downstream training/evaluation routing must be registered
  before consuming those artifacts.

### D-065 - Recognize the registered sentinel across frozen evaluations

- Date: 2026-09-01
- Observation: the same stale process-status assumption corrected for the
  matched-control training analysis in D-064 was present in the frozen joint
  pass@128 and matched-control held-out analysis wrappers. Completed eligible
  evaluations consistently record exit `1` only after writing their finalized
  metrics and completion artifacts because the upstream launcher raises its
  registered post-completion stop exception. Requiring exit zero would reject
  scientifically valid outputs without testing their actual completion gates.
- Decision: change only the orchestration gate for those two analyses from
  exit zero to the exact registered sentinel exit `1`. Continue to require
  `metrics.json` and all pre-existing frozen proposal, proof-log, parquet,
  classification, completion, and condition checks before either analysis may
  publish. The D-038 joint pass@128 panel and D-041 matched-control held-out
  panel, their metrics, decision rules, and eligible run directories remain
  unchanged.
- Frozen operations: sentinel-aware joint pass@128 runner and watcher SHA-256
  values are
  `b2427e349c5c08ffa19bfa1f8a76c84d1c3f6f170d04741193195d562089516a`
  and
  `ce9190dc0325615272097e455dd805a94d03b5189e36bc7bdfe66acf72b5249d`.
  Sentinel-aware held-out runner and watcher SHA-256 values are
  `3e7b7e912d76be4d1305037e31ecc07142bd0bcd8e2b2095396f80a898f430d5`
  and
  `8f86fbfe3c101d72466a78be156dd762e9de25ddbe62187a58da240104335575`.
  Both runners fail closed with status 2 while required metrics are absent.
  Stale watcher processes were stopped; replacement watchers `3929611` and
  `3929612` are live. This correction changes no training or evaluation
  process and creates no result before its registered inputs finalize.

### D-066 - Release the 24-hour C5 retry on a runtime-only gate

- Date: 2026-09-01
- Observation: C5 primary job `868636` had completed 45 visible valid steps when
  the runtime decision was made, after about 1:50,
  including registered 300-second verifier tails at steps 25 and 44. Step 44
  took 346.379 seconds and step 45 returned to 116.108 seconds. The 45-step
  mean was about 139.07 seconds, which projected beyond the remaining 23-hour
  allocation. A schedule-matched estimate was more discriminating: compose
  the 1.157 destination matched-control/C3 slowdown measured through 123
  steps, the 1.020 C5/matched-control ratio measured through 45 paired steps,
  and the exact completed C3 schedule after step 45. It projected 21.54 more
  hours, or about 23.38 total allocation hours—roughly 23 minutes beyond the
  primary limit but 37 minutes inside the preregistered retry's 24 hours.
- Decision: stop primary job `868636` based only on this wall-clock gate,
  before any complete proof snapshot, finalized metrics, or D-054 result
  existed. Permanently exclude its 46-step partial directory and never resume, pool,
  or select its partial samples. Release already-registered pristine retry job
  `869132` through its `afternotok` dependency; preserve execution snapshot
  `a0f1235`, seed 42, 308,960 proposals, base actor/reference, 32 verifier
  workers, optimizer, archive, and all validation and analysis gates.
- Scheduler evidence: step 46 completed in 115.546 seconds and its log flush
  raced with the cancellation request; all 46 partial steps are ineligible.
  Slurm recorded primary cancellation at
  2026-09-01T03:22:50-04:00 after 1:50:33, automatically cancelled zero-runtime
  primary analysis job `868700`, and made retry `869132` eligible at 03:22:57.
  The released `trig0008` node was then independently marked `IDLE+DRAIN` by
  the root health check for unresponsive `nvidia-smi`; retry `869132` remains
  pending for a healthy full H100 node, with analysis `869143` still
  dependency-blocked. The node recovered at 03:25 and a higher-priority job
  immediately acquired it; Slurm's current retry estimate is 08:58. This
  node-health and queue state is operational evidence only and did not motivate
  the pre-result runtime decision.
- Rationale: continuing the primary had a schedule-matched projection outside
  its hard limit, while restarting at this gate maximizes the only eligible
  24-hour trajectory's completion margin. The retry is not a replicate and no
  scientific output was observed or used to choose between runs.

### D-067 - Release the 24-hour matched-control retry on a runtime-only gate

- Date: 2026-09-01
- Observation: matched-control primary job `868049` completed step 130 after
  18,655.317 measured step-seconds. The exact completed C3 schedule used
  15,864.119 seconds through the same positions, giving a cumulative
  destination/control slowdown of 1.175944. Applying that observed ratio to
  C3's exact remaining 55,259.420-second schedule projects another
  64,981.988 seconds and about 23.36 total allocation hours including elapsed
  startup overhead—roughly 21 minutes beyond the primary's 23-hour hard
  limit. Ratios over the last 80, 40, and 20 paired positions were 1.214,
  1.424, and 1.560, so the cumulative estimate is not made pessimistic by a
  recent speedup. A request to extend the running job to the partition's
  24-hour ceiling was permission-denied and changed no job state.
- Decision: stop primary job `868049` based only on this preregistered
  wall-clock question, before any step-604 checkpoint, proof snapshot,
  finalized metric, or D-040 analysis exists. Permanently exclude its partial
  trajectory and never resume, pool, or select its samples. Release frozen
  fallback job `869225` through its `afterany:868049` dependency. The fallback
  first validates a complete primary and can only start a full pristine replay
  when validation fails; the actor, optimizer, scheduler, and rollout buffer
  all start fresh.
- Preserved factors: execution snapshot `8dc7563`, seed 42, pristine base
  actor and reference, train and validation data, 308,960 registered
  proposals, optimizer/configuration, four H100s, 32 Lean workers, zero core
  limits, disk-backed verifier staging, finalization gates, and the frozen
  D-040 analysis are unchanged. Immutable fallback runner and batch SHA-256
  values remain
  `2120c329c85ffa12bc0b43a50dfc9bc8069771b90c2e3631e0221e256dd06430`
  and
  `0868ca140ca11adff7da3e19ed5cdde3b578268e5eb10f7fe5c016183cb4073a`.
  This retry is not a replicate; no scientific result was observed or used to
  choose between trajectories.
- Scheduler evidence: Slurm cancelled primary `868049` at
  2026-09-01T03:41:52-04:00 after 5:20:03 and cleared the fallback dependency
  shortly afterward. Job `869225` is eligible with a 24-hour limit and a
  current estimated start near 09:38. The primary has no finalized metrics,
  final proof snapshot, or step-604 actor and remains excluded.

### D-068 - Route matched-control consumers through the eligible retry

- Date: 2026-09-01
- Observation: D-067 makes the fresh job `869225` the only trajectory eligible
  to produce the matched-control actor. The existing D-040 analysis watcher,
  delayed held-out job `868264`, and D-041 analysis watcher are bound to the
  now-excluded primary directories. Leaving those routes unchanged would
  either wait forever or spend a full-node allocation that cannot find an
  eligible actor.
- Decision: cancel delayed held-out workbench `868264` before allocation and
  stop only its exact launcher. Submit a replacement retained 23-hour
  four-H100 workbench dependency-bound by `afterok:869225`, evaluating the
  retry's `global_step_604` actor in fresh directory
  `eval128-c3-matched-control-20260901-seed42-8dc7563-workers32-retry1-training`.
  The evaluator remains snapshot `8dc7563`, 467 frozen theorems, 128 proposals
  per theorem, seed 42, no update, no evaluation-time blocking, 32 Lean
  workers, disk-backed verifier staging, and the exact registered parquet hash
  `f9fb4d92b529499fa684f81a01a51249a2b9e1736cf50412ca374f11dbf4d840`.
- Frozen evaluation routing: wrapper SHA-256
  `132b66d85e04f59f311f00f475abc34da9acd8b1233b0e4acd0ffeee0e6e527f`
  verifies base evaluator `2dbc8208...`, substitutes only the eligible
  training directory, fresh evaluation directory, and scheduling label, and
  requires resulting evaluator SHA-256
  `bca5c14fe77ad5dbab851832242fdd9abcc9da0cec240ca9691e70985d83282a`.
  Its no-allocation preflight exits 2 before creating any evaluation artifact.
- Frozen analysis routing: replace only the stale persistent D-040 and D-041
  watchers. Retry-bound training-analysis runner/watcher SHA-256 values are
  `5eae4e0c33a332522717c7a4c2ce246b85eed6bba57f7b8c3d51d629e421cad5`
  and
  `e01c0269e242c5af41f75bac8a9353126e75badac6094aaf81199eee1d4b1872`;
  held-out runner/watcher values are
  `ab9bb5bd06110f72416e6c6ccff5a32a8ddffa3a123592d02b3643705931ee4f`
  and
  `a7593810f7fc2865260ff107e1c2947d446caf55305cf66ef4004ee76978fcda`.
  Each runner verifies its frozen base and exact materialized checksum, fails
  closed while eligible metrics are absent, and executes the unchanged D-040
  or D-041 panel after exact sentinel exit `1`. No metric or decision rule is
  changed.
- Scheduler evidence: old held-out job `868264` was cancelled at
  2026-09-01T03:48:10-04:00 with zero runtime. Replacement job `869396` is
  dependency-bound by `afterok:869225` for a retained 23-hour full-node
  allocation. Retry-aware training and held-out analysis watchers are live as
  processes `877` and `878`; the stale launcher and primary-bound analysis
  watchers were stopped. The independent pass@128 watcher remains unchanged.

### D-069 - Release retained pass@128 nodes only after registered analysis

- Date: 2026-09-01
- Observation: jobs `868001`, `868076`, and `868228` are retained workbenches.
  Their payload runners return to `sleep infinity` after finalization, so the
  three complete H100 nodes would remain allocated until their 23-hour limits
  even after the registered pass@128 result exists. C5 retry `869132` and
  matched-control retry `869225` are both pending for complete H100 nodes.
- Decision: attach one fail-closed release watcher that waits for both atomic
  D-038 outputs, then independently validates the comparison classification,
  59,776-proposal budget, frozen parquet hash, exact three eligible run
  directories, sentinel exits, finalized classifications and completion
  markers, and metrics/proof-log SHA-256 values recorded by the accumulation
  result. Only after every check passes may it cancel exact retained jobs
  `868001`, `868076`, and `868228`, with their expected job names verified at
  cancellation time.
- Rationale and boundary: release occurs only after the scientific artifacts
  have already been produced and validated, so it cannot affect proposals,
  verification, metrics, or analysis. It avoids holding up to three idle
  four-H100 nodes that may delay the already-registered full retries. Watcher
  SHA-256 is
  `a9957319de86632adad6142cf4dcd1cbe2e3159ae8d78c90fcd0bd55a7434a6b`;
  a one-second no-result preflight remained waiting, changed no job state, and
  emitted no output.

### D-070 - Release each pass@128 node after independent source validation

- Date: 2026-09-01
- Observation: D-069 unnecessarily holds a completed condition until the
  slowest of three evaluations and joint CPU-only analysis finish. C1's recent
  ten-step mean is about 114 seconds and places it materially ahead of C0 and
  C3. The joint analyzer reads durable shared artifacts and needs no allocated
  GPU node, so retaining a fully validated source cannot improve or repair its
  scientific output.
- Decision: supersede and stop the still-waiting D-069 watcher before any
  cancellation. Replace it with three independent waits in one fail-closed
  watcher. For each condition, require finalized metrics, finalization log,
  exact sentinel exit `1`, condition and registered classification, completion
  marker, 59,776 registered proposals, physical/padding accounting, frozen
  parquet hash, failure-class totals, local proof-line count and SHA-256,
  mode-manifest SHA-256, hardware-record SHA-256, and both dataset keys. Only
  then verify the exact live job ID/name and release that condition's retained
  workbench. Because the frozen finalizer writes `metrics.json` just before it
  updates metadata and prints its terminal JSON record, also wait for that
  exact completion marker in `finalization.log`, require the completion
  appendix to contain the metrics SHA-256, and atomically normalize only the
  stale pre-finalization status line to complete.
- Boundary: source validation occurs only after evaluation finalization, so
  early node release cannot change any proposal or metric. The unchanged
  D-065 joint-analysis watcher continues to wait for all three durable sources
  and publishes the same D-038 artifacts. New release-watcher SHA-256 is
  `137c32e0ceaf64d91e04e05c43f283ac3ea0925d1853a358b00f6aea6fe3a0f6`.
  No output currently exists, so syntax and live-job identity checks are the
  available no-result preflight; the watcher makes no state change before a
  source finalizes.

### D-071 - Preserve the frozen metadata completion transition

- Date: 2026-09-01
- Observation: the frozen training and evaluation finalizers replace the exact
  line `Status: prepared; no result exists yet.` after durable completion.
  Queue-state annotations had customized that first line in the pending C5
  retry, matched-control retry, and retry-derived held-out directories. Their
  eventual metrics would remain valid, but the human-readable status would
  misleadingly remain pending after the finalizer appended its completion
  record.
- Decision: before any of those three jobs starts, restore only the exact
  recognized prepared status line and retain eligibility, dependency, and
  queue state as separate metadata bullets. Do not change any runner, input,
  checksum, scheduler dependency, scientific configuration, or result gate.
- Consequence: the immutable finalizers will atomically make their intended
  status transition after full completion. Current pass@128 runs already have
  live status annotations; D-070 separately waits for their terminal
  finalization records and normalizes those lines only after validating all
  durable source artifacts.

### D-072 - Route the unallocated C5 retry through the available account

- Date: 2026-09-01
- Observation: eligible C5 retry job `869132` remained pending under
  `def-zhijing`, whose user fair-share factor was about 0.042 and whose current
  allocation was heavily used. The same user has an authorized `rrg-zhijing`
  association with a fair-share factor about 7.05 and no current TRES usage.
  The retry had not allocated a node or produced any model-worker artifact.
- Decision: change only job `869132`'s Slurm billing account in place to
  `rrg-zhijing`. Preserve the existing job ID and `afternotok:868636`
  dependency, immutable runner, run directory, input hashes, execution
  snapshot, requested complete four-H100 node, 24-hour limit, and all
  scientific settings. Keep analysis job `869143` dependency-bound to the
  unchanged retry job ID.
- Evidence and boundary: immediately after the transition, Slurm reported
  account `rrg-zhijing`, priority 1,126,546 rather than about 582,824, and an
  estimated start of 06:25:38 on `trig0008` rather than 10:46. Both jobs still
  had zero runtime; the retry directory still contained only the prepared
  metadata and frozen train, validation, and archive inputs. This is an
  operational queue-routing change before allocation, not a change to the C5
  intervention or comparison.

### D-073 - Bound pathological pass@128 verifier concurrency

- Date: 2026-09-01
- Observation: fresh C1 pass@128 retry8 completed 86 of 117 batches and all 86
  verifier schedulers closed normally. In batch 87, however, 32 concurrent
  Lean REPLs each reached about 21--22 GiB RSS. Ray measured 739.19/755.57 GiB
  node memory, killed the main evaluation task, and the immutable finalizer
  refused completion because no proof snapshot existed. Retry8 is therefore
  permanently excluded; its 44,032 completed partial proposals cannot enter
  any registered metric. The retained job `868001` remains live and has about
  15.15 hours available after Ray cleanup returned the node to 731 GiB free.
- Decision: run one fresh retry9 from the same C1 actor, frozen 467-theorem
  parquet, seed 42, 128 proposals per theorem, sampling settings, 300-second
  Lean timeout, verifier, and execution snapshot, changing only operational
  Lean concurrency from 32 to 16. The observed pathological batch projects
  about 350 GiB of concurrent REPL RSS at 16 workers. The first 86 retry8
  batches used 0.249 generation hours and 3.856 verification hours; linear
  16-worker scaling projects 10.83 hours for all 117 batches, leaving about
  4.3 hours of allocation margin at preparation.
- Routing and boundary: the fresh eligible directory is
  `eval128-c1-grpo-default-20260901-seed42-8dc7563-retry9-workers16-disk`.
  Runner SHA-256 is
  `cc88aea5a3c38e9201d3d1623024ed93dcf232c7345479bb45160f8b57093e97`.
  The pass@128 analysis runner changes only the eligible C1 source path and has
  SHA-256
  `a48dee6239e9767069f324063cfbf0642cb9a76286d034abb4aad4041cb32f02`;
  its sentinel watcher SHA-256 is
  `28030377b96517b429e5f445c6a8a440f0a83ac2e2453fedb0535835d2db010c`.
  The per-source release watcher likewise changes only that source path and
  has SHA-256
  `ad4c35fc58d3f6395ab5a41bcf7d9331910e37db7c89fde6c42dc441281f7d6c`.
  Syntax checks and two-second no-result preflights emitted no output and made
  no state change. Worker count does not affect model sampling, but later D-078
  shows that it can move borderline 300-second verifier timeout outcomes;
  proposal and frozen-source gates remain unchanged.
- Five-batch execution gate: retry9 matched retry8 exactly on every recorded
  scientific field for steps 1--5. The batch-4 stress case finalized all 512
  proposals in 1,561.504 seconds and peak recorded node use was 334.93 GiB,
  less than half Ray's retry8 failure reading. The observed first-five verifier
  ratio is 1.5689 rather than the conservative 2.0; projecting it over retry8's
  measured schedule gives 8.57 hours total and about 6.5 hours of hard-limit
  margin. Continue retry9 unchanged.

### D-074 - Admit the pristine C5 retry after startup validation

- Date: 2026-09-01
- Observation: Slurm allocated retry job `869132` on complete H100 node
  `trig0033` at 05:36:52, earlier than its last projected start. The canceled
  primary remained scientifically incomplete, so the fail-only recovery gate
  selected the pre-registered pristine retry rather than reusing any primary
  state.
- Validation: Slurm allocated exactly one node, 96 CPUs, 770,000 MiB, and four
  NVIDIA H100 80GB HBM3 GPUs. Disk-backed sparse verifier staging consumed
  4,555,536 KiB and left about 550 GiB free. The run-local operational runner
  matched SHA-256
  `e248e119027232670fb0dbea124714c8a36565b7c6872e9d7eb6c6bcc261caa6`.
  The resolved configuration passed its built-in validation and retained the
  base actor with resume disabled, seed 42, exact frozen train/validation and
  archive paths, 604 steps, 32 proposals per theorem, 32 Lean workers, two PPO
  epochs, KL coefficient 0.1, rank penalty 0, and `reject_reward` blocking at
  the registered threshold and support floor.
- Decision and boundary: admit job `869132` as the sole eligible complete C5
  retry and monitor its mechanism, accounting, and runtime gates. Analysis job
  `869143` stays `afterok:869132`; no scientific result exists before all 604
  steps, final artifacts, corrected telemetry validation, and frozen analysis
  complete.

### D-075 - Apply the validated pass@128 memory bound to C0 and C3

- Date: 2026-09-01
- Observation: C0 retry3 independently reproduced C1 retry8's exact failure
  boundary. It completed 86 batches, then 32 concurrent Lean REPLs reached
  about 21--22 GiB each in batch 87; Ray failed at 739.24/755.64 GiB and Slurm
  recorded `NODE_FAIL`. No proof snapshot or metric exists, so its 44,032
  partial proposals are permanently excluded. C3 retry2 was at 82 complete
  batches in the same frozen theorem order. Two independent, near-identical
  failures make another 32-worker batch-87 crash predictable rather than an
  informative experiment.
- Decision: stop only C3 retry2's incomplete evaluator, preserve retained job
  `868228`, and start a fresh C3 retry3 there with 16 Lean workers. Submit one
  fresh C0 retry4 as complete four-H100, 96-CPU, 770,000-MiB, 23-hour job
  `870055` under authorized account `rrg-zhijing`, also with 16 Lean workers.
  Preserve each condition's actor, frozen parquet, seed, sampling, verifier,
  300-second timeout, and 59,776-proposal budget; reuse no partial proposal.
  C0 and C3 runner SHA-256 values are respectively
  `2ab937c91dc1657b66129bbc30bcfe230bf6abf7fec6c348596b43d99299ba79`
  and
  `afa15a5c3f3b8ccc0c298a8d542391ad7fce88740acb5e055c6f98def269f9b6`.
- Result routing: reroute the unchanged frozen pass@128 analysis to eligible
  C0 retry4, C1 retry9, and C3 retry3. Analysis runner and watcher SHA-256
  values are
  `252e3b959840d75460233282b3abdcd91dbbb7b227e216fe04328aabe36844ab`
  and
  `47dbba008806261d4b406a4fd6dc88dcae8c433d4a8ec215f9ac4324dc28adda`.
  The per-source release watcher also accepts a not-yet-allocated eligible job
  as pending, but retains every terminal artifact and exact job-name gate; its
  SHA-256 is
  `13251ab7c7da8ba2bb0d90e6b2054255c5bb356e532fb7727e2bc7cac2af2b8a`.
  Syntax checks and two-second no-result preflights were silent. C3 staging is
  live in job `868228`; C0 job `870055` is pending only on resources.

### D-076 - Admit the 16-worker C0 and C3 replays

- Date: 2026-09-01
- Observation: Slurm allocated C0 retry4 job `870055` on complete H100 node
  `trig0045` at 06:03:43, with the exact requested 96 CPUs, 770,000 MiB, four
  H100s, `rrg-zhijing` account, and 23-hour limit. C3 retry3 retained its exact
  job `868228` allocation on `trig0016`. Both staged the verifier at the pinned
  size and launched exactly 16 Lean workers.
- Gate: C0 retry4 step 1 matched excluded retry3 exactly on every recorded
  scientific field, including 319 verifier errors and 481 cumulative unique
  proofs; duration was 373.516 versus 344.071 seconds. C3 retry3 likewise
  matched excluded retry2 exactly, including 304 errors and 487 cumulative
  unique proofs; duration was 373.100 versus 367.894 seconds. Neither run has
  an OOM, worker-kill, traceback, fatal, or stale-result signature.
- Decision: admit both fresh replays and continue unchanged. These exact first
  batches establish matching sampling and ordinary Lean behavior; D-078 later
  qualifies the verdict claim at the timing-heavy batch-4 boundary. No
  registered result exists until all 117 batches finalize.

### D-077 - Continue C5 after the step-22 mechanism and runtime gate

- Date: 2026-09-01
- Mechanism evidence: the corrected validator reconstructed 22 optimizer
  updates and all 8,608 optimized proofs with zero residual. They comprise 464
  blocked correct, 5,417 alternative correct, and 2,727 incorrect proofs, with
  weighted mean advantages -0.708912, +0.557064, and -0.985947. Every nonempty
  category in every update has the registered sign and every summary names
  `reject_reward`. Step records show 465 physically blocked correct proofs and
  465 reward rejections with no mismatch; one all-blocked-prompt proof was not
  optimized, explaining the one-proof difference from update telemetry.
- Runtime evidence: three steps reached the registered verifier-timeout tail.
  Even so, cumulative timed-step cost through batch 22 was 3,455.93 seconds,
  versus 2,888.82 seconds through the same theorem batches in the excluded
  primary: 9.45 minutes of measured excess. Adding that excess to the frozen
  schedule-matched projection of about 23.38 hours yields about 23.54 hours,
  leaving roughly 27 minutes inside the retry's 24-hour allocation. Node memory
  remained healthy and no traceback, OOM, worker-kill, or fatal event appeared.
- Decision: continue eligible C5 retry `869132` unchanged. Preserve the base
  actor, seed, data order, 32 Lean workers, 300-second timeout, intervention,
  optimizer, checkpoint cadence, and all frozen gates. This remains an
  operational mechanism/runtime checkpoint, not a full scientific result.

### D-078 - Match held-out verifier concurrency after timeout evidence

- Date: 2026-09-01
- Observation: C0 retry4 matched retry3 exactly through five batches. C3
  retry3 generated the same cumulative proof-mode totals as retry2, but its
  timing-heavy batch 4 recorded 296 verifier errors rather than 298. Thus the
  worker bound preserves deterministic model sampling, while existing
  300-second Lean timeout outcomes can vary at the margin. C0 and C3 batch-4
  peaks were 329.17 and 344.18 GiB and both returned near 110 GiB in batch 5.
  Their measured schedules project 9.22 and 7.89 hours total.
- Consequence: the eligible registered C0/C1/C3 comparison is operationally
  matched because all three fresh sources use 16 Lean workers. The pending
  retry-derived matched-control evaluation still specified 32, which would
  introduce avoidable verifier-concurrency mismatch in the separate held-out
  C3-versus-control panel.
- Decision: cancel dependency-blocked job `869396` with zero runtime and no
  artifact. Replace it with job `870226`, preserving dependency
  `afterok:869225`, 23-hour complete-node request, eligible training actor,
  frozen parquet, seed, sampling, verifier, timeout, and proposal budget, but
  using 16 Lean workers and a fresh directory. Evaluation runner SHA-256 is
  `7f45fb60d43fa84d2ed9a62e9f99565374c3342a802eaa600027982117cff301`.
  Reroute the unchanged D-041 analysis to the eligible 16-worker C3 and control
  sources; analysis runner and watcher SHA-256 values are
  `8353c8a605dda89c7bb5b95e8c9aac25634ec3d23864e0b3569a0fcd50d1a9c6`
  and
  `27c5805de4af1323d3db532968a6afd58c00e009365760859572bcec1c6cbf08`.
  Outside-allocation and two-second no-result preflights failed closed without
  creating artifacts. Training analysis routing is unchanged.

### D-079 - Continue C5 after the step-40 decision gate

- Date: 2026-09-01
- Mechanism evidence: the corrected buffer-aware reconstruction finds 40
  optimizer updates, 14,944 retained and optimized proofs, and zero residual.
  The optimized categories are 738 blocked correct, 9,516 alternative correct,
  and 4,690 incorrect, with weighted mean advantages -0.730431, +0.538667,
  and -0.978017. Every nonempty category retains the registered sign. All 739
  physically blocked correct proofs were reward-rejected; one all-blocked
  prompt proof was correctly omitted from optimization.
- Runtime evidence: retry timed-step cost through the same 40 seeded batches is
  6,335.553 seconds versus 5,387.128 in the excluded primary, an excess of
  15.81 minutes. Adding that measured excess to the frozen 23.38-hour
  schedule-matched projection yields about 23.64 hours, leaving roughly 21
  minutes inside the 24-hour allocation. Peak recorded node use is 171.03 GiB,
  with no OOM, worker-kill, traceback, or fatal event.
- Decision: continue eligible retry `869132` unchanged. The mechanism remains
  active with exact accounting and the stronger schedule-matched runtime gate
  remains positive. No full C5 scientific result exists before all 604 steps,
  finalization, corrected validation, and frozen analysis complete.

### D-080 - Continue C5 after the step-60 tail-sensitive gate

- Date: 2026-09-01
- Mechanism evidence: the gate was evaluated immediately after step 61 flushed.
  The corrected buffer-aware reconstruction finds 59 optimizer updates, 21,696
  retained and optimized proofs, and zero residual. The optimized categories
  are 1,322 blocked correct, 13,778 alternative correct, and 6,596 incorrect,
  with weighted mean advantages -0.732884, +0.531680, and -0.963707. Every
  nonempty category in every update retains the registered sign and every
  summary names `reject_reward`. All 1,324 physically blocked correct proofs
  were reward-rejected; exactly two were omitted from optimization because
  their prompts had no accepted alternative.
- Runtime evidence: through the complete 46-step prefix shared with the
  excluded primary, retry timed-step cost is 7,104.606 seconds versus
  6,373.761, an excess of 12.18 minutes. Adding that measured excess to the
  frozen 23.38-hour projection gives about 23.58 hours, or roughly 25 minutes
  of allocation margin. A deliberately tail-sensitive alternative scales the
  exact completed C3 schedule after step 61 by the retry/C3 timed-step ratio
  through step 61 (1.205565); including measured startup overhead projects
  about 23.90 hours, leaving only about six minutes. This conservative estimate
  incorporates the consecutive 400.690-, 353.477-, and 341.364-second tails at
  steps 56--58. Peak recorded node use is 171.14 GiB, with no OOM, worker-kill,
  traceback, or fatal event.
- Decision: continue eligible retry `869132` unchanged. Both schedule-matched
  estimates remain inside the hard 24-hour allocation, although the adaptive
  estimate makes the completion margin operationally fragile. Stopping now
  guarantees no eligible result, while changing verifier concurrency, timeout,
  optimizer, data order, or checkpoint policy would invalidate the frozen
  condition. Continue close runtime monitoring; this remains an operational
  mechanism gate, not a full C5 scientific result.

### D-081 - Replace C5 retry 1 after the step-80 runtime gate

- Date: 2026-09-01
- Mechanism evidence: the exact step-80 prefix remains scientifically valid.
  Seventy-seven optimizer updates account for all 27,680 retained proofs with
  zero residual: 1,606 blocked correct, 17,868 alternative correct, and 8,206
  incorrect. Their weighted mean advantages are -0.777064, +0.517784, and
  -0.975359; every nonempty per-update category has the registered sign. All
  1,608 physically blocked correct proofs were reward-rejected and exactly two
  all-blocked-prompt proofs were correctly omitted from optimization. Peak
  recorded node use is 171.45 GiB and no OOM, worker-kill, traceback, or fatal
  event exists.
- Runtime evidence: retry-1 timed-step cost through step 80 is 12,619.066
  seconds versus 9,995.476 seconds through the same seeded positions in the
  completed C3 schedule, a cumulative ratio of 1.262478. Applying that observed
  ratio to C3's exact 61,128.063-second remaining schedule and adding the
  measured 12,942-second allocation prefix projects 25.03 total hours, about
  62 minutes beyond the hard 24-hour partition maximum. This tail-sensitive
  gate supersedes the less informative 46-step common-prefix projection after
  34 additional observed batches. No complete checkpoint, proof snapshot,
  finalized metrics, or C5 scientific result exists.
- Recovery preparation: before stopping retry 1, stage a pristine retry-2
  directory with byte-identical train, validation, and archive inputs; base
  actor/reference; seed; data order; optimizer; 32 proposals; 32 Lean workers;
  300-second timeout; `reject_reward`; and resume disabled. Immutable training
  runner and submission SHA-256 values are
  `115c03dcbdd10020c3d0dc059951ee19bf79bead11731af9ae7526484df0b04a`
  and `d09f3ad773b6738e7f42e4890a617d2642fdb895e2c66c5aab00226c4efbef32`.
  Job `870750` is dependency-bound by `afternotok:869132`; frozen analysis job
  `870751` is bound by `afterok:870750`, with runner and submission SHA-256
  values `94d24cbb26366fb67b8eaaea7b7ac991a1c70499000831b9f5d6209412db0165`
  and `5a16abcbdbbf633a19c0a0831c7e3129c8779e7c3abc4740a01088118372b0ea`.
  Both jobs have zero runtime and unfulfilled dependencies at registration.
- Decision: permanently exclude retry-1 partial state and stop job `869132` on
  this runtime-only gate. Never resume, pool, compare, or select its partial
  samples. Release only the already dependency-bound pristine retry 2 and route
  the frozen D-054 analysis exclusively through its finalized artifacts. This
  is an operational replacement before any C5 result, not an added replicate.
- Scheduler evidence: retry 1 was canceled at
  2026-09-01T09:17:37-04:00 after 3:40:45. Three additional batches flushed
  while the fail-only successor was staged, so the excluded partial ends at 83
  visible steps; finalized metrics and the step-604 checkpoint remain absent.
  Slurm satisfied retry 2's dependency and allocated job `870750` on the
  freshly released `trig0033` node at 09:18:08. Old analysis job `869143` was
  canceled with zero runtime; retry-2 analysis `870751` remains dependency
  bound. Because the replacement received the same physical node, admit or
  reject its runtime trajectory using a first-five-batch timing gate while
  preserving every frozen scientific setting.

### D-082 - Admit C5 retry 2 after the first-five gate

- Date: 2026-09-01
- Configuration evidence: job `870750` records the exact execution snapshot,
  base model, seed 42, train/validation/archive hashes, resume disabled, two PPO
  epochs, KL coefficient 0.1, rank penalty 0, 32 proposals per theorem, 32 Lean
  workers, 300-second timeout, and `reject_reward`. Slurm allocated the exact
  complete-node request: four H100s, 96 CPUs, and 770,000 MiB. Sparse verifier
  staging used 4,555,536 KiB and left 546 GiB free; the run-local runner matches
  SHA-256 `115c03dcbdd10020c3d0dc059951ee19bf79bead11731af9ae7526484df0b04a`.
- Mechanism evidence: four optimizer updates account for all 1,792 retained
  proofs with zero residual: 106 blocked correct, 1,025 alternative correct,
  and 661 incorrect. Weighted mean advantages are -0.692536, +0.634536, and
  -0.872905; every nonempty per-update category has the registered sign. All
  106 physically blocked correct proofs were reward-rejected. Peak recorded
  node use is 172.72 GiB and no fatal signature exists.
- Runtime evidence: retry 2's first five steps cost 608.530 seconds, versus
  893.026 in excluded retry 1, 681.364 in the excluded primary, and 515.047 in
  the completed C3 schedule. Scaling C3's exact remaining schedule by the
  observed 1.181504 retry-2/C3 prefix ratio and adding measured startup projects
  about 23.39 total allocation hours, leaving roughly 37 minutes inside 24.
- Reproducibility qualification: step 1 matches both excluded predecessors on
  every non-timing scientific field. After the first optimizer update, small
  floating-point update differences and later rollout/verifier outcomes
  diverge despite the same frozen seed. Therefore retry 2 is a scientifically
  matched stochastic execution, not a bitwise replay. Its eligibility follows
  solely from the pre-result D-081 runtime gate; no scientific outcome from an
  excluded partial is used to select it.
- Decision: admit retry 2 and continue unchanged under later mechanism and
  tail-sensitive runtime gates. Do not alter node, worker count, verifier,
  timeout, optimizer, data order, intervention, or checkpoint policy. No C5
  scientific result exists before all 604 steps finalize and pass the frozen
  validation and D-054 analysis.

### D-083 - Continue C5 retry 2 under conflicting step-20 projections

- Date: 2026-09-01
- Mechanism evidence: 19 optimizer updates account for all 7,872 retained and
  optimized proofs with zero residual: 404 blocked correct, 4,981 alternative
  correct, and 2,487 incorrect. Weighted mean advantages are -0.664375,
  +0.544863, and -0.983335; every nonempty category in every update has the
  registered sign. All 404 physically blocked correct proofs were
  reward-rejected. Peak node use remains 172.72 GiB and no OOM, worker-kill,
  traceback, or fatal event exists.
- Direct runtime evidence: retry-2 timed-step cost through step 20 is 2,778.915
  seconds, versus 3,208.902 in excluded retry 1 and 2,629.102 in the excluded
  primary. Thus the fresh retry has recovered 429.987 seconds relative to retry
  1 and is only 149.813 seconds slower than the primary through the same
  positions. The most recent ten steps average 127.199 seconds.
- Projection disagreement: adding the direct retry-2/primary prefix excess to
  the frozen 23.38-hour schedule gives 23.42 hours and about 35 minutes of
  margin. Extrapolating the full 20-step mean with measured startup gives 23.36
  hours and about 38 minutes; the last-ten mean gives 21.45 hours. In contrast,
  scaling C3's exact 68,896.488-second remaining schedule by the 1.247800
  retry-2/C3 prefix ratio gives 24.70 hours, about 42 minutes outside the hard
  limit. The latter changes sharply from the step-10 ratio of 1.18115 because
  C3 steps 11--20 were unusually fast (95.124-second mean) while retry 2's
  corresponding steps averaged a still-healthy 127.199 seconds.
- Decision: continue retry 2 unchanged to a preselected step-40 gate. Two
  independent estimators based on the live trajectory remain inside the limit,
  the run has recovered materially from retry 1, and stopping on a single
  high-variance 20-step ratio would be premature. At step 40, repeat exact
  mechanism accounting and compare the longer prefix under all four estimators.
  This decision changes no scientific or operational setting and does not
  create a partial C5 result.

### D-084 - Continue C5 after the recovered step-40 and live step-66 gates

- Date: 2026-09-01
- Observation recovery: the login node lost its Munge socket after step 22,
  closing the local observer and temporarily preventing Slurm queries. The
  allocation itself remained live: run-log and memory timestamps continued to
  advance with zero fatal signatures. Scheduler authentication later recovered
  and confirmed job `870750` still `RUNNING`. No process, configuration, or
  scientific state was restarted or changed. The exact log permits a complete
  retrospective step-40 reconstruction and an authoritative step-66 gate.
- Runtime evidence: retry-2 timed-step costs are 5,771.667 seconds through step
  40, 8,953.711 through step 60, and 9,585.063 through step 66. Its ratio to the
  exact C3 schedule falls monotonically across the disputed longer gates:
  1.210294, 1.134299, and 1.126293, compared with the noisy step-20 ratio of
  1.247800. At step 66, applying 1.126293 to C3's exact 62,613.264-second
  remainder and conservatively including current elapsed from the partly
  processed step 67 projects 22.40 total hours, about 96 minutes inside the
  limit. The frozen schedule plus the complete shared 46-step primary-prefix
  excess projects 23.42 hours, about 35 minutes inside. Uniform all-step and
  last-20 extrapolations remain outside at 24.52 and 25.69 hours because they
  spread the observed nonuniform verifier-timeout clusters across every future
  step rather than using the known seeded schedule.
- Mechanism evidence: through step 66, 61 optimizer updates account for 22,720
  optimized proofs and a valid 192-proof residual from 22,912 retained. The
  optimized categories are 1,398 blocked correct, 14,387 alternative correct,
  and 6,935 incorrect, with weighted mean advantages -0.723791, +0.528422, and
  -0.950331. Every nonempty per-update category has the registered sign, every
  summary names `reject_reward`, and all 1,398 physically blocked correct proofs
  were reward-rejected. Peak node use is 183.10 GiB with no OOM, worker-kill,
  traceback, or fatal event.
- Decision: continue retry 2 unchanged to step 80. The longer schedule-aware
  evidence has resolved D-083's early ratio spike in the favorable direction,
  while mechanism and resource gates remain exact. Preserve every frozen
  setting and repeat all estimators at step 80; no partial scientific result is
  admitted.

### D-085 - Replace retry 2 at the exact step-80 gate and drain its failed node

- Date: 2026-09-01
- Mechanism evidence: the exact 80-step prefix remains scientifically valid.
  Seventy-three optimizer updates account for all 27,104 retained and optimized
  proofs with zero residual: 1,634 blocked correct, 17,298 alternative correct,
  and 8,172 incorrect. Their weighted mean advantages are -0.751327, +0.526091,
  and -0.963369; every nonempty per-update category has the registered sign.
  All 1,634 physically blocked correct proofs were reward-rejected. Peak node
  use is 183.10 GiB, and no OOM, worker crash, traceback, or fatal signature
  exists. No metrics, finalization log, exit record, or complete checkpoint was
  produced.
- Runtime evidence: retry-2 timed-step cost through step 80 is 12,470.058
  seconds versus 9,995.476 seconds through the same seeded C3 positions, a
  cumulative ratio of 1.247570. At the gate, 12,650 allocation seconds had
  elapsed. Adding that measured prefix to the ratio-scaled exact 61,128.063-
  second C3 remainder projects 24.70 total hours, about 42 minutes beyond the
  hard 24-hour maximum. This exact long-prefix gate supersedes both D-083's
  volatile early estimates and D-084's favorable step-66 estimate.
- Decision: permanently exclude retry-2 partial state and cancel job `870750`
  on the registered runtime-only gate. The job ended at 12:49:39 after 3:31:31
  with exactly 80 visible completed steps. Never resume, pool, compare, or
  select its partial samples. Frozen analysis job `870751` was canceled at zero
  runtime.
- Failed-node evidence: dependency-bound pristine retry-3 job `871169`
  initially received the just-released `trig0033` node. Seven seconds later,
  before the batch runner executed or any run artifact was created, Slurm
  canceled the allocation and drained the node with reason
  `prolog.chk.nvidia-smi.unresponsive`. Dependent analysis job `871170` was
  canceled at zero runtime. The retry-3 directory still contained only its
  metadata and byte-identical frozen train, validation, and archive inputs.
- Recovery: after retry 2 and the failed allocation were terminal, submit the
  exact immutable retry-3 runner again as job `871184`, without a now-redundant
  dependency, pending a healthy complete four-H100 node. Bind frozen analysis
  job `871185` by `afterok:871184`. The training runner, submission, analysis
  runner, and analysis submission SHA-256 values remain respectively
  `1bb835bdf1e06f8394fd52c4665cee358976f8a4a695c33696a4b3b8ad905169`,
  `ddf0cde38c45d4b2755da58202f84150c8f90ba29b64ef48f0da7b8c715d1732`,
  `0c3338515ed38282c276baf031f0ed160e12eb7b14bd7971cc693c6040219e3f`,
  and `d06eddcbb570687e553bcf690bf3c3f976d3dddac27af4e389cb57d72d72fdc3`.
  This is an operational replacement before any C5 result and changes no
  scientific setting.

### D-086 - Exclude the repeatedly infeasible C5 physical node

- Date: 2026-09-01
- New scheduler observation: after D-085's prolog failure drained `trig0033`,
  Slurm automatically returned that node to service and allocated retry-3 job
  `871184` there at 12:51:36. This passed the later prolog but repeated the
  physical node on which two scientifically valid 80-step trajectories had
  projected 25.03 and 24.70 hours against the 24-hour maximum.
- Decision gate: stop job `871184` before any completed training step rather
  than spend a third full trajectory on the empirically infeasible node. It was
  canceled at 12:53:53 after 2:17 of sparse staging/startup, with zero visible
  step records, no metrics, and no final checkpoint. Dependent analysis job
  `871185` was canceled with zero runtime. This startup-only directory is
  permanently excluded and never reused.
- Corrected recovery: stage a separate pristine directory with the same
  byte-identical train, validation, and archive inputs; execution snapshot;
  base actor/reference; seed; optimizer; proposal budget; 32-worker verifier;
  300-second timeout; `reject_reward`; resume disabled; and complete four-H100
  hardware class. Change only the scheduler constraint
  `ExcNodeList=trig0033`. Training job `871191` is pending on resources with
  that exclusion and zero runtime; frozen analysis job `871192` is
  `afterok:871191`.
- Frozen artifacts: training runner and submission SHA-256 values are
  `b9d3e7b44673f242afe9226d8879edbed536785b2c02ce33691fbd0f7e2a3c94`
  and `c250cc4c0de396ff99c524099e11f52945661399e3ada9e1950aba23fc534fa5`;
  analysis runner and submission values are
  `4747f5cf4f9d34d737fb69ab907a8976f872f2f4f456f9f254c161675dbf7dc4`
  and `32d627a255ac1e840bbfb6d86a7cc3847252b547d691ad34987fea9216d8bcb6`.
  Outside-allocation preflights failed closed with status 2 and created no run
  or result artifact.
- Superseded requests: jobs `871187`/`871188` and `871189`/`871190` were
  canceled with zero runtime after their predecessor dependency had already
  become terminal and Slurm therefore removed the satisfied edge. They created
  no artifact and are never eligible. The only C5 training trajectory now
  eligible to start is node-excluding job `871191`.
- Interpretation: excluding a demonstrably infeasible physical node is an
  operational completion safeguard, not a scientific intervention. The GPU
  class, driver requirement, resource shape, verifier, timeout, sampling,
  optimizer, and model condition remain unchanged; no partial scientific
  outcome is selected or pooled.

### D-087 - Admit the finalized C1 pass@128 source and correct its release gate

- Date: 2026-09-01
- Finalized source: C1 retry-9 job `868001` completed all 117 batches and
  finalized at 13:14 EDT with the registered upstream post-completion sentinel.
  Metrics SHA-256 is
  `fcdd5a6dcb76c8ab7735bc8b4c445acf349e7a9805c67a0eb9fc369ee35c26b9`.
  It records 59,776 registered proposals, 59,904 physical proposals, 128
  excluded padding proposals, and 29,172 registered correct proofs. MiniF2F has
  11,101 correct proofs, 2,979 correct modes, and 121/244 theorems solved at
  128; registered validation has 18,071 correct proofs, 5,489 modes, and
  154/223 solved at 128. This is one eligible source, not a C0/C1/C3 result.
- Release-gate observation: the first release watcher correctly refused to
  cancel the retained workbench because it asserted that failure classes cover
  every physical proof-log row. Finalized metrics show the intended accounting:
  failure classes sum to the 59,776 registered proposals, while the proof log
  contains all 59,904 physical rows and `excluded_padding_proposals` exactly
  reconciles the 128-row difference. Treating padding as a registered failure
  class would contradict its explicit exclusion.
- Correction: change only the watcher assertion to require failure-class
  coverage of `registered_proposals`; retain independent checks that the proof
  log has `physical_proposals` rows, the physical/registered difference equals
  excluded padding, all hashes match, the sentinel is present, and metadata
  records completion. Corrected watcher SHA-256 is
  `98398715b991f8c29b7b3aad082c0f3500e80ca1570e0d758b894d6b5de07f1d`.
- Evidence and decision: the restarted watcher passed every guard, normalized
  no scientific artifact, and released finalized job `868001`. Keep the C1
  source immutable and wait for eligible C0 and C3 finalization before the
  frozen joint analysis publishes any comparative result.

### D-088 - Admit the node-excluding C5 allocation through five batches

- Date: 2026-09-01
- Allocation evidence: job `871191` started at 13:15:02 on `trig0031` with
  authoritative `ExcNodeList=trig0033`. Slurm supplied the exact complete-node
  request: four H100 80GB GPUs, 96 CPUs, 770,000 MiB, and 24 hours. Sparse
  verifier staging used 4,555,536 KiB and left 546 GiB free; the run-local
  runner, inputs, intervention, execution snapshot, and hardware record match
  the frozen registration. Analysis job `871192` remains `afterok:871191` with
  zero runtime.
- Mechanism evidence: five optimizer updates account for all 1,856 retained
  and optimized proofs with zero residual: 113 blocked correct, 1,064
  alternative correct, and 679 incorrect. Weighted mean advantages are
  -0.649184, +0.614962, and -0.855614; every nonempty category in every update
  has the registered sign and every blocked proof was reward-rejected. No OOM,
  worker crash, traceback, or fatal signature exists.
- Runtime evidence: the first five timed steps cost 840.692 seconds, versus
  893.026 in excluded retry 1, 608.530 in excluded retry 2, and 515.047 in the
  completed C3 schedule. One 355.882-second verifier tail at step 4 accounts
  for most of the excess. The first three steps otherwise cost 358.866 seconds,
  close to retry 2's 335.140-second prefix.
- Decision: continue job `871191` unchanged to an exact step-20 gate. Prior C5
  attempts established that a five-step prefix containing one timeout cluster
  is not predictive of the longer schedule ratio; stopping now guarantees no
  eligible result. Preserve every scientific and operational setting and
  evaluate exact mechanism accounting, tail distribution, and runtime
  feasibility after 20 completed steps. No partial scientific result is
  admitted.

### D-089 - Allocate the unchanged matched control through its authorized account

- Date: 2026-09-01
- Motivation: the matched control is the discriminating test of whether C3's
  observed diversity gain is caused by hard exclusion rather than its earlier
  optimizer history. Pending job `869225` was delayed solely by its scheduler
  association: the user's effective fair share was about 0.056 under
  `def-zhijing` versus 0.205 under the already authorized `rrg-zhijing`
  account.
- Decision: change only job `869225`'s billing account in place to
  `rrg-zhijing`. Preserve the job ID, immutable runner, pristine run directory,
  base actor/reference, seed, train/validation/archive inputs, disabled
  blocking, optimizer, data order, 32 proposals, 32 Lean workers, complete
  four-H100 shape, resume refusal, and 24-hour limit. Submit no duplicate.
- Evidence: scheduler priority rose from about 279,691 to 1,026,466 and Slurm
  allocated the same job on `trig0044` at 13:32:43 EDT. The submission and
  immutable runner SHA-256 values remain
  `0868ca140ca11adff7da3e19ed5cdde3b578268e5eb10f7fe5c016183cb4073a`
  and `2120c329c85ffa12bc0b43a50dfc9bc8069771b90c2e3631e0221e256dd06430`.
  The account change is scheduling-only and cannot alter the scientific
  comparison. No matched-control claim exists until all 604 steps finalize and
  the frozen training and held-out analyses validate.

### D-090 - Continue C5 after the node-excluding step-20 gate

- Date: 2026-09-01
- Mechanism evidence: 20 optimizer updates account for all 7,840 retained and
  optimized proofs with zero residual: 443 blocked correct, 4,826 alternative
  correct, and 2,571 incorrect. Weighted mean advantages are -0.618396,
  +0.558346, and -0.941512; every nonempty category in every update has the
  registered sign and every summary names `reject_reward`. Step telemetry
  records exactly 443 physical blocked-correct proofs and 443 reward
  rejections, with no all-blocked-prompt residual.
- Runtime evidence: current timed-step cost through step 20 is 2,664.161
  seconds, compared with 2,227.051 for C3, 2,629.102 for the excluded primary,
  3,208.902 for excluded retry 1, and 2,778.915 for excluded retry 2. Thus the
  new node is only 35.059 seconds behind the primary and is already faster than
  both long-node retries at the same positions. Its last ten steps average
  120.786 seconds; the single step-4 timeout remains the 355.882-second
  maximum.
- Projection: adding the measured primary-prefix excess to the frozen
  23.38-hour schedule gives 23.39 hours and about 37 minutes of margin. A
  deliberately conservative alternative uses the current/C3 prefix ratio of
  1.196273, C3's exact 68,896.488-second remaining schedule, and the later
  48:22 allocation observation rather than the earlier step-completion time;
  it projects 23.70 hours and about 18 minutes of margin. Uniform all-step and
  last-ten projections are shorter. Peak use is 181,426,284 KiB (173.02 GiB),
  with no OOM, worker kill, traceback, or fatal event.
- Decision: continue eligible job `871191` unchanged to an exact step-40 gate.
  Both schedule-matched and tail-sensitive estimates retain positive margin,
  the mechanism is exact, and the early verifier tail did not recur through
  step 20. Preserve every frozen scientific and operational setting. This is
  not a C5 performance result; admission still requires all 604 steps,
  finalization, validation, and the frozen D-054 analysis.
