#!/usr/bin/env bash
# shellcheck shell=bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV="${VENV:-/scratch/memoozd/rl/prime-rl/.venv}"
export DEEPSEEK_PROVER_ROOT="${DEEPSEEK_PROVER_ROOT:-/scratch/memoozd/rl/DeepSeek-Prover-V1.5}"
export ELAN_HOME="${ELAN_HOME:-/scratch/memoozd/.elan}"
export PATH="${ELAN_HOME}/bin:${PATH}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1

if [[ ! -x "${VENV}/bin/python" ]]; then
  echo "Missing scratch PRIME venv: ${VENV}. Run setup_scratch_env.sh." >&2
  return 1 2>/dev/null || exit 1
fi
source "${VENV}/bin/activate"
