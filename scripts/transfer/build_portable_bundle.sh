#!/usr/bin/env bash
# Assemble one relocatable Restriction-RL directory for transfer to a new cluster.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEST_INPUT="${1:?usage: build_portable_bundle.sh /absolute/path/to/new-bundle}"
DEST="$(realpath -m "${DEST_INPUT}")"
BASE_MODEL_SOURCE="${RESTRICTION_BASE_MODEL_PATH:-/scratch/memoozd/models/DeepSeek-Prover-V1.5-SFT}"
VERIFIER_SOURCE="${DEEPSEEK_PROVER_ROOT:-/scratch/memoozd/rl/DeepSeek-Prover-V1.5}"
ELAN_SOURCE="${ELAN_HOME:-/scratch/memoozd/.elan}"
C0_ARCHIVE_SOURCE="${C0_ARCHIVE_SOURCE:-/home/memoozd/c0-archives}"
LEGACY_ENV_SOURCE="${RESTRICTION_LEGACY_ENV:-${PROJECT_ROOT}/.venv-legacy}"
UV_BIN="${UV_BIN:-$(command -v uv)}"

C1_RUN="c1-grpo-default-full-20260814-seed42-5ced4c3"
C3_RUN="c3-hardblock-restart-full-20260814-seed42-265aecd"
C1_MODEL_SOURCE="${PROJECT_ROOT}/runs/${C1_RUN}/artifacts/actor/global_step_604"
C3_MODEL_SOURCE="${PROJECT_ROOT}/runs/${C3_RUN}/artifacts/actor/global_step_604"

if [[ -e "${DEST}" ]]; then
  echo "refusing existing bundle destination: ${DEST}" >&2
  exit 2
fi
for path in "${BASE_MODEL_SOURCE}" "${VERIFIER_SOURCE}/mathlib4/.lake/build" \
  "${ELAN_SOURCE}/toolchains/leanprover--lean4---v4.9.0-rc1" \
  "${C1_MODEL_SOURCE}" "${C3_MODEL_SOURCE}" \
  "${LEGACY_ENV_SOURCE}/lib/python3.11/site-packages/torch"; do
  if [[ ! -e "${path}" ]]; then
    echo "missing required source: ${path}" >&2
    exit 2
  fi
done

mkdir -p "${DEST}"/{environment/bin,environment/uv-cache,models,repository,runs,verifier,lean,archives,runtime/home}

# Keep the complete repository, including Git history and untracked research
# material, while excluding cluster-bound environments and run payloads copied
# into their own bundle sections below.
rsync -a --link-dest="${PROJECT_ROOT}" \
  --exclude='/runs/' --exclude='/.venv-legacy/' \
  --exclude='/.venv-legacy.copy-partial-20260717/' \
  --exclude='/.venv-legacy.partial-20260717/' \
  "${PROJECT_ROOT}/" "${DEST}/repository/"

# Preserve every run record and proof log, but omit actor checkpoints from
# engineering smokes and intermediate runs. The two authoritative final actors
# are stored exactly once under models/.
rsync -a --link-dest="${PROJECT_ROOT}/runs" \
  --exclude='*/artifacts/actor/***' \
  "${PROJECT_ROOT}/runs/" "${DEST}/runs/"

rsync -a --exclude='/.cache/' --link-dest="${BASE_MODEL_SOURCE}" \
  "${BASE_MODEL_SOURCE}/" "${DEST}/models/base/"
cp -al "${C1_MODEL_SOURCE}" "${DEST}/models/c1-final"
cp -al "${C3_MODEL_SOURCE}" "${DEST}/models/c3-final"
cp -al "${VERIFIER_SOURCE}" "${DEST}/verifier/DeepSeek-Prover-V1.5"
cp -al "${ELAN_SOURCE}" "${DEST}/lean/elan"
if [[ -d "${C0_ARCHIVE_SOURCE}" ]]; then
  rsync -a "${C0_ARCHIVE_SOURCE}/" "${DEST}/archives/c0/"
fi

cp "${UV_BIN}" "${DEST}/environment/bin/uv"
chmod +x "${DEST}/environment/bin/uv"
cp "${PROJECT_ROOT}/scripts/transfer/activate_bundle.sh" "${DEST}/activate.sh"
cp "${PROJECT_ROOT}/scripts/transfer/verify_bundle.py" "${DEST}/verify_bundle.py"
cp "${PROJECT_ROOT}/scripts/transfer/README_TRANSFER.md" "${DEST}/README_TRANSFER.md"
chmod +x "${DEST}/activate.sh" "${DEST}/verify_bundle.py"

# This is an audit of the byte-preserved installed state, not an instruction to
# re-resolve packages against a package index whose historical metadata may
# have changed.
grep -v '^-e ' "${PROJECT_ROOT}/research/legacy-env-freeze.txt" \
  > "${DEST}/environment/requirements.installed.txt"

UV_CACHE_DIR="${DEST}/environment/uv-cache" "${DEST}/environment/bin/uv" python install \
  3.11.4 --install-dir "${DEST}/environment/python" --no-bin
PYTHON_BIN="$(find "${DEST}/environment/python" -type f -path '*/bin/python3.11' -print -quit)"
if [[ -z "${PYTHON_BIN}" ]]; then
  echo "uv did not install the requested Python 3.11.4 runtime" >&2
  exit 2
fi
UV_CACHE_DIR="${DEST}/environment/uv-cache" "${DEST}/environment/bin/uv" venv \
  --relocatable --python "${PYTHON_BIN}" "${DEST}/environment/venv"

# Preserve the actual environment that produced the registered results. A
# fresh resolver currently rejects its historical Torch/NCCL combination even
# though those exact installed bits are known to work together. Hardlinks make
# local assembly cheap; ordinary rsync/tar transfer copies complete file data.
LEGACY_SITE_PACKAGES="${LEGACY_ENV_SOURCE}/lib/python3.11/site-packages"
DEST_SITE_PACKAGES="${DEST}/environment/venv/lib/python3.11/site-packages"
rsync -a --delete --link-dest="${LEGACY_SITE_PACKAGES}" \
  "${LEGACY_SITE_PACKAGES}/" "${DEST_SITE_PACKAGES}/"
printf '%s\n' "$(realpath --relative-to="${DEST_SITE_PACKAGES}" "${DEST}/repository")" \
  > "${DEST_SITE_PACKAGES}/__editable__.verl-0.1.pth"
rm -f "${DEST_SITE_PACKAGES}/verl-0.1.dist-info/direct_url.json"

# Retain package entry points while keeping uv's relocatable activation files
# and interpreter links. Rewrite only the copied scripts' old absolute shebang.
rsync -a \
  --exclude='activate*' --exclude='deactivate*' --exclude='python' \
  --exclude='python3' --exclude='python3.11' --exclude='pydoc.bat' \
  "${LEGACY_ENV_SOURCE}/bin/" "${DEST}/environment/venv/bin/"
find "${DEST}/environment/venv/bin" -maxdepth 1 -type f -print0 | \
  xargs -0 sed -i "1s|^#!${LEGACY_ENV_SOURCE}/bin/python$|#!/usr/bin/env python3|"

# uv records the managed interpreter as an absolute in-bundle symlink. Make it
# relative so the complete top-level directory can be renamed or relocated.
ln -snf ../../python/cpython-3.11.4-linux-x86_64-gnu/bin/python3.11 \
  "${DEST}/environment/venv/bin/python"
ln -snf cpython-3.11.4-linux-x86_64-gnu \
  "${DEST}/environment/python/cpython-3.11-linux-x86_64-gnu"

"${DEST}/environment/venv/bin/python" "${DEST}/verify_bundle.py" "${DEST}" --full-checksums

(cd "${DEST}" && find . -type f \
  ! -path './MANIFEST.sha256' \
  ! -path './SIZE.txt' \
  ! -path './environment/venv/pyvenv.cfg' \
  ! -path './runtime/*' -print0 | \
  sort -z | xargs -0 sha256sum) > "${DEST}/MANIFEST.sha256"
du -sh --apparent-size "${DEST}" > "${DEST}/SIZE.txt"
du -sb --apparent-size "${DEST}" >> "${DEST}/SIZE.txt"
printf '%s\n' "${DEST}"
