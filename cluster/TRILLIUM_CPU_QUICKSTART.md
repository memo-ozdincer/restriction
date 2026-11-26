# Trillium CPU experiment quickstart

For agents running the repository's small-policy, NumPy/SciPy or discrete-search experiments. Start here; no new SSH key, MFA setup, or GPU allocation is needed while the existing multiplex is live.

## 1. Check the live cluster and account

From the local terminal:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 trillium-cpu 'bash -l -s' <<'REMOTE'
hostname
whoami
sacctmgr -nP show assoc where user=$USER format=Account,Partition,QOS
sinfo -o '%P %D %C %m %l'
squeue -u "$USER" -o '%i %a %j %T %M %l %R'
REMOTE
```

- The alias reaches Trillium CPU as `memoozd`. **Use `bash -lc` or `bash -l -s`**: the non-login SSH command shell lacks Slurm commands/modules.
- Prefer **`def-zhijing`**. The last verified association included `def-zhijing` but **not** `rrg-zhijing`. Only use `rrg-zhijing` if a fresh association check confirms it and the user has authorized the fallback. Do not cancel/restart existing work merely to change accounts.
- Standard CPU nodes have **192 physical cores** (dual AMD EPYC 9655, no SMT), advertised memory **767,000 MB**, and no GPU. Slurm allocates/bills a whole node even for a 2-CPU request. Use one full node to parallelize independent runs; do not submit dozens of tiny whole-node jobs.
- `debug` has a one-hour walltime limit; use it for appropriately short, permissible exploratory runs. `compute` has a 24-hour limit for longer sweeps. Queue availability changes, so inspect live state rather than relying on old queue counts. **Omit `--mem`**; the site wrapper rejects it.
- `module load scipy-stack/2026a` is verified: Python 3.11.5, NumPy 2.4.2 and SciPy. No environment install needed for NumPy/SciPy-only experiments.

If SSH fails, report the concrete access/configuration problem. Do not attempt alternate hosts or accounts without authorization.

## 2. Register the experiment and stage an isolated snapshot

Before submitting compute, record the hypothesis, discriminating comparison and decision it will inform. Preserve the controlled baseline, paired seeds, exact verifier, intervention timing and compute accounting. Check for existing jobs/results and avoid duplicate submissions. Use a **new unique experiment directory** under `/scratch/memoozd/rrl/`; never overwrite existing `restriction-rl` or other runs.

Example from the local repository root; replace the local and remote paths and explicit input filenames with the actual experiment. This example is deliberately a template, not a command to rerun an already finished experiment.

```bash
experiment_dir=research/experiments/my_new_experiment
remote_dir=/scratch/memoozd/rrl/my-new-experiment-20261127
# Fail if this run directory already exists; choose a unique name deliberately.
ssh -o BatchMode=yes trillium-cpu "mkdir '$remote_dir'"
scp -q "$experiment_dir/run.py" "$experiment_dir/README.md" \
  "$experiment_dir/sweep.sbatch" trillium-cpu:"$remote_dir/"
# Include every needed input/dependency as an explicit scp source.
shasum -a 256 "$experiment_dir/run.py" "$experiment_dir/README.md" \
  "$experiment_dir/sweep.sbatch"
ssh -o BatchMode=yes trillium-cpu \
  "cd '$remote_dir' && sha256sum run.py README.md sweep.sbatch"
```

Compare basename digests locally and remotely before submission. Do not rsync the entire repository or credentials/caches. Keep versioned snapshots of scripts, source paths/checksums, repo commit and dirty status; pin model/data revisions when applicable.

## 3. Batch script and submission

Typical single full-node CPU sweep (`sweep.sbatch`):

```bash
#!/bin/bash -l
#SBATCH --job-name=my-sweep
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
hostname
date --iso-8601=seconds
python -c 'import sys,numpy; print(sys.version); print(numpy.__version__)'
sha256sum run.py sweep.sbatch
# The runner must implement --workers; adjust to its actual CLI and workload.
python run.py --workers 96 --out results
```

Choose the number of independent processes to fit the actual number of trials and memory usage, never exceeding allocated CPUs. A Python `ProcessPoolExecutor` works for independent trajectories. For a long single-threaded workload, parallelize genuinely independent modes/seeds/task instances rather than adding threads it cannot use. Keep all numerical-library thread limits at one for multiprocessing. Do not use login-node CPUs for bulk experiments.

Check syntax, current jobs and destination status before the one submission:

```bash
bash -n "$experiment_dir/sweep.sbatch"
ssh -o BatchMode=yes trillium-cpu 'bash -lc '\''squeue -u "$USER" -o "%i %a %j %T %M %R"'\'''
# Submit exactly once and immediately record the returned job ID.
ssh -o BatchMode=yes trillium-cpu \
  "bash -lc 'cd \"$remote_dir\" && sbatch --parsable --chdir=\"\$PWD\" --output=\"\$PWD/%j.log\" sweep.sbatch'"
```

If the SSH/submission observation times out, **check `squeue`/`sacct` for the existing job and its name/work directory before retrying**. Do not blindly submit again. Record the actual account, job ID and remote path in the experiment notes and push reviewed code/config at the meaningful milestone if authorized by the project instructions.

## 4. Monitor, retrieve, and verify

Substitute the recorded job ID and directory in these commands:

```bash
job_id=2938787  # example existing completed smoke job
ssh -o BatchMode=yes trillium-cpu \
  "bash -lc 'squeue -j $job_id -o \"%i %a %T %M %R\"; sacct -j $job_id -nP -o JobID,Account,Partition,State,Submit,Start,End,Elapsed,AllocCPUS,NodeList,ExitCode'"
```

Use `tail` on the job's `%j.log` in the remote run directory for live progress, and poll the **same** job until `sacct` confirms completion. Queue disappearance alone does not prove success. Do not modify other jobs. If a particular job fails, diagnose the actual failure and inspect all per-run artifacts; avoid unnecessary retraining when results can be recovered.

Retrieve explicit outputs into a dedicated local experimental directory, preserving source and result hashes:

```bash
# Replace values with the real recorded run path and ID.
ssh -o BatchMode=yes trillium-cpu "sha256sum '$remote_dir/results/results.json' '$remote_dir/$job_id.log'"
scp -q trillium-cpu:"$remote_dir/results/results.json" "$experiment_dir/results.json"
scp -q trillium-cpu:"$remote_dir/$job_id.log" "$experiment_dir/$job_id.log"
shasum -a 256 "$experiment_dir/results.json" "$experiment_dir/$job_id.log"
```

For a failed final aggregation with complete per-run rows, recover those rows and aggregate offline. Independently verify outcomes (exact checker, saved policy replay, full counters) before claiming completion. Record resolved config, seeds, runtime, actual allocation, candidate/action budgets, queue outcome, source/result hashes, and any reproduction discrepancies in the project documentation. Avoid sharing bulk data/checkpoints or raw credentials; leave excluded artifacts with location/provenance records. Review staged paths and scan for secrets before committing/pushing.

## 5. Verified examples and numerical-reproduction lesson

- **Smoke job `2938787`**: `def-zhijing`, `debug`, node `tri0854`, 192 allocated CPUs despite a 2-CPU request, scheduler `COMPLETED`, exit `0:0`, 1-second queue and 5-second elapsed. NumPy/SciPy linear solve succeeded. [Exact successful smoke script](operational_snapshots/trillium_cpu_20261127/smoke.sbatch), [scheduler evidence](operational_snapshots/trillium_cpu_20261127/scheduler_evidence.txt), [full smoke notes](operational_snapshots/trillium_cpu_20261127/README.md).
- **Long subset-sum job `2938839`**: one 192-core node, 72 one-thread workers, 60,000 updates each, 1,105,920,000 candidate proposals. All 72 trajectories finished in 11 seconds elapsed, but the scheduler marked the aggregation failed because Apple Silicon and AMD float64 logits differed by at most `2.8588e-15`. All integer checkpoint records matched; offline recovery preserved the original outputs and independently audited all 72 final policies, without another training run. Follow documented decision D-169 for this experiment; do not silently relax unrelated reproduction checks. [Submitted runner](../research/experiments/subset_long_trillium/train_long.py), [batch script](../research/experiments/subset_long_trillium/sweep.sbatch), [job evidence](../research/experiments/subset_long_trillium/scheduler_evidence.txt), [plan, outcomes and recovery](../research/experiments/subset_long_trillium/README.md), [decision log](../research/DECISIONS.md).
- The original cluster-side sources and outputs remain under `/scratch/memoozd/rrl/cpu-smoke-20261127/` and `/scratch/memoozd/rrl/subset-long-trillium-20261127/`. These are historical evidence; do not resubmit them just for a repeat smoke.
