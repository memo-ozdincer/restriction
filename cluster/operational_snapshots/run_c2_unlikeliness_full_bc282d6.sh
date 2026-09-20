#!/usr/bin/env bash
# Run and finalize the registered C2 soft-unlikeliness comparator.
set -euo pipefail
ulimit -c 0

BUNDLE_ROOT=/scratch/memoozd/rrl/restriction-rl
REPOSITORY="${BUNDLE_ROOT}/repository"
VENV_SOURCE="${BUNDLE_ROOT}/environment/venv"
VERIFIER_SOURCE="${BUNDLE_ROOT}/verifier/DeepSeek-Prover-V1.5"
EXPECTED_COMMIT=bc282d66c415f3857939449b045d55fd302f6414
RUN_DIR="${BUNDLE_ROOT}/runs/c2-unlikeliness-2-full-20260909-seed42-bc282d6-h100-workers64"
SYSTEM_GCC_ROOT=/cvmfs/soft.computecanada.ca/gentoo/2023/x86-64-v3/usr/bin

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
  echo "This runner must execute inside a Slurm allocation." >&2
  exit 2
fi
git -C "${REPOSITORY}" cat-file -e "${EXPECTED_COMMIT}^{commit}"
if [[ ! -f "${RUN_DIR}/RUN_METADATA.md" || -e "${RUN_DIR}/artifacts/actor" || -e "${RUN_DIR}/run.log" ]]; then
  echo "Refusing an unprepared or reused C2 directory." >&2
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
    echo "Required native executable is not executable: ${binary}" >&2
    exit 2
  fi
done

LOCAL_ROOT="${SLURM_TMPDIR:-${TMPDIR:-/tmp}}"
EXEC_ROOT="${LOCAL_ROOT}/restriction-c2-${SLURM_JOB_ID}-workers64"
VERIFIER_ROOT="/tmp/memoozd-rrl-verifier-c2-${SLURM_JOB_ID}-workers64"
RUNTIME_HOME="${LOCAL_ROOT}/restriction-home-c2-${SLURM_JOB_ID}-workers64"
RAY_TMP="/dev/shm/r${SLURM_JOB_ID}-c2-workers64"
if [[ -e "${EXEC_ROOT}" || -e "${VERIFIER_ROOT}" || -e "${RUNTIME_HOME}" || -e "${RAY_TMP}" ]]; then
  echo "Refusing to reuse node-local C2 execution state." >&2
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
export RESTRICTION_BASE_MODEL_PATH="${BUNDLE_ROOT}/models/base"
export RESTRICTION_RUNTIME_HOME="${RUNTIME_HOME}"
export RESTRICTION_LEAN_MAX_WORKERS=64
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
  echo "condition=c2_unlikeliness_2"
  echo "model_path=${RESTRICTION_BASE_MODEL_PATH}"
  echo "expected_commit=${EXPECTED_COMMIT}"
  echo "lean_max_workers=${RESTRICTION_LEAN_MAX_WORKERS}"
  echo "rank_penalty=0.25"
  echo "hard_blocking=false"
  echo "operational_runner_sha256=$(sha256sum "$0" | cut -d' ' -f1)"
  hostname
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
} > "${RUN_DIR}/hardware.txt"
cp "$0" "${RUN_DIR}/operational_runner.sh"

# The project contract requires preflight before every scientific run. Execute
# it against the controlled repository while all node-local runtime paths are live.
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
"${EXEC_ROOT}/scripts/project/launch_c2.sh" "${RUN_DIR}" \
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
  "${EXEC_ROOT}/scripts/project/finalize_training_run.py" \
  "${RUN_DIR}" --condition c2_unlikeliness_2 \
  --classification registered_full_seed42 \
  2>&1 | tee "${RUN_DIR}/finalization.log"

PYTHONPATH="${EXEC_ROOT}:${VERIFIER_SOURCE}" \
  "${VENV_SOURCE}/bin/python" - "${RUN_DIR}" <<'PY'
import json
import sys
from pathlib import Path

import yaml

run_dir = Path(sys.argv[1])
metrics = json.loads((run_dir / "metrics.json").read_text())
config = yaml.safe_load((run_dir / "hydra/.hydra/config.yaml").read_text())
assert metrics["condition"] == "c2_unlikeliness_2"
assert metrics["classification"] == "registered_full_seed42"
assert metrics["proposals"] == 308_960
assert metrics["physical_proposals"] == 308_992
assert metrics["expected_registered_proposals"] == 308_960
assert metrics["blocked_correct"] == 0
assert metrics["blocked_correct_zero_advantage"] == 0
assert metrics["blocked_correct_reward_rejected"] == 0
assert metrics["skipped_all_blocked_prompts"] == 0
assert metrics["archive_sha256"] is None
assert config["lean"]["rank_penalty"] == 0.25
assert config["lean"]["hard_blocking"]["enabled"] is False
assert config["lean"]["max_workers"] == 64
assert config["actor_rollout_ref"]["actor"]["ppo_epochs"] == 2
assert config["actor_rollout_ref"]["actor"]["kl_loss_coef"] == 0.10
assert Path(metrics["actor_checkpoint"]).is_dir()
print(
    "validated c2_unlikeliness_2: "
    f"correct={metrics['correct']}, modes={metrics['correct_mode_coverage']}, "
    f"trained={metrics['update_batch_samples']}"
)
PY

echo "The full C2 soft-unlikeliness comparator completed and finalized."
