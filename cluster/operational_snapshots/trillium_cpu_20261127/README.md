# Trillium CPU smoke — 2026-11-27 session

An independent cluster access check used the existing SSH multiplex alias `trillium-cpu` and submitted a single tiny software smoke test. No pre-existing jobs or project files were changed. The scheduler timestamps are 2026-11-26 (remote clock), whereas the smoke directory was named for the research session date.

## Verified access and resources

- `ssh -o BatchMode=yes trillium-cpu` reaches `tri-login06` as `memoozd`. Use a login shell (`bash -lc` or `bash -l -s`) to expose the Slurm commands and modules; a non-login remote shell does not have them on its PATH.
- `sacctmgr` shows `def-zhijing` with normal QOS. `rrg-zhijing` is *not* among the current associations, so no fallback submission was attempted.
- Standard CPU `compute` partition (1,230 nodes, 24-hour max) and `debug` (1,234 nodes, one-hour max) advertise 192 CPUs and 767,000 MB per node. Availability and queue lengths are dynamic.
- On the actual smoke node `tri0854`, `lscpu` reports two AMD EPYC 9655 sockets, 96 physical cores per socket, 192 CPUs total, one thread per core.
- The cluster's `sbatch` wrapper rejected an explicit `--mem=4G` request, without submitting a job. Retrying with the memory directive omitted succeeded. The 2-CPU smoke request was nevertheless allocated/billed a full 192-CPU, 767,000-MB node, as reported by Slurm. Independent experiment sweeps should use the allocated cores efficiently instead of submitting many tiny whole-node jobs.
- `module load scipy-stack/2026a` supplies Python 3.11.5, NumPy 2.4.2 and SciPy. The smoke verified a small NumPy/SciPy linear solve (`CPU_SMOKE_OK`).

## Authoritative scheduler result

Job `2938787`, account `def-zhijing`, `debug`, node `tri0854`, `COMPLETED`, exit `0:0`, elapsed 5 seconds. Submitted 12:45:04, began 12:45:05, finished 12:45:10 on the remote scheduler clock. No running job was cancelled or modified.

## Source provenance

| Source path on Trillium | SHA-256 |
|---|---|
| `/scratch/memoozd/rrl/cpu-smoke-20261127/smoke.sbatch` | `98465a9a7ab2e1bba1c81c45a24f213233617c5f67924558a6e6c7c3aebd9d44` |
| `/scratch/memoozd/rrl/cpu-smoke-20261127/2938787.log` | `c94416393e67e558890e2342ad3ce96bd2ab5da5d5f6f681e205dd6894e49bb3` |

Local `smoke.sbatch` is byte-identical to the remote source. `scheduler_evidence.txt` contains a fresh directly captured account/partition listing, `sacct` result, remote file hashes, and selected CPU/software/checker lines from the raw log. The complete raw log remains at its remote path. No SSH credentials, environment dump, or unrelated job data are included.

## Reproduction

Check the existing completed job and account association without launching anything:

```bash
ssh -o BatchMode=yes trillium-cpu 'bash -lc '\''sacctmgr -nP show assoc where user=$USER format=Account,Partition,QOS; sacct -j 2938787 -nP -o JobID,Account,Partition,State,Submit,Start,End,Elapsed,AllocCPUS,NodeList,ExitCode'\'''
```

If another software smoke becomes necessary, the exact successful script remains on scratch. Its submission command (inside the Trillium login shell) was:

```bash
smoke_dir=/scratch/memoozd/rrl/cpu-smoke-20261127
sbatch --parsable --chdir="$smoke_dir" --output="$smoke_dir/%j.log" "$smoke_dir/smoke.sbatch"
```

For future authorized CPU sweeps, request `--account=def-zhijing --partition=compute --nodes=1 --ntasks=1 --cpus-per-task=192` and an experiment-appropriate wall time (up to 24 hours); omit `--mem`. Load `scipy-stack/2026a`. For independent Python worker processes, set `OMP_NUM_THREADS=1` and `OPENBLAS_NUM_THREADS=1` to avoid oversubscription. Choose worker count from the actual scheduler allocation and per-worker memory cost. The existing scratch project root is `/scratch/memoozd/rrl`; the isolated smoke directory is separate from `/scratch/memoozd/rrl/restriction-rl`. No production experiment was submitted as part of this check.
