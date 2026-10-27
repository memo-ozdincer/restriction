#!/usr/bin/env bash
# Persistent research workspace; scientific experiments are launched separately.
#SBATCH --job-name=rrl-research-workspace
#SBATCH --account=def-zhijing
#SBATCH --partition=compute_full_node
#SBATCH --nodes=1
#SBATCH --gpus-per-node=h100:4
#SBATCH --cpus-per-task=96
#SBATCH --time=24:00:00
#SBATCH --output=/scratch/memoozd/rrl/slurm-%x-%j.out

set -euo pipefail
ulimit -c 0

BUNDLE=/scratch/memoozd/rrl/restriction-rl
REPO="${BUNDLE}/repository"
RUN="${BUNDLE}/runs/research-workspace-20261026-${SLURM_JOB_ID}"
KEEPER="${REPO}/cluster/workspaces/persistent_gpu_workspace.py"
if [[ "${SLURM_JOB_ACCOUNT:-}" != def-zhijing || -e "${RUN}" ]]; then
  echo "Expected a new def-zhijing workspace." >&2
  exit 2
fi
if [[ -z "${RRL_KEEPER_SHA256:-}" || "$(sha256sum "$KEEPER" | cut -d' ' -f1)" != "$RRL_KEEPER_SHA256" ]]; then
  echo "Keeper changed after submission, or submission digest is missing." >&2
  exit 2
fi
mkdir -p "${RUN}"
cp "$KEEPER" "${RUN}/persistent_gpu_workspace.py"
cp "$0" "${RUN}/submitted.sbatch"
{
  echo "purpose=manual_hypothesis_driven_research_workspace"
  echo "job_id=${SLURM_JOB_ID}"
  echo "account=${SLURM_JOB_ACCOUNT}"
  echo "node=$(hostname)"
  echo "started_utc=$(date -u --iso-8601=seconds)"
  echo "source_commit=$(git -C "$REPO" rev-parse HEAD)"
  echo "scientific_run_started=false"
  echo "automatic_experiment=none"
  sha256sum "${RUN}/persistent_gpu_workspace.py" "${RUN}/submitted.sbatch"
  git -C "$REPO" status --short
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
  cat /proc/self/cgroup
} > "${RUN}/allocation.txt"

export RESTRICTION_VENV="${BUNDLE}/environment/venv"
export ELAN_HOME="${BUNDLE}/lean/elan"
export DEEPSEEK_PROVER_ROOT="${BUNDLE}/verifier/DeepSeek-Prover-V1.5"
export PATH="${RESTRICTION_VENV}/bin:${ELAN_HOME}/bin:${PATH}"
if bash "$REPO/scripts/project/preflight.sh" > "${RUN}/preflight.log" 2>&1; then
  echo "preflight_exit=0" >> "${RUN}/allocation.txt"
else
  echo "preflight_exit=$?" >> "${RUN}/allocation.txt"
  echo "Preflight failed; workspace retained for inspection. Do not launch experiments until resolved."
fi
echo "Workspace ${SLURM_JOB_ID} ready on $(hostname); logs: ${RUN}"
exec "${RESTRICTION_VENV}/bin/python" -u "${RUN}/persistent_gpu_workspace.py" --run-dir "${RUN}"
