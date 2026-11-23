#!/usr/bin/env bash
set -euo pipefail
bundle=/scratch/memoozd/rrl/restriction-rl
repo="$bundle/repository"
job=${1:?job id}
out="$bundle/runs/recursive-grpo-20261123-$job"
[[ $(cat /proc/self/cgroup) == *"job_$job/"* || $(cat /proc/self/cgroup) == *"job_$job" ]]
mkdir "$out"
trap 'scancel "$job"' EXIT
git -C "$repo" rev-parse HEAD > "$out/commit"
git -C "$repo" status --porcelain > "$out/git-status"
scontrol show job "$job" > "$out/allocation.txt"
nvidia-smi -L > "$out/gpus.txt"
export ELAN_HOME="$bundle/lean/elan" PYTHONPATH="$bundle/environment/overlays/peft-0.10.0:$repo" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
panel="$repo/research/experiments/recursive_blocking_20261123/panel.json"
sha256sum "$panel" > "$out/panel.sha256"
for arm in discovery control recursive; do
  "$bundle/environment/venv/bin/python" -u "$repo/scripts/project/run_recursive_grpo.py" "$bundle" "$panel" "$out" "$arm" > "$out/$arm.log" 2>&1
done
