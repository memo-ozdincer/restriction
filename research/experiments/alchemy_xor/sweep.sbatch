#!/bin/bash -l
#SBATCH --job-name=alchemy-xor
#SBATCH --account=def-zhijing
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=00:30:00
set -euo pipefail
hostname
date --iso-8601=seconds
g++ --version | head -1
sha256sum run.cpp sweep.sbatch README.md
g++ -std=c++17 -O3 -march=native run.cpp -o run
mkdir results
for seed in 42 43 44 45; do ./run "$seed" results > "results/seed-$seed.log" 2>&1 & done
fail=0
for pid in $(jobs -p); do wait "$pid" || fail=1; done
[ "$fail" = 0 ]
sha256sum results/* > checksums.txt
