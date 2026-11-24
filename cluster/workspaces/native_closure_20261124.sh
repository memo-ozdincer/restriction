#!/usr/bin/env bash
set -euo pipefail
bundle=/scratch/memoozd/rrl/restriction-rl
repo="$bundle/repository"
job=${1:?job id}
out="$bundle/runs/native-closure-20261124-$job"
[[ $(cat /proc/self/cgroup) == *"job_$job/"* || $(cat /proc/self/cgroup) == *"job_$job" ]]
mkdir "$out"
trap 'scancel "$job"' EXIT
git -C "$repo" rev-parse HEAD > "$out/commit"
git -C "$repo" status --porcelain > "$out/git-status"
scontrol show job "$job" > "$out/allocation.txt"
nvidia-smi -L > "$out/gpus.txt"
git -C "$repo" archive "$(cat "$out/commit")" scripts/project > "$out/source.tar"
mkdir "$out/source"
tar -xf "$out/source.tar" -C "$out/source"
export ELAN_HOME="$bundle/lean/elan" PYTHONPATH="$bundle/environment/overlays/peft-0.10.0:$repo" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
export CUDA_VISIBLE_DEVICES=$( "$bundle/environment/venv/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["CUDA_VISIBLE_DEVICES"])' "$bundle/runs/interface-discovery-workspace-20261118-$job/allocation.json")
"$bundle/environment/venv/bin/python" - "$bundle" "$out" <<'WARM'
import hashlib,json,sys
from pathlib import Path
b,out=map(Path,sys.argv[1:])
sys.path.insert(0,str(b/'verifier/DeepSeek-Prover-V1.5'))
from prover.lean.verifier import verify_lean4_file
v=verify_lean4_file('import Mathlib\nimport Aesop\nopen BigOperators\ntheorem warm (x : Int) : x+0=x := by ring',lake_path=str(b/'lean/elan/bin/lake'),lean_workspace=str(b/'verifier/DeepSeek-Prover-V1.5/mathlib4'),timeout=300)
(out/'warmup.json').write_text(json.dumps(v));assert v.get('complete')
identity={}
for p in sorted((b/'models/c1-final').iterdir()):
 if p.suffix in ['.json','.safetensors']:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
  identity[p.name]=dict(bytes=p.stat().st_size,sha256=h.hexdigest())
(out/'parent-model-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
WARM
driver="$out/source/scripts/project/train_native_closure.py"
"$bundle/environment/venv/bin/python" -u "$driver" prepare "$bundle" "$out/experiment" > "$out/prepare.log" 2>&1
for arm in base hindsight executable transport legacy_executable legacy_transport; do
  "$bundle/environment/venv/bin/python" -u "$driver" run "$bundle" "$out/experiment" --arm "$arm" > "$out/$arm.log" 2>&1
done
"$bundle/environment/venv/bin/python" -u "$driver" verify "$bundle" "$out/experiment" > "$out/verify.log" 2>&1
"$bundle/environment/venv/bin/python" -u "$out/source/scripts/project/audit_native_closure.py" "$bundle" "$out/experiment" > "$out/audit.log" 2>&1
