#!/usr/bin/env bash
set -euo pipefail

# Reuse the cluster-tested PRIME GPU environment while keeping all mutable
# project state on scratch.  This fork intentionally does not resolve its old
# veRL dependency pins into that environment.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRATCH_ROOT="${SCRATCH_ROOT:-/scratch/memoozd}"
PRIME_ROOT="${PRIME_ROOT:-${SCRATCH_ROOT}/rl/prime-rl}"
VENV="${VENV:-${PRIME_ROOT}/.venv}"
PROVER_ROOT="${DEEPSEEK_PROVER_ROOT:-${SCRATCH_ROOT}/rl/DeepSeek-Prover-V1.5}"
UV_BIN="${UV_BIN:-$(command -v uv || true)}"
UV_CACHE_DIR="${UV_CACHE_DIR:-${SCRATCH_ROOT}/.cache/uv}"

if [[ -z "${UV_BIN}" || ! -x "${UV_BIN}" ]]; then
  echo "uv is required; set UV_BIN to its scratch-local path" >&2
  exit 1
fi
if [[ ! -x "${VENV}/bin/python" ]]; then
  echo "Missing tested PRIME venv: ${VENV}" >&2
  exit 1
fi

mkdir -p "${UV_CACHE_DIR}"
if ! "${VENV}/bin/python" -c 'import ray' >/dev/null 2>&1; then
  UV_CACHE_DIR="${UV_CACHE_DIR}" UV_LINK_MODE=copy \
    "${UV_BIN}" pip install --reinstall --python "${VENV}/bin/python" 'ray>=2.38'
fi

if [[ ! -d "${PROVER_ROOT}/.git" ]]; then
  git clone --depth 1 \
    https://github.com/deepseek-ai/DeepSeek-Prover-V1.5.git "${PROVER_ROOT}"
fi
git -C "${PROVER_ROOT}" submodule update --init --depth 1

echo "Environment ready. Activate with:"
echo "  source ${VENV}/bin/activate"
echo "  export DEEPSEEK_PROVER_ROOT=${PROVER_ROOT}"
echo "  export PYTHONPATH=${PROJECT_ROOT}:\${PYTHONPATH:-}"
"${VENV}/bin/python" - <<'PY'
import ray, torch, transformers, vllm
print(f"ray={ray.__version__}")
print(f"torch={torch.__version__} cuda={torch.version.cuda}")
print(f"transformers={transformers.__version__}")
print(f"vllm={vllm.__version__}")
PY
