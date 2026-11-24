#!/usr/bin/env bash
#SBATCH --job-name=rrl-failure-join
#SBATCH --account=def-zhijing
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/scratch/memoozd/rrl/slurm-%x-%j.out
set -euo pipefail
ulimit -c 0
bundle=/scratch/memoozd/rrl/restriction-rl
repo="$bundle/repository"
run="$bundle/runs/failed-experience-join-20261124"
launch="$bundle/runs/failed-experience-join-launch-20261124-$SLURM_JOB_ID"
mkdir "$launch"
git -C "$repo" rev-parse HEAD > "$launch/commit"
git -C "$repo" status --porcelain > "$launch/git-status"
scontrol show job "$SLURM_JOB_ID" > "$launch/allocation.txt"
hostname > "$launch/node"
git -C "$repo" archive "$(cat "$launch/commit")" scripts/project > "$launch/source.tar"
mkdir "$launch/source"
tar -xf "$launch/source.tar" -C "$launch/source"
export ELAN_HOME="$bundle/lean/elan" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
python="$bundle/environment/venv/bin/python"
"$python" -u "$launch/source/scripts/project/failed_experience_join.py" execute "$bundle" "$run" > "$launch/execute.log" 2>&1
"$python" -u "$launch/source/scripts/project/audit_failed_experience_join.py" "$run" > "$launch/audit.log" 2>&1
