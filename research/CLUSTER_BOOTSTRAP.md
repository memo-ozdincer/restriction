# Cluster Bootstrap Record

Last updated: 2026-07-17

This records the actual scratch bootstrap attempt. It is not a training result.

## Reused paths

- Restriction checkout: `/scratch/memoozd/rl/restriction`
- Reused PRIME venv: `/scratch/memoozd/rl/prime-rl/.venv`
- DeepSeek verifier checkout: `/scratch/memoozd/rl/DeepSeek-Prover-V1.5`
- Model cache: `/scratch/memoozd/models/DeepSeek-Prover-V1.5-SFT`
- uv cache: `/scratch/memoozd/.cache/uv`
- Elan home: `/scratch/memoozd/.elan`
- Recovery reference: `../Nowak-coordination/docs/CLUSTER_RL_RUNBOOK.md`

## Legacy environment snapshot

- Python: `3.11.4`
- Ray: `2.38.0`
- Torch: `2.3.0+cu121`
- Transformers: `4.40.1`
- vLLM: `0.4.2`
- TensorDict: `0.3.1`
- Accelerate: `0.33.0`
- Lean: `4.9.0-rc1`
- Lake: `5.0.0-be6c489`
- GPUs observed: 4 × NVIDIA H100 80 GB, driver `580.82.07`

## Commands executed

```bash
UV_BIN=/home/memoozd/.local/bin/uv scripts/project/setup_scratch_env.sh
source scripts/project/activate_scratch_env.sh
bash scripts/project/preflight.sh
```

The DeepSeek repository and `mathlib4` submodule were initialized. Lean was
installed with the scratch-local Elan home:

```bash
ELAN_HOME=/scratch/memoozd/.elan \
  /scratch/memoozd/.elan/bin/elan toolchain install \
  leanprover/lean4:v4.9.0-rc1
ELAN_HOME=/scratch/memoozd/.elan \
  /scratch/memoozd/.elan/bin/elan default leanprover/lean4:v4.9.0-rc1
```

The missing REPL dependency was fetched and built successfully:

```bash
cd /scratch/memoozd/rl/DeepSeek-Prover-V1.5/mathlib4
lake update REPL
lake build REPL
```

Resolved revisions:

- DeepSeek-Prover: `2c4ba9119eef74d0d611f494261b2c5bae98c69a`
- mathlib4: `2f65ba7f1a9144b20c8e7358513548e317d26de1`
- REPL: `c6199a81de2a7e16cb27d6f85f56cff7043cd27f`

## Results

- Four H100 80 GB GPUs detected.
- Lean `4.9.0-rc1` and Lake `5.0.0-be6c489` pass version checks.
- Model files are present locally.
- Ray in the reused PRIME venv now imports successfully (`2.52.1`, `ray.init`
  present), and the restriction preflight passes including Lean/Lake.
- The older veRL fork still cannot import against PRIME Torch `2.11.0`: the
  installed `tensordict` expects `torch.multiprocessing.reductions.ForkingPickler`,
  which this Torch version no longer provides.
- Full pytest collection and `verl.trainer.main_lean` are therefore blocked by
  this Torch/tensordict API mismatch, not by missing Ray or Lean.
- C0 base inference, verifier acceptance, and C1 GRPO smoke have **not** run
  successfully and are not reported as completed.
- The new `.venv-legacy` now imports `verl.trainer.main_lean` successfully
  after adding the small DeepSeek verifier dependencies (`pytz`, `easydict`,
  `tabulate`, `termcolor`, and the pinned `accelerate`).
- The REPL dependency is now present and `lake build REPL` succeeds.
- `scripts/project/preflight.sh` passes with the legacy environment and
  scratch Lean paths.
- After aligning the supported Torch/vLLM/FlashAttention binary pair, the
  one-row base-model smoke completed generation, proof parsing, and Lean
  verification. Evidence and the resolved Hydra configuration are under
  `runs/base-inference-smoke-20260717-vllm042-torch230/`. Its zero correct
  proposals are a smoke observation only, not a C0 result.

## Next unblock

The verifier acceptance smoke and one-row base-inference gate have completed.
The first registered C0 attempt was cancelled at the user's request during
model initialization, before a rollout artifact existed; it is not a C0 result.
Restart C0 in a fresh run directory, then run C1, saving commands and outputs
under `runs/`.

See `research/COMPUTE_SESSION_HANDOFF.md` for the exact cancelled allocation,
run paths, data checksums, environment corrections, and login-node chat
archive location.
