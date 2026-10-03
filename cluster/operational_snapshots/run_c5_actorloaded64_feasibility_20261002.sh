#!/usr/bin/env bash
# Execute only inside the persistent full-node allocation, job 1018353.
set -euo pipefail
ulimit -c 0

BUNDLE=/scratch/memoozd/rrl/restriction-rl
REPO="${BUNDLE}/repository"
VENV="${BUNDLE}/environment/venv"
MODEL="${BUNDLE}/models/base"
VERIFIER_SOURCE="${BUNDLE}/verifier/DeepSeek-Prover-V1.5"
SOURCE="${BUNDLE}/runs/c5-reward-reject-full-20260902-seed42-a0f1235-h100-workers32-retry7-24h-exclude-trig0011-trig0031-trig0033-trig0048-trig0058"
PINNED_COMMIT=a0f1235a97ba4e92b25c53c959c7a942e63ee82c
EXPECTED_TRAIN=502d3216ced1829a996869fe31400cece726ac83e0fb469bda0cd9d79961382a
EXPECTED_VALID=05f6176ec4ca85bff8368c64a09049c0e0dad84b1dd3741ace1f8e7de1b35b15
EXPECTED_ARCHIVE=fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3
SYSTEM_GCC_ROOT=/cvmfs/soft.computecanada.ca/gentoo/2023/x86-64-v3/usr/bin

if [[ "${SLURM_JOB_ID:-}" != "1018353" ]]; then
  echo "Expected the authorized workspace allocation 1018353." >&2
  exit 2
fi
if [[ "${SLURM_JOB_ACCOUNT:-}" != "def-zhijing" ]]; then
  echo "Expected the def-zhijing account." >&2
  exit 2
fi
RUN="${BUNDLE}/runs/c5-actorloaded64-feasibility-20261002-${SLURM_JOB_ID}"
EXEC_ROOT="${SLURM_TMPDIR:-/tmp}/c5-feas-code-${SLURM_JOB_ID}"
VERIFIER_ROOT="/tmp/memoozd-c5-feas-verifier-${SLURM_JOB_ID}"
RUNTIME_HOME="${SLURM_TMPDIR:-/tmp}/c5-feas-home-${SLURM_JOB_ID}"
RAY_TMP="/dev/shm/r${SLURM_JOB_ID}c5f"
for path in "$RUN" "$EXEC_ROOT" "$VERIFIER_ROOT" "$RUNTIME_HOME" "$RAY_TMP"; do
  if [[ -e "$path" ]]; then
    echo "Refusing to reuse $path" >&2
    exit 2
  fi
done
for pair in "train.parquet:${EXPECTED_TRAIN}" "valid.parquet:${EXPECTED_VALID}" "block_archive.json:${EXPECTED_ARCHIVE}"; do
  file=${pair%%:*}
  expected=${pair#*:}
  actual=$(sha256sum "${SOURCE}/${file}" | cut -d' ' -f1)
  if [[ "$actual" != "$expected" ]]; then
    echo "Input checksum mismatch: $file" >&2
    exit 2
  fi
done
git -C "$REPO" cat-file -e "${PINNED_COMMIT}^{commit}"
mkdir -p "$RUN" "$EXEC_ROOT" "$RUNTIME_HOME" "$RAY_TMP"
cp "$SOURCE/train.parquet" "$SOURCE/valid.parquet" "$SOURCE/block_archive.json" "$RUN/"
cat > "$RUN/RUN_METADATA.md" <<EOF
# C5 actor-loaded 64-worker feasibility prefix

Classification: operational only; no eligible C5 scientific result.
Source C5 revision: $PINNED_COMMIT.
Frozen input source: $SOURCE.
Stop rule: after step 20 completes or at 6000 seconds, whichever comes first.
Account: def-zhijing. Allocation: $SLURM_JOB_ID.
EOF
git -C "$REPO" archive "$PINNED_COMMIT" | tar -x -C "$EXEC_ROOT"
ln -s "$VENV" "$EXEC_ROOT/.venv-legacy"
ln -s "${BUNDLE}/lean/elan" "$RUNTIME_HOME/.elan"

export RESTRICTION_BUNDLE_ROOT="$BUNDLE"
export RESTRICTION_VENV="$VENV"
export RESTRICTION_BASE_MODEL_PATH="$MODEL"
export RESTRICTION_RUNTIME_HOME="$RUNTIME_HOME"
export RESTRICTION_LEAN_MAX_WORKERS=64
export RESTRICTION_HARD_BLOCK_INTERVENTION=reject_reward
export ELAN_HOME="${BUNDLE}/lean/elan"
export HF_HOME="${BUNDLE}/runtime/huggingface"
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
export DMB_GIT_COMMIT="$PINNED_COMMIT"
export TMPDIR="$RAY_TMP"
export TRITON_CACHE_DIR="$RAY_TMP/triton-cache"
export TORCHINDUCTOR_CACHE_DIR="$RAY_TMP/torchinductor-cache"
export CC="${SYSTEM_GCC_ROOT}/gcc" CXX="${SYSTEM_GCC_ROOT}/g++"
export PATH="${VENV}/bin:${ELAN_HOME}/bin:${SYSTEM_GCC_ROOT}:${PATH}"

bash "$REPO/scripts/project/preflight.sh" > "$RUN/preflight.log" 2>&1
bash "$EXEC_ROOT/scripts/project/stage_deepseek_verifier.sh" \
  "$VERIFIER_SOURCE" "$VERIFIER_ROOT" > "$RUN/staging.log" 2>&1
export DEEPSEEK_PROVER_ROOT="$VERIFIER_ROOT"
{
  echo "classification=operational_prefix_only_not_scientific_result"
  echo "hypothesis=64_verifier_workers_can_coexist_with_loaded_c5_actor"
  echo "stop_after_completed_step=20"
  echo "time_cap_seconds=6000"
  echo "job_id=${SLURM_JOB_ID} account=${SLURM_JOB_ACCOUNT} node=$(hostname)"
  echo "pinned_commit=$PINNED_COMMIT"
  echo "runner_sha256=$(sha256sum "$0" | cut -d' ' -f1)"
  sha256sum "$RUN/train.parquet" "$RUN/valid.parquet" "$RUN/block_archive.json"
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} > "$RUN/operational_metadata.txt"

printf 'timestamp\tmem_available_kib\tgpu_memory_used_mib\trepl_processes\n' > "$RUN/memory.tsv"
(
  while true; do
    available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
    gpu_used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | paste -sd ';' -)
    repl_count=$(pgrep -fc 'lake exe repl|\.lake/packages/REPL/.lake/build/bin/repl' || true)
    printf '%s\t%s\t%s\t%s\n' "$(date --iso-8601=seconds)" "$available" "$gpu_used" "$repl_count"
    sleep 1
  done
) >> "$RUN/memory.tsv" &
monitor_pid=$!
trap 'kill "$monitor_pid" 2>/dev/null || true' EXIT

"$VENV/bin/ray" stop --force >/dev/null 2>&1 || true
set +e
"$VENV/bin/python" "$REPO/scripts/project/stop_after_completed_step.py" \
  --log "$RUN/run.log" --status "$RUN/stop_status.json" \
  --stop-step 20 --max-seconds 6000 -- \
  bash "$EXEC_ROOT/scripts/project/launch_c3.sh" "$RUN"
result=$?
set -e
"$VENV/bin/ray" stop --force >/dev/null 2>&1 || true
kill "$monitor_pid" 2>/dev/null || true
wait "$monitor_pid" 2>/dev/null || true
trap - EXIT
exit "$result"
