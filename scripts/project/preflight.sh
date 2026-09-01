#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PYTHON_ENV="${RESTRICTION_VENV:-${VENV:-/scratch/memoozd/rl/prime-rl/.venv}}"
ELAN_ROOT="${ELAN_HOME:-/scratch/memoozd/.elan}"
export PATH="${ELAN_ROOT}/bin:${PYTHON_ENV}/bin:${PATH}"

fail=0

check_command() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "[ok] command: $1"
  else
    echo "[missing] command: $1"
    fail=1
  fi
}

check_scratch_python_module() {
  local module="$1"
  local python_bin="${PYTHON_ENV}/bin/python"
  if [[ -x "$python_bin" ]] && "$python_bin" -c "import ${module}" >/dev/null 2>&1; then
    echo "[ok] scratch python module: ${module}"
  else
    echo "[missing] scratch python module: ${module}"
    fail=1
  fi
}

check_file() {
  if [[ -f "$1" ]]; then
    echo "[ok] file: $1"
  else
    echo "[missing] file: $1"
    fail=1
  fi
}

check_executable() {
  local path="$1"
  local label="$2"
  if [[ -x "$path" ]]; then
    echo "[ok] executable: ${label} (${path})"
  else
    echo "[missing or not executable] ${label}: ${path}"
    fail=1
  fi
}

echo "Repository: $ROOT"
git status --short --branch
git remote -v

check_command git
check_command python3
check_command nvidia-smi
check_command gcc
check_scratch_python_module ray
check_executable \
  "${PYTHON_ENV}/lib/python3.11/site-packages/ray/core/src/ray/gcs/gcs_server" \
  "Ray GCS server"
check_executable \
  "${PYTHON_ENV}/lib/python3.11/site-packages/ray/core/src/ray/raylet/raylet" \
  "Ray raylet"
check_executable \
  "${PYTHON_ENV}/lib/python3.11/site-packages/triton/third_party/cuda/bin/ptxas" \
  "Triton ptxas"
check_executable \
  "${PYTHON_ENV}/lib/python3.11/site-packages/triton/third_party/cuda/bin/cuobjdump" \
  "Triton cuobjdump"
check_executable \
  "${PYTHON_ENV}/lib/python3.11/site-packages/triton/third_party/cuda/bin/nvdisasm" \
  "Triton nvdisasm"
check_executable \
  "${PYTHON_ENV}/lib/python3.11/site-packages/torch/bin/torch_shm_manager" \
  "PyTorch shared-memory manager"
check_executable "${ELAN_ROOT}/bin/lake" "pinned lake"
check_executable "${ELAN_ROOT}/bin/lean" "pinned lean"
if [[ -n "${DEEPSEEK_PROVER_ROOT:-}" ]]; then
  check_executable \
    "${DEEPSEEK_PROVER_ROOT}/mathlib4/.lake/packages/REPL/.lake/build/bin/repl" \
    "pinned verifier REPL"
fi

check_file papers/2506.02355v2.pdf
check_file data/mff-lwb-10k-seen.parquet
check_file data/mff-lwb-goedel-holdout-800.parquet
check_file data/mff-lwb-unseen-200.parquet
check_file data/minif2f_test.parquet
check_file examples/lean/grpo.sh
check_file verl/trainer/ppo/ray_lean_trainer.py
check_file verl/lean/verifier.py

if [[ -x "${PYTHON_ENV}/bin/python" ]]; then
    echo "[ok] Python environment: ${PYTHON_ENV}"
else
    echo "[missing] Python environment: ${PYTHON_ENV}"
    fail=1
fi

echo
echo "GPU status:"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
  echo "nvidia-smi unavailable"
fi

echo
echo "Dataset checksums:"
sha256sum data/*.parquet 2>/dev/null || shasum -a 256 data/*.parquet

echo
echo "Paper checksum:"
sha256sum papers/2506.02355v2.pdf 2>/dev/null || \
  shasum -a 256 papers/2506.02355v2.pdf

if [[ "$fail" -ne 0 ]]; then
  echo
  echo "Preflight has missing requirements. See cluster/HANDOFF.md."
  exit 1
fi

echo
echo "Preflight passed."
