# Model and Compute Guidance

## Use this model

```text
deepseek-ai/DeepSeek-Prover-V1.5-SFT
```

This is the paper's base model and the upstream launcher's configured model.
Use the exact same Hugging Face revision for all conditions and record the
resolved commit hash.

Roles:

| Role | Model |
|---|---|
| actor initialization | `deepseek-ai/DeepSeek-Prover-V1.5-SFT` |
| frozen reference policy | the same checkpoint and revision |
| correctness reward | no model; Lean verifier |
| mode detector | no model; deterministic proof signature |
| evaluation generator | the relevant C0-C3 checkpoint |

## Why not another model first

Changing to Qwen, a smaller prover, or a newer DeepSeek-Prover version would
confound the comparison and make the experiment harder to interpret. A smaller model
may also lack enough correct alternatives for blocking to reveal anything.

Alternative models are a later generalization study, not a first experiment.

## Hardware target

The paper reports:

- 4 NVIDIA L40S GPUs;
- 500 GB RAM;
- 48-64 CPU workers for parallel Lean verification;
- all main runs completed within 36 hours;
- the checked-in Slurm request reserves 48 hours.

Good substitutes:

1. 4x H100 80 GB;
2. 4x A100 80 GB;
3. 4x L40S as used by the authors.

CPU and RAM matter because Lean verification runs in parallel. A GPU-rich node
with too few CPU cores can be slower than the paper's setup.

## Expected job classes

### Preflight and unit tests

- CPU only
- minutes

### Base inference smoke test

- 1 GPU
- 12 or more CPU workers
- small data slice

### Full training

- 4 GPUs
- 64 CPU workers
- high-memory node
- up to 48 hours per condition

### Evaluation at pass@512

- array jobs are preferred
- 1 GPU per shard
- enough CPU workers for Lean verification

## Storage

Reserve space for:

- Hugging Face model cache;
- actor and optimizer checkpoints;
- generated proofs at 32 samples per training theorem;
- 512-sample evaluation archives;
- Lean and mathlib build artifacts;
- W&B or local logs.

Use a shared model cache but separate immutable run directories.

## Software dependencies

The upstream project expects:

- CUDA-capable PyTorch;
- veRL dependencies pinned by the repository;
- vLLM;
- Ray;
- DeepSeek-Prover-V1.5 verifier code;
- Lean 4;
- leanprover-community/repl;
- a working mathlib/Lean workspace.

Do not upgrade packages during an experiment unless required to make the
upstream code run. Record every compatibility patch.

## Model recommendation in one line

Use only `deepseek-ai/DeepSeek-Prover-V1.5-SFT` for the controlled study.
Generalize later, after the mechanism works.

## Follow-on track model matrix

These are not substitutes for the primary model. They apply only if the
corresponding source-paper implementation is opened after Phase 1:

| Track | Actor/prover | Reference or judge |
|---|---|---|
| Restriction-RL | `deepseek-ai/DeepSeek-Prover-V1.5-SFT` | same frozen revision; Lean verifies |
| Rewarding the Rare, smallest paper-matched route | Qwen2.5-7B-Instruct | Qwen2.5-72B strategy judge |
| STP Lean | `deepseek-ai/DeepSeek-Prover-V1.5-SFT` | Lean verifier |
| STP Isabelle reproduction | Llemma-7B | Isabelle verifier |

Do not put the Rewarding the Rare judge into the primary Lean experiment. The
point of Phase 1 is that both correctness and mode enforcement are deterministic
and auditable.
