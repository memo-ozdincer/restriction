#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
bundle=/scratch/memoozd/rrl/restriction-rl
repo="$bundle/repository"
job=${1:?job id}
[[ $(cat /proc/self/cgroup) == *"job_$job/"* || $(cat /proc/self/cgroup) == *"job_$job" ]]
trap 'scancel "$job"' EXIT
run="$bundle/runs/failed-experience-join-20261124"
launch="$bundle/runs/failed-experience-join-launch-20261124-$job"
mkdir "$launch"
git -C "$repo" rev-parse HEAD > "$launch/commit"
git -C "$repo" status --porcelain > "$launch/git-status"
scontrol show job "$job" > "$launch/allocation.txt"
hostname > "$launch/node"
git -C "$repo" archive "$(cat "$launch/commit")" scripts/project > "$launch/source.tar"
mkdir "$launch/source"
tar -xf "$launch/source.tar" -C "$launch/source"
export ELAN_HOME="$bundle/lean/elan" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
python="$bundle/environment/venv/bin/python"
"$python" -u "$launch/source/scripts/project/failed_experience_join.py" execute "$bundle" "$run" > "$launch/execute.log" 2>&1
"$python" -u "$launch/source/scripts/project/audit_failed_experience_join.py" "$run" > "$launch/audit.log" 2>&1
