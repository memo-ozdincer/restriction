#!/bin/bash -l
#SBATCH --job-name=rrl-cpu-smoke
#SBATCH --account=def-zhijing
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:05:00
set -euo pipefail
hostname
lscpu | sed -n '1,20p'
module load scipy-stack/2026a
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export OPENBLAS_NUM_THREADS="$SLURM_CPUS_PER_TASK"
python - <<'PYTHON'
import os, platform, sys
import numpy as np
from scipy.linalg import solve
print('PYTHON', sys.version)
print('NUMPY', np.__version__)
print('SLURM_CPUS_PER_TASK', os.environ['SLURM_CPUS_PER_TASK'])
a = np.array([[3., 1.], [1., 2.]])
b = np.array([9., 8.])
assert np.allclose(a @ solve(a,b), b)
print('CPU_SMOKE_OK')
PYTHON
