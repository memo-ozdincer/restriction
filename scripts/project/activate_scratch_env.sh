#!/usr/bin/env bash
# shellcheck shell=bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -n "${RESTRICTION_BUNDLE_ROOT:-}" ]]; then
  VENV="${VENV:-${RESTRICTION_BUNDLE_ROOT}/environment/venv}"
  export DEEPSEEK_PROVER_ROOT="${DEEPSEEK_PROVER_ROOT:-${RESTRICTION_BUNDLE_ROOT}/verifier/DeepSeek-Prover-V1.5}"
  export ELAN_HOME="${ELAN_HOME:-${RESTRICTION_BUNDLE_ROOT}/lean/elan}"
else
  VENV="${VENV:-/scratch/memoozd/rl/prime-rl/.venv}"
  export DEEPSEEK_PROVER_ROOT="${DEEPSEEK_PROVER_ROOT:-/scratch/memoozd/rl/DeepSeek-Prover-V1.5}"
  export ELAN_HOME="${ELAN_HOME:-/scratch/memoozd/.elan}"
fi
export PATH="${ELAN_HOME}/bin:${PATH}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1

if [[ ! -x "${VENV}/bin/python" ]]; then
  echo "Missing Restriction-RL Python environment: ${VENV}." >&2
  return 1 2>/dev/null || exit 1
fi
source "${VENV}/bin/activate"
