#!/usr/bin/env bash
# Run retry 7 of the full C5 condition after runtime-only node exclusions.
set -euo pipefail
ulimit -c 0

BUNDLE_ROOT=/scratch/memoozd/rrl/restriction-rl
REPOSITORY="${BUNDLE_ROOT}/repository"
VENV_SOURCE="${BUNDLE_ROOT}/environment/venv"
VERIFIER_SOURCE="${BUNDLE_ROOT}/verifier/DeepSeek-Prover-V1.5"
EXPECTED_COMMIT=a0f1235a97ba4e92b25c53c959c7a942e63ee82c
VALIDATION_COMMIT=5a9ef4a12c94719f5e7c16521e90823756158aa2
RUN_DIR="${BUNDLE_ROOT}/runs/c5-reward-reject-full-20260902-seed42-a0f1235-h100-workers32-retry7-24h-exclude-trig0011-trig0031-trig0033-trig0048-trig0058"
PRIMARY_RUN_DIR="${BUNDLE_ROOT}/runs/c5-reward-reject-full-20260901-seed42-a0f1235-h100-workers32"
PRIMARY_RECOVERY="${PRIMARY_RUN_DIR}/recovery_validation.json"
SYSTEM_GCC_ROOT=/cvmfs/soft.computecanada.ca/gentoo/2023/x86-64-v3/usr/bin

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
  echo "This runner must execute inside a Slurm allocation." >&2
  exit 2
fi
git -C "${REPOSITORY}" cat-file -e "${EXPECTED_COMMIT}^{commit}"
git -C "${REPOSITORY}" cat-file -e "${VALIDATION_COMMIT}^{commit}"

# The primary's original operational wrapper incorrectly expected one
# hard-blocking summary per dataloader step. Dynamic buffering emits one per
# optimizer update instead. If the primary reached complete, independently
# validated scientific artifacts and failed only at that stale assertion,
# recover those artifacts instead of spending another full training budget.
if [[ -f "${PRIMARY_RUN_DIR}/metrics.json" && -f "${PRIMARY_RUN_DIR}/finalization.log" ]]; then
  validation_root=$(mktemp -d "${SLURM_TMPDIR:-/tmp}/c5-primary-validation.XXXXXX")
  git -C "${REPOSITORY}" archive "${VALIDATION_COMMIT}" \
    scripts/project/validate_c5_reward_reject_run.py | tar -x -C "${validation_root}"
  if "${VENV_SOURCE}/bin/python" \
      "${validation_root}/scripts/project/validate_c5_reward_reject_run.py" \
      "${PRIMARY_RUN_DIR}" --output "${PRIMARY_RECOVERY}"; then
    rm -rf -- "${validation_root}"
    echo "Recovered the complete primary C5 artifacts after wrapper-only validation failure."
    exit 0
  fi
  rm -rf -- "${validation_root}"
  if [[ -e "${PRIMARY_RECOVERY}" ]]; then
    echo "Primary recovery output exists despite failed validation." >&2
    exit 2
  fi
  echo "Primary artifacts did not pass corrected validation; starting the pristine retry."
fi

for binary in \
  "${VENV_SOURCE}/lib/python3.11/site-packages/ray/core/src/ray/gcs/gcs_server" \
  "${VENV_SOURCE}/lib/python3.11/site-packages/ray/core/src/ray/raylet/raylet" \
  "${VENV_SOURCE}/lib/python3.11/site-packages/triton/third_party/cuda/bin/ptxas" \
  "${VENV_SOURCE}/lib/python3.11/site-packages/triton/third_party/cuda/bin/cuobjdump" \
  "${VENV_SOURCE}/lib/python3.11/site-packages/triton/third_party/cuda/bin/nvdisasm" \
  "${VENV_SOURCE}/lib/python3.11/site-packages/torch/bin/torch_shm_manager" \
  "${SYSTEM_GCC_ROOT}/gcc" \
  "${SYSTEM_GCC_ROOT}/g++"; do
  if [[ ! -x "${binary}" ]]; then
    echo "Ray native executable is not executable: ${binary}" >&2
    exit 2
  fi
done
if [[ ! -f "${RUN_DIR}/RUN_METADATA.md" || ! -f "${RUN_DIR}/block_archive.json" || -e "${RUN_DIR}/artifacts" || -e "${RUN_DIR}/run.log" || -e "${RUN_DIR}/metrics.json" ]]; then
  echo "Refusing an unprepared or reused C5 full-run directory." >&2
  exit 2
fi

LOCAL_ROOT="${SLURM_TMPDIR:-${TMPDIR:-/tmp}}"
EXEC_ROOT="${LOCAL_ROOT}/restriction-c5-full-${SLURM_JOB_ID}-workers32"
# Sparse Mathlib artifacts can materialize during verification, so keep the
# verifier on disk-backed /tmp rather than charging that growth to node RAM.
VERIFIER_ROOT="/tmp/memoozd-rrl-verifier-c5-full-${SLURM_JOB_ID}-workers32"
RUNTIME_HOME="${LOCAL_ROOT}/restriction-home-c5-full-${SLURM_JOB_ID}-workers32"
# Ray appends a long session/socket suffix; keep this prefix deliberately short.
RAY_TMP="/dev/shm/r${SLURM_JOB_ID}c5f"
if [[ -e "${EXEC_ROOT}" || -e "${VERIFIER_ROOT}" || -e "${RUNTIME_HOME}" || -e "${RAY_TMP}" ]]; then
  echo "Refusing to reuse node-local execution state." >&2
  exit 2
fi

mkdir -p "${EXEC_ROOT}" "${RUNTIME_HOME}" "${RAY_TMP}"
git -C "${REPOSITORY}" archive "${EXPECTED_COMMIT}" | tar -x -C "${EXEC_ROOT}"
ln -s "${VENV_SOURCE}" "${EXEC_ROOT}/.venv-legacy"
ln -s "${BUNDLE_ROOT}/lean/elan" "${RUNTIME_HOME}/.elan"

echo "Staging the pinned Lean verifier sparsely to disk-backed /tmp."
"${EXEC_ROOT}/scripts/project/stage_deepseek_verifier.sh" \
  "${VERIFIER_SOURCE}" "${VERIFIER_ROOT}" \
  > "${RUN_DIR}/verifier_staging.log" 2>&1
staged_kib=$(du -s "${VERIFIER_ROOT}" | awk '{print $1}')
echo "staged_kib=${staged_kib}" >> "${RUN_DIR}/verifier_staging.log"
df -hT /tmp >> "${RUN_DIR}/verifier_staging.log"
if (( staged_kib > 10485760 )); then
  echo "Sparse verifier staging unexpectedly exceeds 10 GiB." >&2
  exit 2
fi

export RESTRICTION_VENV="${VENV_SOURCE}"
export RESTRICTION_BUNDLE_ROOT="${BUNDLE_ROOT}"
export RESTRICTION_BASE_MODEL_PATH="${BUNDLE_ROOT}/models/base"
export RESTRICTION_RUNTIME_HOME="${RUNTIME_HOME}"
export RESTRICTION_LEAN_MAX_WORKERS=32
export RESTRICTION_HARD_BLOCK_INTERVENTION=reject_reward
export DEEPSEEK_PROVER_ROOT="${VERIFIER_ROOT}"
export ELAN_HOME="${BUNDLE_ROOT}/lean/elan"
export HF_HOME="${BUNDLE_ROOT}/runtime/huggingface"
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export DMB_GIT_COMMIT="${EXPECTED_COMMIT}"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="${RAY_TMP}"
export TRITON_CACHE_DIR="${RAY_TMP}/triton-cache"
export TORCHINDUCTOR_CACHE_DIR="${RAY_TMP}/torchinductor-cache"
export CC="${SYSTEM_GCC_ROOT}/gcc"
export CXX="${SYSTEM_GCC_ROOT}/g++"
export PATH="${VENV_SOURCE}/bin:${ELAN_HOME}/bin:${SYSTEM_GCC_ROOT}:${PATH}"

{
  date --iso-8601=seconds
  echo "slurm_job_id=${SLURM_JOB_ID}"
  echo "condition=c5_reward_reject_restart"
  echo "model_path=${RESTRICTION_BASE_MODEL_PATH}"
  echo "expected_commit=${EXPECTED_COMMIT}"
  echo "lean_max_workers=${RESTRICTION_LEAN_MAX_WORKERS}"
  echo "hard_block_intervention=${RESTRICTION_HARD_BLOCK_INTERVENTION}"
  echo "classification=exploratory_full_seed42_h100"
  echo "launch_reason=d111_retry6_step80_runtime_gate_exclude_trig0011_trig0031_trig0033_trig0048_trig0058"
  echo "operational_runner_sha256=$(sha256sum "$0" | cut -d' ' -f1)"
  hostname
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
} > "${RUN_DIR}/hardware.txt"
cp "$0" "${RUN_DIR}/operational_runner.sh"

printf 'timestamp\tmem_available_kib\tmem_used_kib\trepl_processes\n' > "${RUN_DIR}/memory.tsv"
(
  while true; do
    available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
    total=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
    used=$((total - available))
    repl_processes=$(pgrep -fc 'lake exe repl|\.lake/packages/REPL/.lake/build/bin/repl' || true)
    printf '%s\t%s\t%s\t%s\n' "$(date --iso-8601=seconds)" "${available}" "${used}" "${repl_processes}"
    sleep 15
  done
) >> "${RUN_DIR}/memory.tsv" &
monitor_pid=$!
trap 'kill "${monitor_pid}" 2>/dev/null || true' EXIT

"${VENV_SOURCE}/bin/ray" stop --force >/dev/null 2>&1 || true
set +e
set -o pipefail
"${EXEC_ROOT}/scripts/project/launch_c3.sh" "${RUN_DIR}" \
  2>&1 | tee "${RUN_DIR}/run.log"
run_rc=${PIPESTATUS[0]}
set -e
printf '%s\n' "${run_rc}" > "${RUN_DIR}/exit_code.txt"
"${VENV_SOURCE}/bin/ray" stop --force >/dev/null 2>&1 || true
kill "${monitor_pid}" 2>/dev/null || true
wait "${monitor_pid}" 2>/dev/null || true
trap - EXIT

PYTHONPATH="${EXEC_ROOT}:${PYTHONPATH:-}" \
  "${VENV_SOURCE}/bin/python" \
  "${EXEC_ROOT}/scripts/project/finalize_training_run.py" \
  "${RUN_DIR}" --condition c5_reward_reject_restart \
  --classification exploratory_full_seed42_h100 \
  2>&1 | tee "${RUN_DIR}/finalization.log"

validation_root=$(mktemp -d "${LOCAL_ROOT}/c5-retry-validation.XXXXXX")
git -C "${REPOSITORY}" archive "${VALIDATION_COMMIT}" \
  scripts/project/validate_c5_reward_reject_run.py | tar -x -C "${validation_root}"
"${VENV_SOURCE}/bin/python" \
  "${validation_root}/scripts/project/validate_c5_reward_reject_run.py" \
  "${RUN_DIR}" 2>&1 | tee "${RUN_DIR}/corrected_validation.log"
rm -rf -- "${validation_root}"

echo "The exploratory full C5 reward-rejection run completed and finalized."
