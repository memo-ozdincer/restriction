#!/bin/bash -l
#SBATCH --job-name=alchemy-racetrack
#SBATCH --account=def-zhijing
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=00:20:00
set -euo pipefail
module load scipy-stack/2026a
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
hostname
date --iso-8601=seconds
sha256sum run.py sweep.sbatch
python run.py --workers 4 --out results.json
