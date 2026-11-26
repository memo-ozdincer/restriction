#!/bin/bash -l
#SBATCH --job-name=alchemy-compress
#SBATCH --account=def-zhijing
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --cpus-per-task=192
#SBATCH --ntasks=1
#SBATCH --time=00:15:00
set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"
echo "host=$(hostname) job=$SLURM_JOB_ID"
date --iso-8601=seconds
sha256sum run.cpp README.md sweep.sbatch audit.py
g++ --version | head -1
g++ -O3 -std=c++17 -Wall -Wextra run.cpp -o run
for seed in 42 43 44 45; do
    ./run "$seed" "seed$seed" >"seed$seed.log" 2>&1 &
done
wait
for seed in 42 43 44 45; do test -s "seed$seed.json"; done
sha256sum seed*.json seed*.jsonl
