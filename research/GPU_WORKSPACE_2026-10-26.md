# October 26 persistent GPU research workspace

The user explicitly requested a `def-zhijing` Slurm allocation retained by a
Python infinite-sleep process so experiments can be launched manually over SSH.
This workspace is infrastructure for the newly authorized research program;
it starts no scientific experiment automatically. Each experiment still needs
a recorded hypothesis, inputs, comparison, budget, and stopping rule.

## Submission and status

- Job: `1176227`, name `rrl-research-workspace`.
- Submitted October 26, 2026 at 20:06:46 America/Toronto (October 27 00:06:46 UTC).
- Account: `def-zhijing`; association verified using `sacctmgr show assoc`.
- Partition: `compute_full_node`; one node, four H100 GPUs, 96 CPUs,
  770000M scheduler-assigned node memory, 24-hour wall-clock limit.
- Initial state: PENDING, reason Priority, zero runtime, no start estimate.
- At October 26 20:08 EDT, the scheduler estimated October 27 01:41:02 EDT
  as the start time. This is a mutable scheduling estimate, not an allocation
  or a guarantee. SSH validation remains pending until a node is assigned.
- No existing user jobs were present; no other allocation was modified.
- Source HEAD at submission: `98edb9beefaca57b22e219fed1daec306a3ad733`.
- Batch stdout: `/scratch/memoozd/rrl/slurm-rrl-research-workspace-1176227.out`.
- Allocation artifacts, once started:
  `/scratch/memoozd/rrl/restriction-rl/runs/research-workspace-20261026-1176227`.

Exact submission from the repository root:

```bash
sbatch --parsable --export=ALL,RRL_KEEPER_SHA256=6089e6bac6ca49e20a992e5664d1b2778178b16dedac586b6d2d53fb3b0da9df cluster/workspaces/research_workspace_20261026.sbatch
```

Slurm warned that requesting its maximum wall time can delay scheduling.
The 24-hour request matches the explicitly requested persistent workspace;
it does not establish a predicted wait or experiment duration.

## Implementation and checks

`cluster/workspaces/persistent_gpu_workspace.py` uses an interruptible Python
wait loop until SIGTERM, SIGINT, SIGHUP, or Slurm termination. Every minute it
atomically updates resource information in `heartbeat.json`; startup and
shutdown events are appended to `events.jsonl`. It checks that it is inside a
`def-zhijing` allocation. The batch script records the node, GPU model, cgroup,
source commit and dirty status, and copies both scripts into the run directory.
The keeper SHA-256 is pinned at submission and rechecked before execution.

SHA-256 values at submission:

| File | SHA-256 |
| --- | --- |
| `cluster/workspaces/persistent_gpu_workspace.py` | `6089e6bac6ca49e20a992e5664d1b2778178b16dedac586b6d2d53fb3b0da9df` |
| `cluster/workspaces/research_workspace_20261026.sbatch` | `4155f09ff777b572331e72edfa972b7f14e86612146186eee76ddfed878189fc` |

Shell syntax and Python AST parsing passed. Project preflight passed using:

```bash
RESTRICTION_VENV=/scratch/memoozd/rrl/restriction-rl/environment/venv \
ELAN_HOME=/scratch/memoozd/rrl/restriction-rl/lean/elan \
DEEPSEEK_PROVER_ROOT=/scratch/memoozd/rrl/restriction-rl/verifier/DeepSeek-Prover-V1.5 \
bash scripts/project/preflight.sh
```

Preflight is repeated on the allocated node and saved to `preflight.log`.
The workspace is retained if that preflight fails so its environment can be
inspected; scientific work must wait for the failure to be resolved. The prior
snapshot of the complete historical experiment is not automatically resumed.

## Access and boundaries

Use `squeue -j 1176227` or `scontrol show job 1176227` to find the allocated node.
SSH access and cgroup placement must be checked after the allocation starts;
neither is established while it is pending. Use only that assigned node within
the live allocation. Manually launched processes remain subject to Slurm's
24-hour limit and cancellation, and must save durable outputs to the shared run
directory. An infinite-sleep keeper does not provide checkpoint recovery.

The keeper imposes negligible CPU load, reserves the requested GPUs, and does
not launch training, alter model weights, or change verifier behavior. Release
the allocation when the authorized experiments no longer need it. No automatic
renewal or duplicate allocation has been configured.
