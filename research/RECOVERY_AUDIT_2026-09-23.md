# Codex-session and project recovery audit

Audit date: 2026-09-23 EDT. This is a read-only reconciliation of Codex
history, Git refs, Slurm accounting, and local run artifacts, followed by
documentation-only repository updates. It does not authorize or report a new
experiment.

## Recovered Codex history

The project session that could not be resumed directly is:

- session ID: `01a086a9-6c8d-7400-a322-54110e516f44`
- recorded working directory: `/scratch/memoozd/rrl`
- transcript:
  `/scratch/memoozd/.codex/sessions/2026/09/09/rollout-2026-09-09T10-54-05-01a086a9-6c8d-7400-a322-54110e516f44.jsonl`
- size: 24,743,958 bytes and 13,853 JSONL records
- SHA-256:
  `06265991a7f0081264cee8a4da61c56316b4042563d4c3559965572c8c449720`

Every record parses as JSON. The last records are repeated verified waits for
verifier benchmark `918556`, ending at 09:36 EDT on September 21 while the job
was still pending. Direct resume failed because Codex's SQLite stores were
malformed, not because the JSONL transcript was truncated. Read-only SQLite
`quick_check` reports corruption in `thread_history_1.sqlite`, `state_5.sqlite`,
and `logs_2.sqlite`; the live stores were not modified or rebuilt during this
audit.

The recovery follow-up is session
`01a0c514-719f-7882-9c04-8dcd6dcb1a81`, stored at
`/scratch/memoozd/.codex/sessions/2026/09/21/rollout-2026-09-21T13-47-26-01a0c514-719f-7882-9c04-8dcd6dcb1a81.jsonl`.
It contains 168 records in 1,551,369 bytes, with SHA-256
`01e073262d98cf535ebd87f2f8f965cda86cbf7f299d994caf2accca10267d7f`.
It reconciled the broken transcript with Git, discovered that `918556` had
completed after the last main-session check, validated the output, and produced
commit `c785aeb5a7ba21cdc844a7b4183af3a4078b795d`.

Two nearby large sessions were checked and excluded from this project audit:
`01a086a8-4d88-7c01-9ef4-8038499e39ac` and
`01a0c073-792f-7021-b2f6-fc14a70afd69` both record the unrelated working
directory `/scratch/memoozd/rr/alice`.

The raw Codex transcripts are not committed: they contain complete prompts,
tool traces, cluster paths, and potentially sensitive operational context.
Their exact local paths and checksum above make the relevant recovery
auditable without publishing that material. The intact JSONL remains directly
readable even though normal Codex resume is unavailable.

## Git reconciliation

After `git fetch --prune origin`, the checkout is clean and both local branches
exactly match their remote tracking refs:

| Branch | Commit | Relationship |
|---|---|---|
| `dominant-mode-blocking` | `db54771281adc6325eddd0e6e8192e95d418155a` | GitHub default and preserved historical baseline |
| `work/dominant-mode-rejection` | `c785aeb5a7ba21cdc844a7b4183af3a4078b795d` | Active research branch |

The active branch is a strict 117-commit descendant of the default branch:
`git rev-list --left-right --count dominant-mode-blocking...work/dominant-mode-rejection`
returns `0 117`. Therefore no unique commit or unmerged work exists on the old
branch. The default branch was not silently advanced; publishing the active
line there is a separate branch-management decision.

## Scheduler and artifact reconciliation

At the audit, `squeue -u memoozd` is empty. Slurm accounting from September 21
onward contains only job `918556`, which completed successfully at 10:19 EDT on
September 21 with exit `0:0` and elapsed time 19m36s. That outcome is already
tracked in `research/VERIFIER_CONCURRENCY_BENCHMARK.md`, `PROJECT_STATE.md`, and
`results/verifier_workers_918556_summary.json` at commit `c785aeb`.

A filesystem timestamp scan found no new non-Git project file after the
13:52 EDT recovery commit. The full benchmark outputs and raw Slurm log remain
local at the paths and checksums recorded in the benchmark report. No pending
job, undocumented completed run, new checkpoint, or new result artifact was
found.

## Recovered unfinished work and current gates

The broken transcript contains no uncommitted code or completed result beyond
the benchmark outcome recovered in `c785aeb`. Its unfinished items are plans or
gates, not missing execution artifacts:

1. C5 reward rejection still has no eligible full-scale result. The latest full
   attempt timed out at step 571/604 and produced no eligible checkpoint or
   final metric. A plain retry was not authorized.
2. The fixed-proof benchmark supports 64 verifier workers (1.385x aggregate
   verifier speedup with identical outcomes), but a separately scoped and
   authorized actor-loaded feasibility check is still required before treating
   that setting as safe for full training.
3. Exact checkpoint recovery remains unimplemented. The required atomic
   manifest, optimizer/scheduler/RNG/buffer restoration, crash-consistency
   tests, distributed trajectory comparison, and runtime test are specified in
   `research/CHECKPOINT_RECOVERY_AUDIT.md`. The September 21 override guard is a
   fail-closed safeguard, not recovery support.
4. The completed admission analysis shows that reward rejection changes which
   saturated all-correct groups enter optimization. Any future C5 result must
   report these strata. An admission-aware soft comparator is a conditional
   follow-up, not a registered or queued run.
5. ProofNet validation and a deployment-restriction study remain proposed
   research directions in `research/CAPABILITY_RETENTION.md`; neither is an
   approved pending job.

The present scientific conclusion is therefore unchanged: C2 soft
unlikeliness outperforms C3 zero-advantage blocking on the matched syntactic
diversity comparison; C3 still demonstrates substantial diversity retention
relative to standard GRPO; and C5 reward rejection is scientifically
unresolved because no eligible full run exists. All 93 project tests pass at
the audited revision plus these documentation-only changes.
