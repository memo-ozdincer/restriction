#!/usr/bin/env bash
#SBATCH --account=def-aspuru_cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --job-name=restriction-compare

set -euo pipefail

ROOT=/scratch/memoozd/rl/restriction
OUTPUT="${1:?usage: sbatch compare_pipeline.sbatch OUTPUT C0_EVAL C1_EVAL C3_EVAL C0_TRAIN C1_TRAIN C3_TRAIN EXPECTED_COMMIT}"
C0_EVAL="${2:?missing C0_EVAL}"
C1_EVAL="${3:?missing C1_EVAL}"
C3_EVAL="${4:?missing C3_EVAL}"
C0_TRAIN="${5:?missing C0_TRAIN}"
C1_TRAIN="${6:?missing C1_TRAIN}"
C3_TRAIN="${7:?missing C3_TRAIN}"
EXPECTED_COMMIT="${8:?missing EXPECTED_COMMIT}"
mkdir -p "$(dirname "${OUTPUT}")"
exec > >(tee -a "${OUTPUT}.log") 2>&1

git -C "${ROOT}" cat-file -e "${EXPECTED_COMMIT}^{commit}"
EXEC_ROOT="/tmp/memoozd/restriction-compare-${SLURM_JOB_ID}"
test ! -e "${EXEC_ROOT}"
mkdir -p "${EXEC_ROOT}"
git -C "${ROOT}" archive "${EXPECTED_COMMIT}" | tar -x -C "${EXEC_ROOT}"
ln -s "${ROOT}/.venv-legacy" "${EXEC_ROOT}/.venv-legacy"
export PYTHONPATH="${EXEC_ROOT}:${PYTHONPATH:-}"

"${EXEC_ROOT}/.venv-legacy/bin/python" \
  "${EXEC_ROOT}/scripts/project/compare_registered_evaluations.py" \
  --c0-base-eval "${C0_EVAL}" \
  --c1-grpo-default-eval "${C1_EVAL}" \
  --c3-hardblock-restart-eval "${C3_EVAL}" \
  --c0-base-training "${C0_TRAIN}" \
  --c1-grpo-default-training "${C1_TRAIN}" \
  --c3-hardblock-restart-training "${C3_TRAIN}" \
  --output "${OUTPUT}"
