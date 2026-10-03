#!/usr/bin/env bash
# Persistent, monitored full-node workspace for the bounded C5 feasibility gate.
# Scientific runs must be launched separately with srun --jobid JOB_ID.
#SBATCH --job-name=rrl-c5-workspace
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
RUN="${BUNDLE}/runs/c5-workspace-20261002-${SLURM_JOB_ID}"
if [[ -e "${RUN}" ]]; then
  echo "Refusing to reuse workspace: ${RUN}" >&2
  exit 2
fi
mkdir -p "${RUN}"
{
  echo "purpose=bounded_c5_actor_loaded_feasibility"
  echo "job_id=${SLURM_JOB_ID}"
  echo "account=${SLURM_JOB_ACCOUNT}"
  echo "node=$(hostname)"
  echo "started=$(date --iso-8601=seconds)"
  echo "submission_sha256=$(sha256sum "$0" | cut -d' ' -f1)"
  echo "source_commit=$(git -C "${BUNDLE}/repository" rev-parse HEAD)"
  echo "scientific_run_started=false"
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} > "${RUN}/allocation.txt"

printf 'timestamp\tmem_available_kib\tmem_used_kib\tgpus_index_used_mib_util_pct\n' > "${RUN}/heartbeat.tsv"
monitor() {
  while true; do
    timestamp=$(date --iso-8601=seconds)
    available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
    total=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
    used=$((total - available))
    gpu_state=$(nvidia-smi --query-gpu=index,memory.used,utilization.gpu \
      --format=csv,noheader,nounits | tr -d ' ' | paste -sd ';' -)
    printf '%s\t%s\t%s\t%s\n' "$timestamp" "$available" "$used" "$gpu_state" \
      >> "${RUN}/heartbeat.tsv"
    printf 'job_id=%s\nnode=%s\nlast_sample=%s\nmem_available_kib=%s\ngpus=%s\n' \
      "${SLURM_JOB_ID}" "$(hostname)" "$timestamp" "$available" "$gpu_state" \
      > "${RUN}/heartbeat.tmp"
    mv -f "${RUN}/heartbeat.tmp" "${RUN}/heartbeat.txt"
    sleep 30
  done
}
monitor &
monitor_pid=$!
sleep infinity &
sleep_pid=$!
cleanup() {
  kill "$monitor_pid" "$sleep_pid" 2>/dev/null || true
  wait "$monitor_pid" "$sleep_pid" 2>/dev/null || true
  echo "ended=$(date --iso-8601=seconds)" >> "${RUN}/allocation.txt"
}
trap cleanup EXIT
wait "$sleep_pid"
