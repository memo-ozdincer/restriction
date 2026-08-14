#!/usr/bin/env bash
#SBATCH --account=def-zhijing_gpu
#SBATCH --partition=gpubase_bygpu_b3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=56
#SBATCH --gpus-per-node=h100:4
#SBATCH --mem=256G
#SBATCH --time=23:00:00
#SBATCH --job-name=c3-hardblock-full

set -u

ROOT=/scratch/memoozd/rl/restriction
RUN_DIR_INPUT="${1:?usage: sbatch submit_c3_full.sbatch RUN_DIR EXPECTED_COMMIT}"
EXPECTED_COMMIT="${2:?usage: sbatch submit_c3_full.sbatch RUN_DIR EXPECTED_COMMIT}"
RUN_DIR="$(cd "${RUN_DIR_INPUT}" && pwd)"
exec > >(tee -a "${RUN_DIR}/allocation.log") 2>&1

hold_allocation() {
  echo "Allocation ${SLURM_JOB_ID} remains available on $(hostname) via sleep infinity."
  sleep infinity
}

echo "job_id=${SLURM_JOB_ID}"
echo "node=$(hostname)"
echo "started_at=$(date --iso-8601=seconds)"
if [[ "$(git -C "${ROOT}" rev-parse HEAD)" != "${EXPECTED_COMMIT}" ]]; then
  echo "refusing C3 launch: repository HEAD differs from prepared commit ${EXPECTED_COMMIT}" >&2
  hold_allocation
fi

{
  date --iso-8601=seconds
  echo "slurm_job_id=${SLURM_JOB_ID}"
  echo "slurm_step_id=${SLURM_STEP_ID:-batch}"
  hostname
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
} > "${RUN_DIR}/hardware.txt"

VERIFIER_ROOT="/tmp/memoozd/DeepSeek-Prover-V1.5-c3-${SLURM_JOB_ID}"
if ! "${ROOT}/scripts/project/stage_deepseek_verifier.sh" \
  /scratch/memoozd/rl/DeepSeek-Prover-V1.5 "${VERIFIER_ROOT}" \
  > "${RUN_DIR}/verifier_staging.log" 2>&1; then
  echo "verifier staging failed; see ${RUN_DIR}/verifier_staging.log" >&2
  printf '%s\n' 2 > "${RUN_DIR}/exit_code.txt"
  hold_allocation
fi

set -o pipefail
export DEEPSEEK_PROVER_ROOT="${VERIFIER_ROOT}"
export DMB_GIT_COMMIT="${EXPECTED_COMMIT}"
"${ROOT}/scripts/project/launch_c3.sh" "${RUN_DIR}" 2>&1 | tee "${RUN_DIR}/run.log"
run_rc=${PIPESTATUS[0]}
printf '%s\n' "${run_rc}" > "${RUN_DIR}/exit_code.txt"
echo "training_process_exit=${run_rc}"
echo "training_process_finished_at=$(date --iso-8601=seconds)"
hold_allocation
