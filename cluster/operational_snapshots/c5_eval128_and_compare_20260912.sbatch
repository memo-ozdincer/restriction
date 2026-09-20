#!/usr/bin/env bash
#SBATCH --job-name=eval128-c5-c2-compare
#SBATCH --account=def-zhijing
#SBATCH --partition=compute_full_node
#SBATCH --nodes=1
#SBATCH --gpus-per-node=h100:4
#SBATCH --cpus-per-task=96
#SBATCH --time=23:00:00
#SBATCH --output=/scratch/memoozd/rrl/slurm-%x-%j.out

set -euo pipefail
runner=/scratch/memoozd/rrl/run_eval128_c5_and_compare_20260912.sh
expected_sha256=89e63ea01781df08c00f569fa570896a354d15040c2fe1c739bffd6caac5987f
actual_sha256=$(sha256sum "${runner}" | cut -d' ' -f1)
if [[ "${actual_sha256}" != "${expected_sha256}" ]]; then
  echo "C5 evaluation runner changed after registration." >&2
  exit 2
fi
exec prlimit --core=0:0 bash "${runner}"
