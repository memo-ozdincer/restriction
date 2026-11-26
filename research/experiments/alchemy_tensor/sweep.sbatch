#!/bin/bash -l
#SBATCH --job-name=alchemy-tensor
#SBATCH --account=def-zhijing
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=00:15:00
set -euo pipefail
module load scipy-stack/2026a
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
hostname
date --iso-8601=seconds
python -c 'import sys,numpy; print(sys.version, numpy.__version__)'
sha256sum train.py native_environment.py sweep.sbatch README.md
python train.py --out results.json --workers 4
