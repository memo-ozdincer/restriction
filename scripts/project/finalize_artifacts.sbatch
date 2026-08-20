#!/usr/bin/env bash
#SBATCH --account=def-aspuru_cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=128G
#SBATCH --time=04:00:00
#SBATCH --job-name=restriction-finalize

set -euo pipefail

ROOT=/scratch/memoozd/rl/restriction
ACTION="${1:?usage: sbatch finalize_artifacts.sbatch ACTION RUN_DIR CONDITION CLASSIFICATION EXPECTED_COMMIT}"
RUN_DIR="$(cd "${2:?missing RUN_DIR}" && pwd)"
CONDITION="${3:?missing CONDITION}"
CLASSIFICATION="${4:?missing CLASSIFICATION}"
EXPECTED_COMMIT="${5:?missing EXPECTED_COMMIT}"
NUM_SAMPLES="${6:-32}"
exec > >(tee -a "${RUN_DIR}/finalization.log") 2>&1

git -C "${ROOT}" cat-file -e "${EXPECTED_COMMIT}^{commit}"
EXEC_ROOT="/tmp/memoozd/restriction-finalize-${SLURM_JOB_ID}"
test ! -e "${EXEC_ROOT}"
mkdir -p "${EXEC_ROOT}"
git -C "${ROOT}" archive "${EXPECTED_COMMIT}" | tar -x -C "${EXEC_ROOT}"
ln -s "${ROOT}/.venv-legacy" "${EXEC_ROOT}/.venv-legacy"
export PYTHONPATH="${EXEC_ROOT}:${PYTHONPATH:-}"

case "${ACTION}" in
  training)
    "${EXEC_ROOT}/.venv-legacy/bin/python" \
      "${EXEC_ROOT}/scripts/project/finalize_training_run.py" \
      "${RUN_DIR}" --condition "${CONDITION}" --classification "${CLASSIFICATION}"
    ;;
  evaluation)
    "${EXEC_ROOT}/.venv-legacy/bin/python" \
      "${EXEC_ROOT}/scripts/project/finalize_lean_evaluation.py" \
      "${RUN_DIR}" --condition "${CONDITION}" --num-samples "${NUM_SAMPLES}"
    ;;
  *)
    echo "unknown finalization action: ${ACTION}" >&2
    exit 2
    ;;
esac
