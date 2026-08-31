#!/usr/bin/env bash
# Run a prepared C0 rollout. This is sample-only and has no policy update.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_DIR_INPUT="${1:?usage: launch_c0.sh /absolute/path/to/fresh-c0-run}"
RUN_DIR="$(cd "${RUN_DIR_INPUT}" && pwd)"
if [[ ! -f "${RUN_DIR}/RUN_METADATA.md" || -e "${RUN_DIR}/artifacts/actor" ]]; then
  echo "refusing unprepared or reused C0 run directory: ${RUN_DIR}" >&2
  exit 2
fi

export VENV="${VENV:-${RESTRICTION_VENV:-${ROOT}/.venv-legacy}}"
source "${ROOT}/scripts/project/activate_scratch_env.sh"
export HOME="${RESTRICTION_RUNTIME_HOME:-/scratch/memoozd}"
export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"
BASE_MODEL_PATH="${RESTRICTION_BASE_MODEL_PATH:-/scratch/memoozd/models/DeepSeek-Prover-V1.5-SFT}"
# The upstream wrapper otherwise imposes a 10-GB RLIMIT_AS on every Lean
# worker.  On the 1-TB C0 allocation this can turn a verifier result handoff
# into a worker MemoryError and deadlock the batch.  This only changes the
# process resource ceiling; Lean verification semantics remain unchanged.
export DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB="${DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB:-32}"
export DMB_GIT_COMMIT="${DMB_GIT_COMMIT:-$(git -C "${ROOT}" rev-parse HEAD)}"
export DMB_MODEL_REVISION="${DMB_MODEL_REVISION:-e9a6e6fbb67620d4e9c4944bc51ff7c435af12da}"
cd "${DEEPSEEK_PROVER_ROOT}"

exec python -m verl.trainer.main_lean \
  data.train_files="${RUN_DIR}/train.parquet" \
  data.val_files="${RUN_DIR}/valid.parquet" \
  data.max_prompt_length=512 \
  +data.seed=42 \
  actor_rollout_ref.model.path="${BASE_MODEL_PATH}" \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=8 \
  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=16 \
  actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=16 \
  critic.ppo_micro_batch_size=8 \
  trainer.default_hdfs_dir=null \
  trainer.default_local_dir="${RUN_DIR}/artifacts" \
  trainer.n_gpus_per_node=4 \
  trainer.nnodes=1 \
  trainer.logger='[console]' \
  actor_rollout_ref.rollout.name=vllm \
  actor_rollout_ref.rollout.n=1 \
  actor_rollout_ref.rollout.response_length=512 \
  actor_rollout_ref.actor.use_kl_loss=True \
  actor_rollout_ref.actor.kl_loss_coef=0.02 \
  actor_rollout_ref.actor.ppo_epochs=1 \
  algorithm.adv_estimator=grpo \
  +actor_rollout_ref.model.trust_remote_code=True \
  actor_rollout_ref.rollout.load_format=dummy_dtensor \
  actor_rollout_ref.actor.update_rule=ppo \
  trainer.experiment_name="$(basename "${RUN_DIR}")" \
  trainer.save_freq=0 \
  trainer.save_proof_freq="${SAVE_PROOF_FREQ:-25}" \
  trainer.total_epochs=1 \
  +trainer.sample_only=True \
  +trainer.resume=False \
  lean.prompt_key=deepseek-prover \
  lean.num_samples=32 \
  lean.problem_batch_size=16 \
  lean.rejection_sampling=False \
  lean.advantage_threshold=False \
  lean.max_workers=64 \
  lean.hard_blocking.enabled=False \
  hydra.run.dir="${RUN_DIR}/hydra"
