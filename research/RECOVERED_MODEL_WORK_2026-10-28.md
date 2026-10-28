# Work recovered from the broken Codex sessions

Documented October 28, 2026. This report describes historical work recovered
from local transcripts and checked against repository commits and artifacts.
It records no new training, scheduler submission, or scientific result.

## Which model and which work

The requested session, **Recover broken session work**, is
`01a0c514-719f-7882-9c04-8dcd6dcb1a81`. Its recorded turn context identifies
`gpt-5.6-sol` with low reasoning effort. That is transcript metadata, not an
independent assertion about the serving backend. Its substantive conversation
runs from September 21, 2026, 17:47 to 17:53 UTC.

The user asked it to reconcile the work from older broken session
`01a086a9-6c8d-7400-a322-54110e516f44` and explain the project's position.
The recovery model's contribution was an audit and a late-result publication;
it did not originate all the research summarized below. The older session
contains the research and operational history from September 9–21.

Both sessions used `/scratch/memoozd/rrl`. The actual Git checkout is
`/scratch/memoozd/rrl/restriction-rl/repository`, on branch
`work/dominant-mode-rejection`.

## What the recovery model completed

It read the older JSONL transcript despite the SQLite resume failure, located
the checkout, compared the saved work with Git, and inspected reports, ignored
artifacts, and scheduler state. Its final message reported that the existing
work was tracked and the branch synchronized with GitHub.

It found one outcome missing from the older session's final status: verifier
benchmark **918556 had completed** after that session's last scheduler check.
The model recorded the completed result in three files:

- [PROJECT_STATE.md](../PROJECT_STATE.md)
- [VERIFIER_CONCURRENCY_BENCHMARK.md](VERIFIER_CONCURRENCY_BENCHMARK.md)
- [verifier_workers_918556_summary.json](../results/verifier_workers_918556_summary.json)

The resulting commit is
`c785aeb5a7ba21cdc844a7b4183af3a4078b795d`, **Record verifier concurrency
benchmark results**. Its diff adds 78 lines across those three files. The
commit exists in the current branch's ancestry. The transcript reports six
benchmark tests passing and a successful push; these are historical validation
claims, not tests rerun by this documentation pass. The benchmark artifact is
still tracked and its latest modifying commit is `c785aeb`.

The recovery model explicitly left the broken session and databases untouched.
The later [September 23 audit](RECOVERY_AUDIT_2026-09-23.md) independently
documents the same recovery outcome and reconciles it with Git and accounting.

## Research preserved by that recovery

### Completed C2 versus C3 comparison

C2 applies soft unlikeliness weighting. C3 zeroes the final policy advantage
of the frozen archive's dominant correct mode. These completed conditions
must be distinguished from C5 reward rejection, which changes the reward
before group admission and normalization.

The registered C2 run completed 604 steps. The saved matched analysis favors
C2 over C3 on the measured tactic-signature diversity:

| Measure | C2 | C3 |
|---|---:|---:|
| Training correct tactic modes | 75,180 | 53,825 |
| Training expected modes at 16 correct draws | 7.4585 | 5.4732 |
| Held-out correct tactic modes | 12,006 | 10,444 |
| Held-out expected modes at 16 correct draws | 10.9667 | 10.1568 |
| Theorems solved in the combined 467-theorem panel | 277 | 277 |

The held-out rarefaction comparison uses 259 common eligible theorems.
These are syntactic proof-mode measurements, not demonstrated mathematical
novelty, elegance, or general capability retention. The comparison protocol,
run IDs, and interpretation limits are in [C2_COMPARISON.md](C2_COMPARISON.md).
Compact evidence is in
[training comparison](../results/c2_unlikeliness_vs_c3_training_seed42.json)
and [held-out comparison](../results/c2_unlikeliness_vs_c3_seed42_pass128.json).
Commit `c0d3d74` published the comparison, proof-characteristic analyses,
failure audits, and operational snapshots.

### C5 failure and recovery safeguards

C5 training job `909982` timed out at step **571/604**, with no saved
checkpoint or finalized proof log. Its dependent comparison `910004` was
canceled at zero runtime. This supplies no eligible full C5 result and cannot
establish that reward rejection beats C2 or C3.

The source audit identified missing optimizer/scheduler/RNG restoration,
non-atomic actor/buffer/proof saves, and incomplete-checkpoint selection risks.
Commit `34d4e7d` documented the hazards and proposed validation gates.
Commit `9bc4226` then closed an initialization-guard bypass through checkpoint
and step overrides, adding regression coverage. The guard is implemented;
exact full-state recovery was not implemented by those changes. See
[CHECKPOINT_RECOVERY_AUDIT.md](CHECKPOINT_RECOVERY_AUDIT.md).

### Saturated-prompt learning mechanism

Commit `1176dcd` tested the production selection and advantage logic with
synthetic groups. Under the registered filter, C1/C2/C3 discard all-correct
groups. C5 can retain an all-correct group containing both blocked and
alternative proofs, assigning negative advantage to blocked proofs and
positive advantage to alternatives. All-blocked groups still skip.

A discriminating control showed that soft weighting can also provide a signal
if its admission filter is changed. This is therefore an admission mechanism
worth measuring, not a unique capability established for hard rejection.

Commit `aaf3c77` added a completed-log analyzer, tests, and compact evidence:

- C2 saved samples contain 275 saturated mixed-mode groups, 27.12% of the
  1,014 archive-eligible groups.
- C3 saved samples contain 347, or 34.22% of archive-eligible groups.
- C3's reconstructed 13,906 blocked correct proofs match finalized telemetry.

These counts measure exposure on existing C2/C3 samples, with counterfactual
archive membership for C2. They do not predict a future C5 distribution or
prove a trained-model benefit. See
[SATURATED_PROMPT_MECHANISM.md](SATURATED_PROMPT_MECHANISM.md) and
[the admission artifact](../results/training_admission_c2_c3_seed42.json).

### Verifier throughput result recovered after the session stopped

The bounded diagnostic replayed four fixed 512-proposal panels, each twice
with 32 workers and twice with 64: 2,048 distinct proofs and 8,192 verification
attempts. Commit `5d19e76` introduced the benchmark; later commits pinned its
runtime path and tested persistence/input safety.

Job `918556` completed September 21 at 10:19 EDT, elapsed 19m36s. Mean pass
time was **75.445 seconds at 32 workers** and **54.486 seconds at 64**, a
**1.385× aggregate speedup**. All sixteen passes finished with zero verdict
or failure-class disagreements, parse failures, or timeouts.

The actor was not loaded. Consequently this measures verifier throughput,
not full-training memory safety, end-to-end speedup, or proof performance.
The historical decision was a separately scoped actor-loaded feasibility
check before any full C5 retry. The result publication is the recovery
model's concrete contribution in `c785aeb`.

## What remained unfinished at that historical handoff

There was no eligible full-scale C5 result, no validated exact checkpoint
continuation, and no demonstrated capability-retention/generalization benefit.
An actor-loaded feasibility check, a possible admission-aware soft comparator,
and proposed retention/deployment-restriction studies were follow-up gates or
ideas, not completed experiments. Repeated scheduler waits at the end of the
older transcript add no new scientific evidence.

This is a September handoff, not the current experiment queue. Later October
work includes C5 feasibility evidence and a procedure-execution/transfer track;
consult [PROJECT_STATE.md](../PROJECT_STATE.md) before continuing work. This
report does not restart the historical research goal or submit any experiment.

## Provenance and recovery limits

The local source transcripts are:

```text
/scratch/memoozd/.codex/sessions/2026/09/21/rollout-2026-09-21T13-47-26-01a0c514-719f-7882-9c04-8dcd6dcb1a81.jsonl
/scratch/memoozd/.codex/sessions/2026/09/09/rollout-2026-09-09T10-54-05-01a086a9-6c8d-7400-a322-54110e516f44.jsonl
```

At the October recovery inspection they parsed as 169 and 13,854 JSONL records,
respectively. SHA-256 values read during this documentation pass:

```text
recovery: 78bd4f8a31d80fbba57f0b92607b7dd873ed0defcf0fe08b229160c47e2b8079
original: f60204112f1751abdd0cdec10d30832d53917478ad276a28ac84abda254dcc85
```

The September 23 audit records earlier counts/checksums. The current files
have an additional record each; the historical checksums describe those
earlier snapshots, not the current files. Raw transcripts remain local because
they include full prompts and operational tool traces. This report publishes
the recovered work and provenance, not a backup of every raw artifact.

A readable recovery extract is also saved locally at
`/home/memoozd/codex-recovery-01a0c514/conversation.txt`.
Content recovery does not repair the Remote renderer: the October inspection
confirmed corruption in `thread_history_1.sqlite`. No database or daemon
repair is claimed here.
