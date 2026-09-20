#!/usr/bin/env bash
#SBATCH --job-name=c5-reject-retry7
#SBATCH --account=rrg-zhijing
#SBATCH --partition=compute_full_node
#SBATCH --nodes=1
#SBATCH --gpus-per-node=h100:4
#SBATCH --cpus-per-task=96
#SBATCH --time=24:00:00
#SBATCH --exclude=trig0011,trig0031,trig0033,trig0048,trig0058
#SBATCH --output=/scratch/memoozd/rrl/slurm-%x-%j.out

set -euo pipefail
expected_runner_sha256=317be131c461f698c29915856b0aa4e4556868678f8fc8de019e39a25362d990
runner=/scratch/memoozd/rrl/run_c5_reward_reject_full_h100_retry7_24h_317be131.sh
actual_runner_sha256=$(sha256sum "${runner}" | cut -d' ' -f1)
if [[ "${actual_runner_sha256}" != "${expected_runner_sha256}" ]]; then
  echo "C5 retry-7 runner changed after registration." >&2
  exit 2
fi
exec bash "${runner}"
