# Rewarding the Unlikely - Paper Notes

Paper: `papers/2506.02355v2.pdf`

SHA-256:

```text
5daad4497bf1a2af73ee663688ec7873b5d26aa883c5c246acfc0f0fa1e56292
```

## Core observation

GRPO preferentially reinforces already likely correct proof sequences. The
paper calls this rank bias. Pass@1 can improve while pass@N at larger N
stagnates or deteriorates relative to the base model.

## Paper intervention

Within each problem's correct rollout group, rank samples by current-policy
likelihood. Apply a multiplicative rank penalty to correct rollout rewards so
rarer correct proofs receive relatively more advantage.

Incorrect rollouts are not changed by the rank penalty. Samples that had zero
advantage before perturbation remain skipped.

## Paper configuration

Base model:

```text
deepseek-ai/DeepSeek-Prover-V1.5-SFT
```

Shared settings reported in the paper:

- learning rate: `1e-6` after reducing the unstable reported `5e-6`;
- 32 proof attempts per theorem;
- 512 generated response tokens;
- one training epoch;
- Lean verification as binary correctness reward.

Table 1:

| Condition | PPO epochs | KL coefficient | rank penalty |
|---|---:|---:|---:|
| GRPO-Default | 1 | 0.02 | none |
| GRPO-Unlikeliness-1 | 1 | 0.10 | 0.25 |
| GRPO-Unlikeliness-2 | 2 | 0.10 | 0.25 |
| GRPO-Epochs-2 | 2 | 0.10 | none |
| GRPO-Epochs-3 | 3 | 0.10 | none |

The main 10K analysis reports 9,600 training problems sampled during the
one-epoch run. The final larger recipe uses an approximately 11K theorem
dataset and evaluates on miniF2F-test plus the paper's validation set.

## Compute

The authors report 4 NVIDIA L40S GPUs, 500 GB RAM, and 48-64 CPUs. Main
training runs finish within 36 hours. Generation plus verification for a batch
of 16 problems x 32 attempts takes about 120 seconds. Policy-update time is
approximately 70 seconds per PPO epoch.

## Released code observations

The current `examples/lean/grpo.sh` defaults to:

- model: the correct DeepSeek-Prover base;
- data: `mff-lwb-goedel-28k.parquet`;
- KL: `0.10`;
- PPO epochs: `2`;
- rank penalty: `0.25`;
- 32 samples per problem;
- response length: 512;
- one training epoch.

It is therefore configured like GRPO-Unlikeliness-2, not GRPO-Default.

The dataset default does not transparently match the paper's stated 10K or 11K
experiment. This must be resolved before treating a run as a reproduction.

## Relevant code seams

- `examples/lean/grpo.sh`
- `verl/trainer/ppo/ray_lean_trainer.py::_generate_and_verify_full_proofs`
- `verl/trainer/ppo/ray_lean_trainer.py::_compute_advantages`
- `verl/lean/utils.py::parse_proof_steps`
- `examples/inference/proof_sampler.py`
- `misc/paper_figures.ipynb`

## Limitations inherited from the paper

- Unique proof strings can overstate strategy diversity.
- The paper's rank proxy is relative sequence likelihood, not a semantic proof
  taxonomy.
- The data come from autoformalized Lean statements and may contain artifacts.
- A result on Lean proof scripts does not establish natural-language strategy
  diversity.

## Our single intended change

Replace the continuous rank penalty with persistent, deterministic hard
exclusion of the dominant correct mode, and reset training to the pristine base
model before applying it.

