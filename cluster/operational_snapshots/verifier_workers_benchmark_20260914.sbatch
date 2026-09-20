#!/usr/bin/env bash
#SBATCH --job-name=verifier-workers32-64
#SBATCH --account=def-zhijing
#SBATCH --partition=compute_full_node
#SBATCH --nodes=1
#SBATCH --gpus-per-node=h100:4
#SBATCH --cpus-per-task=96
#SBATCH --time=02:00:00
#SBATCH --output=/scratch/memoozd/rrl/slurm-%x-%j.out

set -euo pipefail
ulimit -c 0
BUNDLE=/scratch/memoozd/rrl/restriction-rl
REPOSITORY="${BUNDLE}/repository"
COMMIT=26a8628a1f41be7586ec526ab5bb23acfb406b99
RUN="${BUNDLE}/runs/verifier-workers-benchmark-20260914-${SLURM_JOB_ID}"
EXEC_ROOT="${SLURM_TMPDIR:-/tmp}/verifier-bench-code-${SLURM_JOB_ID}"
VERIFIER_ROOT="/tmp/memoozd-verifier-bench-${SLURM_JOB_ID}"
if [[ -e "${RUN}" || -e "${EXEC_ROOT}" || -e "${VERIFIER_ROOT}" ]]; then
  echo "Refusing reused benchmark state." >&2
  exit 2
fi
mkdir -p "${RUN}" "${EXEC_ROOT}"
git -C "${REPOSITORY}" archive "${COMMIT}" | tar -x -C "${EXEC_ROOT}"
export RESTRICTION_VENV="${BUNDLE}/environment/venv"
export ELAN_HOME="${BUNDLE}/lean/elan"
export PATH="${RESTRICTION_VENV}/bin:${ELAN_HOME}/bin:${PATH}"
export DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB=32
export PYTHONDONTWRITEBYTECODE=1
bash "${REPOSITORY}/scripts/project/preflight.sh" > "${RUN}/preflight.log" 2>&1
bash "${EXEC_ROOT}/scripts/project/stage_deepseek_verifier.sh" \
  "${BUNDLE}/verifier/DeepSeek-Prover-V1.5" "${VERIFIER_ROOT}" > "${RUN}/staging.log" 2>&1
export DEEPSEEK_PROVER_ROOT="${VERIFIER_ROOT}"
patch -d "${VERIFIER_ROOT}" -p1 < "${EXEC_ROOT}/scripts/project/patches/benchmark_lake_path.patch"
test -x "${ELAN_HOME}/bin/lake"
export PYTHONPATH="${EXEC_ROOT}:${VERIFIER_ROOT}"
{
  date --iso-8601=seconds
  echo "job=${SLURM_JOB_ID} commit=${COMMIT} account=${SLURM_JOB_ACCOUNT}"
  echo "timeout_seconds=300 memory_limit_gib=32 actor_loaded=false"
  hostname
  lscpu
  free -k
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  sha256sum "${EXEC_ROOT}/scripts/project/benchmark_verifier_workers.py" \
    "${EXEC_ROOT}/verl/lean/verifier.py" "${VERIFIER_ROOT}/prover/lean/verifier.py"
} > "${RUN}/hardware.txt"
cd "${VERIFIER_ROOT}"
"${RESTRICTION_VENV}/bin/python" "${EXEC_ROOT}/scripts/project/benchmark_verifier_workers.py" \
  --c2-run "${BUNDLE}/runs/c2-unlikeliness-2-full-20260909-seed42-bc282d6-h100-workers64" \
  --c3-run "${BUNDLE}/runs/c3-hardblock-restart-full-20260814-seed42-265aecd" \
  --output-dir "${RUN}/results" 2>&1 | tee "${RUN}/run.log"
