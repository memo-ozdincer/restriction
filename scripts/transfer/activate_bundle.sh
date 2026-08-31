#!/usr/bin/env bash
# Source this file from the root of a Restriction-RL portable bundle.
set -euo pipefail

BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export RESTRICTION_BUNDLE_ROOT="${BUNDLE_ROOT}"
export RESTRICTION_PROJECT_ROOT="${BUNDLE_ROOT}/repository"
export RESTRICTION_BASE_MODEL_PATH="${BUNDLE_ROOT}/models/base"
export RESTRICTION_C1_MODEL_PATH="${BUNDLE_ROOT}/models/c1-final"
export RESTRICTION_C3_MODEL_PATH="${BUNDLE_ROOT}/models/c3-final"
export RESTRICTION_VENV="${BUNDLE_ROOT}/environment/venv"
export VENV="${RESTRICTION_VENV}"
export VIRTUAL_ENV="${RESTRICTION_VENV}"
export DEEPSEEK_PROVER_ROOT="${BUNDLE_ROOT}/verifier/DeepSeek-Prover-V1.5"
export ELAN_HOME="${BUNDLE_ROOT}/lean/elan"
export RESTRICTION_RUNTIME_HOME="${RESTRICTION_RUNTIME_HOME:-${BUNDLE_ROOT}/runtime/home}"
export HOME="${RESTRICTION_RUNTIME_HOME}"
export UV_CACHE_DIR="${BUNDLE_ROOT}/environment/uv-cache"
export HF_HOME="${BUNDLE_ROOT}/runtime/huggingface"
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export PYTHONPATH="${RESTRICTION_PROJECT_ROOT}:${PYTHONPATH:-}"
export PATH="${RESTRICTION_VENV}/bin:${ELAN_HOME}/bin:${BUNDLE_ROOT}/environment/bin:${PATH}"
export PYTHONUNBUFFERED=1

mkdir -p "${RESTRICTION_RUNTIME_HOME}" "${HF_HOME}"

# A venv records its base interpreter directory as an absolute path. Refresh
# that one in-bundle path after a transfer or rename before invoking Python.
PYVENV_CFG="${RESTRICTION_VENV}/pyvenv.cfg"
PYTHON_BASE_BIN="${BUNDLE_ROOT}/environment/python/cpython-3.11.4-linux-x86_64-gnu/bin"
if [[ ! -f "${PYVENV_CFG}" ]]; then
  echo "portable Python configuration is missing: ${PYVENV_CFG}" >&2
  return 1 2>/dev/null || exit 1
fi
if ! grep -Fqx "home = ${PYTHON_BASE_BIN}" "${PYVENV_CFG}"; then
  sed -i "s|^home = .*$|home = ${PYTHON_BASE_BIN}|" "${PYVENV_CFG}"
fi
unset PYTHONHOME

if [[ ! -x "${RESTRICTION_VENV}/bin/python" ]]; then
  echo "portable Python environment is missing: ${RESTRICTION_VENV}" >&2
  return 1 2>/dev/null || exit 1
fi

cd "${RESTRICTION_PROJECT_ROOT}"
