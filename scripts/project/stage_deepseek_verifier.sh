#!/usr/bin/env bash
# Copy the pinned DeepSeek verifier workspace to node-local storage, then apply
# the audited result-handoff robustness patch.
set -euo pipefail

SOURCE_ROOT="${1:-${DEEPSEEK_PROVER_ROOT:-/scratch/memoozd/rl/DeepSeek-Prover-V1.5}}"
DEST_ROOT="${2:-${TMPDIR:-/tmp}/${USER:-restriction}/DeepSeek-Prover-V1.5-c0-local}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATCH_FILE="${ROOT}/scripts/project/patches/deepseek_verifier_compact_result.patch"

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
patch -d "${DEST_ROOT}" -p1 < "${PATCH_FILE}"
test -d "${DEST_ROOT}/mathlib4/.lake/build"
printf '%s\n' "${DEST_ROOT}"
