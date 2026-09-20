#!/usr/bin/env bash
# Run the frozen C5-versus-C3 analysis after retry-7 finalization.
set -euo pipefail

BUNDLE_ROOT=/scratch/memoozd/rrl/restriction-rl
REPOSITORY="${BUNDLE_ROOT}/repository"
VENV="${BUNDLE_ROOT}/environment/venv"
EXPECTED_COMMIT=39ba50dcd35cd90500f1674f36fcc32a43bb715d
C0_ARCHIVE="${BUNDLE_ROOT}/runs/c0-base-20260804-seed42-complete/mode_archive.json"
C3_RUN="${BUNDLE_ROOT}/runs/c3-hardblock-restart-full-20260814-seed42-265aecd"
PRIMARY_C5_RUN="${BUNDLE_ROOT}/runs/c5-reward-reject-full-20260901-seed42-a0f1235-h100-workers32"
FALLBACK_C5_RUN="${BUNDLE_ROOT}/runs/c5-reward-reject-full-20260902-seed42-a0f1235-h100-workers32-retry7-24h-exclude-trig0011-trig0031-trig0033-trig0048-trig0058"
if [[ -f "${PRIMARY_C5_RUN}/recovery_validation.json" ]]; then
  "${VENV}/bin/python" - "${PRIMARY_C5_RUN}/recovery_validation.json" "${PRIMARY_C5_RUN}" <<'PY'
import json
import sys
from pathlib import Path

record = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert record["validation"] == "c5-reward-rejection-finalized-v2"
assert Path(record["run_dir"]).resolve() == Path(sys.argv[2]).resolve()
assert record["dataloader_steps"] == 604
assert record["optimizer_updates"] > 0
assert record["retained_samples"] >= record["optimized_samples"] > 0
assert 0 <= record["residual_buffer_samples"] <= 255
PY
  C5_RUN="${PRIMARY_C5_RUN}"
else
  C5_RUN="${FALLBACK_C5_RUN}"
fi
OUTPUT="${REPOSITORY}/results/c5_vs_c3_training_seed42.json"
LOG="${C5_RUN}/c5_training_analysis.log"

if [[ -z "${SLURM_JOB_ID:-}" ]]; then
  echo "This runner must execute inside a Slurm allocation." >&2
  exit 2
fi
git -C "${REPOSITORY}" cat-file -e "${EXPECTED_COMMIT}^{commit}"
if [[ ! -f "${C5_RUN}/metrics.json" || ! -f "${C5_RUN}/finalization.log" ]]; then
  echo "Complete finalized C5 inputs do not exist." >&2
  exit 2
fi
if [[ -e "${OUTPUT}" || -e "${LOG}" ]]; then
  echo "Refusing to overwrite an existing C5 analysis." >&2
  exit 2
fi

EXEC_ROOT="/tmp/memoozd-c5-analysis-${SLURM_JOB_ID}"
if [[ -e "${EXEC_ROOT}" ]]; then
  echo "Refusing to reuse analysis execution state." >&2
  exit 2
fi
mkdir -p "${EXEC_ROOT}"
git -C "${REPOSITORY}" archive "${EXPECTED_COMMIT}" | tar -x -C "${EXEC_ROOT}"
TEMP_ROOT=$(mktemp -d "${REPOSITORY}/results/.c5-training-analysis.XXXXXX")
TEMP_OUTPUT="${TEMP_ROOT}/result.json"
TEMP_LOG="${TEMP_ROOT}/analysis.log"
cleanup() {
  rm -rf -- "${EXEC_ROOT}" "${TEMP_ROOT}"
}
trap cleanup EXIT

export PYTHONPATH="${EXEC_ROOT}:${BUNDLE_ROOT}/verifier/DeepSeek-Prover-V1.5"
export PYTHONDONTWRITEBYTECODE=1
{
  date --iso-8601=seconds
  echo "slurm_job_id=${SLURM_JOB_ID}"
  echo "analysis_commit=${EXPECTED_COMMIT}"
  "${VENV}/bin/python" "${EXEC_ROOT}/scripts/project/analyze_c5_training.py" \
    --c0-archive "${C0_ARCHIVE}" \
    --c3-run "${C3_RUN}" \
    --c5-run "${C5_RUN}" \
    --output "${TEMP_OUTPUT}"
  "${VENV}/bin/python" - "${TEMP_OUTPUT}" <<'PY'
import json
import sys
from pathlib import Path

result = json.loads(Path(sys.argv[1]).read_text())
assert result["analysis"] == "c5-versus-c3-full-training-v1"
assert result["sources"]["c5"]["classification"] == "exploratory_full_seed42_h100"
assert result["sources"]["c3"]["classification"] == "registered_full_seed42"
assert result["archived_dominant_mode_concentration"]["eligible_theorems"] == 1_014
print(json.dumps({
    "classification": result["frozen_decision_rule"]["classification"],
    "c3": result["overall"]["c3"],
    "c5": result["overall"]["c5"],
    "rarefied_16": result["paired_correct_draw_rarefaction"].get("16"),
    "dominant_share": result["archived_dominant_mode_concentration"]["paired_common_solved"],
}, sort_keys=True))
PY
  sha256sum "${TEMP_OUTPUT}"
} 2>&1 | tee "${TEMP_LOG}"

mv "${TEMP_OUTPUT}" "${OUTPUT}"
mv "${TEMP_LOG}" "${LOG}"

echo "The frozen C5-versus-C3 training analysis completed."
