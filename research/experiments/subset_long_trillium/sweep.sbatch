#!/bin/bash -l
#SBATCH --job-name=subset-long
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
python -c 'import numpy, sys; print(sys.version); print("NUMPY",numpy.__version__)'
hostname
date --iso-8601=seconds
sha256sum source_run.py train_long.py original_results.json sweep.sbatch
python train_long.py --original-records original_results.json --out results --workers 72
sha256sum results/results.json
date --iso-8601=seconds
