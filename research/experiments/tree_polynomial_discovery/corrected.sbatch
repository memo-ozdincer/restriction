#!/bin/bash -l
#SBATCH --job-name=tree-poly-pg-guard
#SBATCH --account=def-zhijing
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=00:15:00
set -euo pipefail
module load scipy-stack/2026a
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
hostname
date --iso-8601=seconds
python -c 'import sys,numpy; print(sys.version); print(numpy.__version__)'
sha256sum -c CORRECTED_SHA256SUMS
python -m unittest -q test_environment test_train
python corrected_panel.py
date --iso-8601=seconds
