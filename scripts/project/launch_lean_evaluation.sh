#!/usr/bin/env bash
# Generate and Lean-verify a registered evaluation at the requested proposal budget.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_DIR_INPUT="${1:?usage: launch_lean_evaluation.sh RUN_DIR MODEL_PATH [NUM_SAMPLES]}"
MODEL_PATH="${2:?usage: launch_lean_evaluation.sh RUN_DIR MODEL_PATH [NUM_SAMPLES]}"
NUM_SAMPLES="${3:-32}"
case "${NUM_SAMPLES}" in
  32) PROBLEM_BATCH_SIZE=16 ;;
  128) PROBLEM_BATCH_SIZE=4 ;;
  *) echo "supported evaluation proposal budgets are 32 and 128" >&2; exit 2 ;;
esac
RUN_DIR="$(cd "${RUN_DIR_INPUT}" && pwd)"
if [[ ! -f "${RUN_DIR}/RUN_METADATA.md" || -e "${RUN_DIR}/artifacts/proofs" ]]; then
  echo "refusing unprepared or reused evaluation directory: ${RUN_DIR}" >&2; exit 2
fi
if [[ ! -d "${MODEL_PATH}" || -z "${DEEPSEEK_PROVER_ROOT:-}" || ! -d "${DEEPSEEK_PROVER_ROOT}" ]]; then
  echo "model and pinned verifier paths must exist" >&2; exit 2
fi
export VENV="${ROOT}/.venv-legacy"
source "${ROOT}/scripts/project/activate_scratch_env.sh"
export HOME=/scratch/memoozd PYTHONPATH="${ROOT}:${PYTHONPATH:-}"
export DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB="${DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB:-32}"
export DMB_GIT_COMMIT="${DMB_GIT_COMMIT:-unknown}" DMB_MODEL_REVISION=e9a6e6fbb67620d4e9c4944bc51ff7c435af12da
export VLLM_ATTENTION_BACKEND=XFORMERS
cd "${DEEPSEEK_PROVER_ROOT}"
exec python -m verl.trainer.main_lean \
  data.train_files="${RUN_DIR}/train.parquet" data.val_files="${RUN_DIR}/valid.parquet" \
  data.max_prompt_length=512 +data.seed=42 actor_rollout_ref.model.path="${MODEL_PATH}" \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=8 \
  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=16 \
  actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=16 critic.ppo_micro_batch_size=8 \
  trainer.default_hdfs_dir=null trainer.default_local_dir="${RUN_DIR}/artifacts" \
  trainer.n_gpus_per_node=4 trainer.nnodes=1 trainer.logger='[console]' \
  actor_rollout_ref.rollout.name=vllm actor_rollout_ref.rollout.n=1 \
  actor_rollout_ref.rollout.response_length=512 actor_rollout_ref.rollout.temperature=1.0 \
  actor_rollout_ref.rollout.top_p=1.0 actor_rollout_ref.rollout.top_k=-1 \
  +actor_rollout_ref.model.trust_remote_code=True actor_rollout_ref.rollout.load_format=dummy_dtensor \
  trainer.experiment_name="$(basename "${RUN_DIR}")" trainer.save_freq=0 \
  trainer.save_proof_freq=1000000 trainer.total_epochs=1 +trainer.sample_only=True +trainer.resume=False \
  algorithm.adv_estimator=grpo \
  lean.prompt_key=deepseek-prover lean.num_samples="${NUM_SAMPLES}" lean.problem_batch_size="${PROBLEM_BATCH_SIZE}" \
  lean.rejection_sampling=False lean.advantage_threshold=False lean.max_workers=64 \
  lean.hard_blocking.enabled=False hydra.run.dir="${RUN_DIR}/hydra"
