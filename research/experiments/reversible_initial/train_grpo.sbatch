#!/bin/bash
#SBATCH --job-name=rrl-circuit-grpo
#SBATCH --array=0-1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=48:00:00
set -euo pipefail
cd /h/405/memo/rrl-phc
runtime=/mfs1/u/memo/rcc-research/envs/rcc-managed312/bin/python
model=/mfs1/u/memo/rcc-research/cache/huggingface/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots/cdbee75f17c01a7cc42f958dc650907174af0554
case "${SLURM_ARRAY_TASK_ID:?}" in
  0) arm=identity ;;
  1) arm=exploratory ;;
  *) exit 2 ;;
esac
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
out=/mfs1/u/memo/rrl-phc/runs/grpo-${arm}-${SLURM_JOB_ID:?}
mkdir -p "$(dirname "$out")"
exec "$runtime" research/experiments/reversible_initial/train_grpo.py --arm "$arm" --model "$model" --out "$out"
