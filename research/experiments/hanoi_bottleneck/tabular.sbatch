#!/bin/bash
#SBATCH --account=def-zhijing
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=00:20:00
set -euo pipefail
module load scipy-stack/2026a
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
python3 tabular.py --out tabular_results.json --workers 80
