#!/bin/bash -l
#SBATCH --job-name=exposure-panel
#SBATCH --account=def-zhijing
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=00:55:00
set -uo pipefail
module load scipy-stack/2026a
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
hostname
date --iso-8601=seconds
python -c 'import sys,numpy; print(sys.version); print(numpy.__version__)'
sha256sum -c SHA256SUMS || exit 1

# Run independent domain panels concurrently, under 192 allocated CPUs.
(
  cd exposure_tsp_puzzles
  python run.py --domain both --workers 64 --out scratch-results &&
  python run.py --domain both --workers 64 --common-prefix --out common-results
) > tsp-flip.log 2>&1 &
p1=$!
(
  cd exposure_tensor_sokoban
  python train.py --domains sokoban sokoban-medium --workers 32 --out sokoban-results
) > sokoban.log 2>&1 &
p2=$!
(
  cd exposure_tensor_sokoban
  python matrix_train.py --workers 16 --out matrix-results.json
) > matrix.log 2>&1 &
p3=$!
(
  cd exposure_reversible_review
  python run.py --workers 44 --out results
) > reversible.log 2>&1 &
p4=$!
rc=0
for pid in "$p1" "$p2" "$p3" "$p4"; do
  wait "$pid" || rc=1
done
date --iso-8601=seconds
exit "$rc"
