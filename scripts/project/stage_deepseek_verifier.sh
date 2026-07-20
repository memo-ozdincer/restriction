#!/usr/bin/env bash
# Copy the existing DeepSeek verifier workspace to node-local storage unchanged.
set -euo pipefail

SOURCE_ROOT="${1:-/scratch/memoozd/rl/DeepSeek-Prover-V1.5}"
DEST_ROOT="${2:-/tmp/memoozd/DeepSeek-Prover-V1.5-c0-local}"

if [[ ! -d "${SOURCE_ROOT}/mathlib4" ]]; then
  echo "missing DeepSeek verifier workspace: ${SOURCE_ROOT}" >&2
  exit 2
fi
if [[ -e "${DEST_ROOT}" ]]; then
  echo "refusing to overwrite existing local verifier workspace: ${DEST_ROOT}" >&2
  exit 2
fi

mkdir -p "$(dirname "${DEST_ROOT}")"
rsync -a "${SOURCE_ROOT}/" "${DEST_ROOT}/"
test -d "${DEST_ROOT}/mathlib4/.lake/build"
printf '%s\n' "${DEST_ROOT}"
