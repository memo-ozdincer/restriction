# Decision Log

Record decisions before running the affected experiment.

## D-001 - Repository base

- Date: 2026-07-18
- Decision: fork official repository commit
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
- Decision: test the mechanism in the Rewarding the Unlikely Lean/GRPO fork,
  then open a Rewarding the Rare fork, and defer STP until the small controlled
  experiment is interpretable.
- Reason: the first fork supplies deterministic verification, a narrow code
  seam, and the same DeepSeek-Prover base used by STP without requiring STP's
  conjecturer and large iterative data pipeline.

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
- Compatibility note: this fork's historical pins (`transformers<4.48`,
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
- Decision: use the separately provisioned `.venv-legacy` for this old veRL
  fork and leave PRIME-RL's environment untouched.
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
- Decision: replace legacy-environment `vllm==0.4.1` with the fork-supported
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
  fork split, not exact numerical reproductions of the paper's unpublished
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
