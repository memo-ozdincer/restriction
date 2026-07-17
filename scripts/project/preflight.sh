#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

fail=0

check_command() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "[ok] command: $1"
  else
    echo "[missing] command: $1"
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

echo "Repository: $ROOT"
git status --short --branch
git remote -v

check_command git
check_command python3
check_command nvidia-smi
check_command ray
check_command lake
check_command lean

check_file papers/2506.02355v2.pdf
check_file data/mff-lwb-10k-seen.parquet
check_file data/mff-lwb-goedel-holdout-800.parquet
check_file data/mff-lwb-unseen-200.parquet
check_file data/minif2f_test.parquet
check_file examples/lean/grpo.sh
check_file verl/trainer/ppo/ray_lean_trainer.py
check_file verl/lean/verifier.py

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
