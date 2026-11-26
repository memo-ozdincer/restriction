#!/bin/bash -l
#SBATCH --job-name=hanoi-horizon
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
python -c 'import sys,numpy,scipy; print(sys.version,numpy.__version__,scipy.__version__)'
sha256sum hanoi_horizon/run.py hanoi_horizon/sweep.sbatch hanoi_mechanism/analyze.py hanoi_bottleneck/{run,tabular,audit}.py
python hanoi_horizon/run.py --workers 48 --out results.json
