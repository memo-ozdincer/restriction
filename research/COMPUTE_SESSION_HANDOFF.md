# Compute Session Handoff

Last updated: 2026-07-17 (allocation `17895062` shutdown)

## Outcome

The environment and the unchanged base-model inference path are working. The
registered C0 rollout did **not** complete and has no reportable C0 metric.
It was intentionally cancelled during initialization at the user's request.
No proof-mode archive was built from it, and no model update was performed.

## Allocation and cancellation record

- Slurm allocation: `17895062` (`interactive-4xh100`)
- Node: `g21`
- Requested resources: 4 H100 GPUs, 56 CPUs, 1000 GB memory
- C0 directory: `runs/c0-base-20260717-grpo-default/`
- State at shutdown: one transient sample-only batch completed (visible only in
  `run.log`); no proof JSONL, checkpoint, or completed rollout artifact
  existed.
- Required continuation: allocate fresh resources and begin a *new* C0 run
  directory. Do not turn this incomplete directory into a result.

## What is verified

- `scripts/project/preflight.sh` passed in `.venv-legacy`.
- The DeepSeek REPL and its pinned Mathlib workspace built locally.
- Direct Lean verification accepted `(1 : Nat) = 1 := by rfl` using the
  upstream verifier runtime.
- The pristine
  `deepseek-ai/DeepSeek-Prover-V1.5-SFT` inference gate completed at
  `runs/base-inference-smoke-20260717-vllm042-torch230/`: generation, proof
  parsing, and Lean verification ran end-to-end. The smoke's zero correct
  proposals are not a C0 result.

## Reproduction inputs for the fresh C0

- Model revision:
  `e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`
- Source data: `data/mff-lwb-10k-seen.parquet`
  - SHA-256: `56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb`
- Registered derivatives (preserved in the interrupted directory):
  - `train.parquet`: 9,655 rows, SHA-256
    `502d3216ced1829a996869fe31400cece726ac83e0fb469bda0cd9d79961382a`
  - `valid.parquet`: 223 rows, SHA-256
    `05f6176ec4ca85bff8368c64a09049c0e0dad84b1dd3741ace1f8e7de1b35b15`
- Seed: 42
- Proposal budget: 32 samples/problem; do not alter it for C3.
- C0 launch configuration: `runs/c0-base-20260717-grpo-default/run.sh` and
  `runs/c0-base-20260717-grpo-default/hydra/.hydra/config.yaml`.

## Environment actually used

- Python 3.11.4; Torch 2.3.0+cu121; Ray 2.38.0; Transformers 4.40.1;
  TensorDict 0.3.1; vLLM 0.4.2; xFormers 0.0.26.post1; FlashAttention 2.5.8.
- Lean 4.9.0-rc1; Lake 5.0.0-be6c489.
- Upstream runtime requirement: set `HOME=/scratch/memoozd`, use the DeepSeek
  repository as the working directory, and preserve its `PYTHONPATH` so the
  verifier finds `$HOME/.elan/bin/lake` and its pinned workspace.
- The reasons for each compatibility correction are recorded in D-010 through
  D-019 of `research/DECISIONS.md`; the complete environment freeze is
  `research/legacy-env-freeze.txt`.

## Chat-history recovery on a login node

The compute node's `$HOME` is the shared NFS `/home` filesystem. A copy of the
Codex history needed for this handoff was made at:

`/home/memoozd/codex-handoffs/20260717-17895062/`

It deliberately excludes Codex credentials. The directory contains the CLI
history, July session files, the local Codex log database, and a checksum
manifest. It is directly visible after logging in because `/home` is shared;
no compute-node SSH hop is required.

The copied manifest SHA-256 is
`052ccd89bb8428e62ce77dd8ba01135defaa0558a1163e645e3372d3c1db7d79`.

## Next work in required order

1. Start fresh allocation and fresh C0 directory from the pristine base model.
2. Complete C0 and one short unchanged C1 smoke, recording all required
   counts and metadata.
3. Run the existing proof-mode unit tests, freeze the C0 archive, and only
   then enable the disabled-by-default hard-exclusion treatment for C3.

Do not use the failed/partial C0 directory for metrics, checkpoints, archive
construction, or restart.
