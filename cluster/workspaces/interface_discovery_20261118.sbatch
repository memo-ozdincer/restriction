#!/usr/bin/env bash
# One bounded, manually driven inference experiment; this job only holds resources.
#SBATCH --job-name=rrl-interface-discovery
#SBATCH --account=def-zhijing
#SBATCH --partition=compute_h200
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --time=01:00:00
#SBATCH --output=/scratch/memoozd/rrl/slurm-%x-%j.out
set -euo pipefail
ulimit -c 0
BUNDLE=/scratch/memoozd/rrl/restriction-rl
REPO="$BUNDLE/repository"
RUN="$BUNDLE/runs/interface-discovery-workspace-20261118-$SLURM_JOB_ID"
mkdir "$RUN"
cp "$REPO/cluster/workspaces/persistent_gpu_workspace.py" "$RUN/keeper.py"
cp "$REPO/scripts/project/interface_discovery_pilot.py" "$RUN/pilot.py"
cp "$REPO/scripts/project/run_interface_discovery.py" "$RUN/driver.py"
export RRL_INTERFACE_RUN="$RUN"
"$BUNDLE/environment/venv/bin/python" - <<'PY'
import json, os, socket, subprocess
from pathlib import Path
run = Path(os.environ['RRL_INTERFACE_RUN'])
data = {k:os.environ.get(k) for k in ['SLURM_JOB_ID','SLURM_JOB_ACCOUNT','SLURM_JOB_GPUS','CUDA_VISIBLE_DEVICES']}
data['node'] = socket.gethostname()
data['source_commit'] = subprocess.check_output(['git','-C','/scratch/memoozd/rrl/restriction-rl/repository','rev-parse','HEAD'], text=True).strip()
data['gpu'] = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name,memory.total','--format=csv,noheader'],text=True)
data['cgroup'] = Path('/proc/self/cgroup').read_text()
(run/'allocation.json').write_text(json.dumps(data,indent=2)+'\n')
PY
exec "$BUNDLE/environment/venv/bin/python" -u "$RUN/keeper.py" --run-dir "$RUN"
