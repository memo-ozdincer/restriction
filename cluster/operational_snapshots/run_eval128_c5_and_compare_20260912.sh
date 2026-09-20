#!/usr/bin/env bash
# Evaluate finalized C5 at pass@128, then execute the frozen C2/C5 panels.
set -euo pipefail
ulimit -c 0

BUNDLE_ROOT=/scratch/memoozd/rrl/restriction-rl
REPOSITORY="${BUNDLE_ROOT}/repository"
VENV_SOURCE="${BUNDLE_ROOT}/environment/venv"
VERIFIER_SOURCE="${BUNDLE_ROOT}/verifier/DeepSeek-Prover-V1.5"
EXPECTED_COMMIT=a51fff96ce424773bec594c9ab1a893a2bc9837c
C5_TRAIN_RUN="${BUNDLE_ROOT}/runs/c5-reward-reject-full-20260902-seed42-a0f1235-h100-workers32-retry7-24h-exclude-trig0011-trig0031-trig0033-trig0048-trig0058"
C3_TRAIN_RUN="${BUNDLE_ROOT}/runs/c3-hardblock-restart-full-20260814-seed42-265aecd"
C0_ARCHIVE="${BUNDLE_ROOT}/runs/c0-base-20260804-seed42-complete/mode_archive.json"
RUN_DIR="${BUNDLE_ROOT}/runs/eval128-c5-reward-reject-20260912-seed42-workers16"
MODEL_PATH="${C5_TRAIN_RUN}/artifacts/actor/global_step_604"
C0_EVAL="${BUNDLE_ROOT}/runs/eval128-c0-base-20260901-seed42-8dc7563-retry4-workers16-disk"
C3_EVAL="${BUNDLE_ROOT}/runs/eval128-c3-hardblock-restart-20260901-seed42-8dc7563-retry3-workers16-disk"
EVALUATION_RESULT="${REPOSITORY}/results/c2_vs_c5_seed42_pass128.json"
NUM_SAMPLES=128
SYSTEM_GCC_ROOT=/cvmfs/soft.computecanada.ca/gentoo/2023/x86-64-v3/usr/bin

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
  echo "This runner must execute inside a Slurm allocation." >&2
  exit 2
fi
git -C "${REPOSITORY}" cat-file -e "${EXPECTED_COMMIT}^{commit}"
if [[ ! -f "${RUN_DIR}/RUN_METADATA.md" || ! -d "${MODEL_PATH}" ]]; then
  echo "Missing fresh C5 evaluation directory or finalized C5 model." >&2
  exit 2
fi
if [[ -e "${RUN_DIR}/artifacts/proofs" || -e "${RUN_DIR}/metrics.json" || -e "${RUN_DIR}/run.log" ]]; then
  echo "Refusing a reused C5 evaluation directory." >&2
  exit 2
fi
if [[ -e "${EVALUATION_RESULT}" ]]; then
  echo "Refusing to overwrite an existing registered C5 comparison." >&2
  exit 2
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
    echo "Required native runtime is not executable: ${binary}" >&2
    exit 2
  fi
done

LOCAL_ROOT="${SLURM_TMPDIR:-${TMPDIR:-/tmp}}"
EXEC_ROOT="${LOCAL_ROOT}/restriction-eval-c5-${SLURM_JOB_ID}-workers16"
VERIFIER_ROOT="/tmp/memoozd-rrl-verifier-eval-c5-${SLURM_JOB_ID}-workers16"
RUNTIME_HOME="${LOCAL_ROOT}/restriction-home-eval-c5-${SLURM_JOB_ID}-workers16"
RAY_TMP="/dev/shm/r${SLURM_JOB_ID}c5e"
if [[ -e "${EXEC_ROOT}" || -e "${VERIFIER_ROOT}" || -e "${RUNTIME_HOME}" || -e "${RAY_TMP}" ]]; then
  echo "Refusing to reuse node-local C5 evaluation state." >&2
  exit 2
fi
mkdir -p "${EXEC_ROOT}" "${RUNTIME_HOME}" "${RAY_TMP}"
git -C "${REPOSITORY}" archive "${EXPECTED_COMMIT}" | tar -x -C "${EXEC_ROOT}"
ln -s "${VENV_SOURCE}" "${EXEC_ROOT}/.venv-legacy"
ln -s "${BUNDLE_ROOT}/lean/elan" "${RUNTIME_HOME}/.elan"

echo "Staging the pinned Lean verifier to disk-backed node-local storage."
"${EXEC_ROOT}/scripts/project/stage_deepseek_verifier.sh" \
  "${VERIFIER_SOURCE}" "${VERIFIER_ROOT}" \
  > "${RUN_DIR}/verifier_staging.log" 2>&1
staged_kib=$(du -s "${VERIFIER_ROOT}" | awk '{print $1}')
echo "staged_kib=${staged_kib}" >> "${RUN_DIR}/verifier_staging.log"
df -hT /tmp >> "${RUN_DIR}/verifier_staging.log"
if (( staged_kib > 10485760 )); then
  echo "Verifier staging unexpectedly exceeds 10 GiB." >&2
  exit 2
fi

export RESTRICTION_VENV="${VENV_SOURCE}"
export RESTRICTION_BUNDLE_ROOT="${BUNDLE_ROOT}"
export RESTRICTION_RUNTIME_HOME="${RUNTIME_HOME}"
export RESTRICTION_LEAN_MAX_WORKERS=16
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
  echo "model_path=${MODEL_PATH}"
  echo "expected_commit=${EXPECTED_COMMIT}"
  echo "lean_max_workers=${RESTRICTION_LEAN_MAX_WORKERS}"
  echo "num_samples=${NUM_SAMPLES}"
  echo "operational_runner_sha256=$(sha256sum "$0" | cut -d' ' -f1)"
  hostname
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
} > "${RUN_DIR}/hardware.txt"
cp "$0" "${RUN_DIR}/operational_runner.sh"

"${REPOSITORY}/scripts/project/preflight.sh" \
  > "${RUN_DIR}/preflight.log" 2>&1

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
"${EXEC_ROOT}/scripts/project/launch_lean_evaluation.sh" \
  "${RUN_DIR}" "${MODEL_PATH}" "${NUM_SAMPLES}" \
  2>&1 | tee "${RUN_DIR}/run.log"
run_rc=${PIPESTATUS[0]}
set -e
printf '%s\n' "${run_rc}" > "${RUN_DIR}/exit_code.txt"
"${VENV_SOURCE}/bin/ray" stop --force >/dev/null 2>&1 || true
kill "${monitor_pid}" 2>/dev/null || true
wait "${monitor_pid}" 2>/dev/null || true
trap - EXIT

PYTHONPATH="${EXEC_ROOT}:${VERIFIER_SOURCE}" \
  "${VENV_SOURCE}/bin/python" \
  "${EXEC_ROOT}/scripts/project/finalize_lean_evaluation.py" \
  "${RUN_DIR}" --condition c5_reward_reject_restart --num-samples "${NUM_SAMPLES}" \
  2>&1 | tee "${RUN_DIR}/finalization.log"

"${VENV_SOURCE}/bin/python" - "${RUN_DIR}/metrics.json" <<'PY'
import json
import sys
from pathlib import Path

metrics = json.loads(Path(sys.argv[1]).read_text())
assert metrics["condition"] == "c5_reward_reject_restart"
assert metrics["registered_proposals"] == 59_776
assert metrics["physical_proposals"] == 59_904
assert metrics["classification"] == "registered_evaluation_128"
assert metrics["completion_marker"] == "upstream_post_completion_stop_sentinel"
print(
    f"validated c5_reward_reject_restart pass@128: correct={metrics['correct']}, "
    f"physical={metrics['physical_proposals']}"
)
PY

PYTHONPATH="${EXEC_ROOT}:${VERIFIER_SOURCE}" \
  "${VENV_SOURCE}/bin/python" \
  "${EXEC_ROOT}/scripts/project/analyze_c2_c5_evaluation.py" \
  --c0-run "${C0_EVAL}" \
  --c1-run "${BUNDLE_ROOT}/runs/eval128-c1-grpo-default-20260901-seed42-8dc7563-retry9-workers16-disk" \
  --c2-run "${BUNDLE_ROOT}/runs/eval128-c2-unlikeliness-2-20260909-seed42-bc282d6-workers16" \
  --c5-run "${RUN_DIR}" --output "${EVALUATION_RESULT}"
analysis_runner=/scratch/memoozd/rrl/run_c5_training_analysis_retry7_24h_a499d1c3.sh
analysis_sha=$(sha256sum "${analysis_runner}" | cut -d' ' -f1)
if [[ "${analysis_sha}" != a499d1c33d8c6b5d123aba0c1cbfafc61a652ae2adcf2d0e6b947aacc268c418 ]]; then
  echo "Frozen C5 training analysis runner changed." >&2
  exit 2
fi
bash "${analysis_runner}"
echo "C5 pass@128, C2/C5 comparison, and C5/C3 training analysis completed."
