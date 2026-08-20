#!/usr/bin/env bash
#SBATCH --account=def-zhijing_gpu
#SBATCH --partition=gpubase_bygpu_b3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=56
#SBATCH --gpus-per-node=h100:4
#SBATCH --mem=1000G
#SBATCH --time=23:00:00
#SBATCH --job-name=lean-registered-eval

set -u
ROOT=/scratch/memoozd/rl/restriction
RUN_DIR="$(cd "${1:?usage: sbatch submit_lean_evaluation.sbatch RUN_DIR MODEL_PATH EXPECTED_COMMIT [NUM_SAMPLES] [HOLD_AFTER]}" && pwd)"
MODEL_PATH="${2:?usage: sbatch submit_lean_evaluation.sbatch RUN_DIR MODEL_PATH EXPECTED_COMMIT [NUM_SAMPLES] [HOLD_AFTER]}"
EXPECTED_COMMIT="${3:?usage: sbatch submit_lean_evaluation.sbatch RUN_DIR MODEL_PATH EXPECTED_COMMIT [NUM_SAMPLES] [HOLD_AFTER]}"
NUM_SAMPLES="${4:-32}"
HOLD_AFTER="${5:-true}"
exec > >(tee -a "${RUN_DIR}/allocation.log") 2>&1
finish_allocation() {
  local rc="${1}"
  if [[ "${HOLD_AFTER}" == "true" ]]; then
    echo "Allocation ${SLURM_JOB_ID} remains available on $(hostname) via sleep infinity."
    sleep infinity
  fi
  exit "${rc}"
}
if [[ "${HOLD_AFTER}" != "true" && "${HOLD_AFTER}" != "false" ]]; then
  echo "HOLD_AFTER must be true or false" >&2
  exit 2
fi
if ! git -C "${ROOT}" cat-file -e "${EXPECTED_COMMIT}^{commit}"; then echo "prepared commit unavailable" >&2; finish_allocation 2; fi
EXEC_ROOT="/tmp/memoozd/restriction-eval-${SLURM_JOB_ID}"
if [[ -e "${EXEC_ROOT}" ]]; then echo "execution snapshot exists" >&2; finish_allocation 2; fi
mkdir -p "${EXEC_ROOT}"; git -C "${ROOT}" archive "${EXPECTED_COMMIT}" | tar -x -C "${EXEC_ROOT}"
ln -s "${ROOT}/.venv-legacy" "${EXEC_ROOT}/.venv-legacy"
{
  date --iso-8601=seconds; echo "slurm_job_id=${SLURM_JOB_ID}"; hostname
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
} > "${RUN_DIR}/hardware.txt"
VERIFIER_ROOT="/tmp/memoozd/DeepSeek-Prover-V1.5-eval-${SLURM_JOB_ID}"
if ! "${EXEC_ROOT}/scripts/project/stage_deepseek_verifier.sh" /scratch/memoozd/rl/DeepSeek-Prover-V1.5 "${VERIFIER_ROOT}" > "${RUN_DIR}/verifier_staging.log" 2>&1; then
  printf '%s\n' 2 > "${RUN_DIR}/exit_code.txt"; finish_allocation 2
fi
set -o pipefail; export DEEPSEEK_PROVER_ROOT="${VERIFIER_ROOT}" DMB_GIT_COMMIT="${EXPECTED_COMMIT}"
"${EXEC_ROOT}/scripts/project/launch_lean_evaluation.sh" "${RUN_DIR}" "${MODEL_PATH}" "${NUM_SAMPLES}" 2>&1 | tee "${RUN_DIR}/run.log"
run_rc=${PIPESTATUS[0]}; printf '%s\n' "${run_rc}" > "${RUN_DIR}/exit_code.txt"
echo "evaluation_process_exit=${run_rc}"; finish_allocation "${run_rc}"
