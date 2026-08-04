# Compute Session Handoff

Last updated: 2026-08-04 (C0 completed on allocation `19059868`)

## Outcome

The environment, unchanged base-model inference path, and registered C0 rollout
are complete. C0 contains all 9,655 registered train theorems at 32 proposals
each (308,960 scientific proposals). A 32-proposal dataloader padding group is
reported separately and excluded. No model update was performed.

Authoritative aggregate:
`runs/c0-base-20260804-seed42-complete/`

- Validation: `validation.json` (`status: valid`)
- Metrics: `metrics.json`
- Frozen dominance archive: `mode_archive.json`
- Archive SHA-256:
  `fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3`
- Correct proposals: 168,029
- Solved theorems: 7,785; pass@32: 0.806318
- Independent non-scratch backup:
  `/home/memoozd/c0-archives/c0-base-20260804-seed42-complete.tar.zst`
  (15 MiB compressed; SHA-256
  `300ba7b441433aa0676a2e2df5851a7aa51beca2afcaa93d7ab17c59f6edda70`)

## Completed allocation record

- Slurm allocation: `19059868`
- Node: `g28`
- Final run step: `19059868.5` (00:47:12)
- Resources: 4 H100 80GB HBM3 GPUs, 56 CPU cores, 256 GB RAM
- Final continuation:
  `runs/c0-base-20260804-seed42-telemetry-final535/`
- Final proof snapshot: `artifacts/proofs/global_step_34.jsonl`
  (`cb35eefdd88825ba951ca220339eb8283b2eb0ee7c7e46908382c40818162a43`)
- The upstream expected `Exception("Stop")` sentinel followed
  `[TRAINING] Training finished`; all final artifacts were already saved.

## Historical interrupted allocation

- Slurm allocation: `17895062` (`interactive-4xh100`)
- Node: `g21`
- Requested resources: 4 H100 GPUs, 56 CPUs, 1000 GB memory
- C0 directory: `runs/c0-base-20260717-grpo-default/`
- State at shutdown: one transient sample-only batch completed (visible only in
  `run.log`); no proof JSONL, checkpoint, or completed rollout artifact
  existed.
- Historical disposition: excluded permanently. It was never turned into a
  result; the later four-snapshot aggregate supersedes its continuation need.

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

## Authoritative C0 inputs

- Model revision:
  `e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`
- Source data: `data/mff-lwb-10k-seen.parquet`
  - SHA-256: `56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb`
- Registered derivatives:
  - `train.parquet`: 9,655 rows, SHA-256
    `502d3216ced1829a996869fe31400cece726ac83e0fb469bda0cd9d79961382a`
  - `valid.parquet`: 223 rows, SHA-256
    `05f6176ec4ca85bff8368c64a09049c0e0dad84b1dd3741ace1f8e7de1b35b15`
- Seed: 42
- Proposal budget: 32 samples/problem; do not alter it for C3.
- Final continuation's exact resolved configuration:
  `runs/c0-base-20260804-seed42-telemetry-final535/hydra/.hydra/config.yaml`
  (`00c41e95b94325965fca4abe7e08a0ef207fb284d5cfd095f1856b51542e1851`).

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

1. Run one short unchanged C1 smoke, recording all required counts and
   metadata.
2. Build the persistent dominance blocklist from the frozen C0 archive.
3. Keep hard exclusion disabled by default and start C3 from the exact pristine
   base model, never from a discovery checkpoint.

Do not use the failed/partial historical C0 directory for metrics, checkpoints,
archive construction, or restart. Use only the four source snapshots recorded
in the complete aggregate manifest.
