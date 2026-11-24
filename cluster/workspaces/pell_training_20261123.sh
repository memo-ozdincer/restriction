#!/usr/bin/env bash
set -euo pipefail
bundle=/scratch/memoozd/rrl/restriction-rl
repo="$bundle/repository"
job=${1:?job id}
out="$bundle/runs/pell-training-20261123-$job"
[[ $(cat /proc/self/cgroup) == *"job_$job/"* || $(cat /proc/self/cgroup) == *"job_$job" ]]
mkdir "$out"
trap 'scancel "$job"' EXIT
git -C "$repo" rev-parse HEAD > "$out/commit"
git -C "$repo" status --porcelain > "$out/git-status"
scontrol show job "$job" > "$out/allocation.txt"
nvidia-smi -L > "$out/gpus.txt"
export ELAN_HOME="$bundle/lean/elan" PYTHONPATH="$bundle/environment/overlays/peft-0.10.0:$repo" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
export CUDA_VISIBLE_DEVICES=$( "$bundle/environment/venv/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["CUDA_VISIBLE_DEVICES"])' "$bundle/runs/interface-discovery-workspace-20261118-$job/allocation.json")
"$bundle/environment/venv/bin/python" - "$bundle" "$out" <<'WARM'
import json, sys
from pathlib import Path
bundle, out = map(Path, sys.argv[1:])
verifier = bundle/'verifier/DeepSeek-Prover-V1.5'
sys.path.insert(0,str(verifier))
from prover.lean.verifier import verify_lean4_file
result = verify_lean4_file('import Mathlib\nimport Aesop\ntheorem warm : True := by trivial', lake_path=str(bundle/'lean/elan/bin/lake'), lean_workspace=str(verifier/'mathlib4'), timeout=300)
(out/'warmup.json').write_text(json.dumps(result))
assert result.get('complete')
WARM
driver="$repo/scripts/project/train_pell_construction.py"
"$bundle/environment/venv/bin/python" -u "$driver" prepare "$bundle" "$out" > "$out/prepare.log" 2>&1
for arm in base literal expression; do
  "$bundle/environment/venv/bin/python" -u "$driver" run "$bundle" "$out" --arm "$arm" > "$out/$arm.log" 2>&1
done
"$bundle/environment/venv/bin/python" -u "$driver" verify "$bundle" "$out" > "$out/verify.log" 2>&1
