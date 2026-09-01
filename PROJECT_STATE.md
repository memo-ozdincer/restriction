# Project State

Last updated: 2026-09-01

## Completed

- [x] Provisioned and validated the Lean, veRL, Ray, and DeepSeek-Prover
  environment on H100 nodes.
- [x] Verified unchanged base-model inference and standard-GRPO training.
- [x] Implemented deterministic proof canonicalization and tactic signatures.
- [x] Implemented a persistent, checksummed dominance archive.
- [x] Integrated hard dominant-mode blocking behind a configuration flag.
- [x] Enforced pristine actor and reference restart for Restriction-RL.
- [x] Added proposal-level block decisions and complete physical compute
  accounting.
- [x] Added behavioral coverage for canonicalization, archive persistence,
  threshold boundaries, blocked advantages, incorrect advantages, all-blocked
  prompt skipping, disabled-feature equivalence, and restart enforcement.
- [x] Built the C0 archive from all 9,655 training theorems and 308,960
  proposals.
- [x] Completed full standard-GRPO and Restriction-RL training runs.
- [x] Completed fresh pass@32 evaluation on registered-valid and miniF2F-test.
- [x] Completed paired theorem-level, rarefaction, concentration, training
  momentum, and base-mode recovery analyses.
- [x] Assembled and relocation-tested a self-contained transfer directory with
  repository history, datasets, base/C1/C3 weights, run evidence, Lean and the
  built verifier, and the exact PyTorch/CUDA Python environment.

## Headline result

At the same 308,960-proposal training budget, Restriction-RL produced 53,825
distinct correct tactic signatures versus 34,336 for standard GRPO, a 56.8%
increase. It also produced 111,570 exact correct proofs versus 66,515, a 67.7%
increase.

Across 467 held-out theorems, Restriction-RL produced 3,926 correct tactic
signatures versus 3,445 for standard GRPO. It solved 273 theorems at pass@32
versus 271. The paired increase is 1.03 correct tactic signatures per theorem
(`p = 7.94e-15`).

At exactly 16 correct held-out draws in all three conditions, Restriction-RL
has 10.27 expected tactic modes per theorem versus 9.14 for standard GRPO
(+12.4%, paired `p = 7.20e-15`). Its C3-over-C1 coverage advantage is positive
at every frozen representation resolution, from first tactic head through
exact normalized proof; this does not make tactic signatures semantic proof
strategies.

Rarefaction over all proposals in the completed pass@32 sample shows the
intended head-to-tail tradeoff: C3's expected mode coverage relative to C1 is
-4.3% at one draw, crosses to +1.3% at four, then grows to +5.0%, +9.1%, and
+14.0% at 8, 16, and 32 draws. The pending pass@128 run tests whether this
accumulation advantage persists beyond the observed 32-proposal support.

Restriction-RL recovered 43.3% of base-policy tactic signatures observed at
least twice but absent from the standard-GRPO sample. Recovery reached 58.8%
for signatures observed at least four times in the base distribution.

Machine-readable results are in:

- `results/registered_c0_c1_c3_seed42.json`
- `results/theorem_selection_c1_vs_c3_seed42.json`
- `results/training_dynamics_c1_vs_c3_seed42.json`
- `results/registered_c0_c1_c3_seed42_pass32_accumulation.json`
- `results/c0_crossfit_blocking.json`
- `results/reward_rejection_replay.json`
- `results/c5_reward_rejection_smoke_seed42.json`

## Active: pass@128 retry

Fresh matched pass@128 evaluations evaluate 467 theorems with 128 proposals per
theorem, or 59,776 proposals per condition.

- Jobs `20173754` and `20173755` received allocations on August 27 but stopped
  before model-worker creation because the reusable launcher omitted the
  sample-only `algorithm.adv_estimator=grpo` override recorded in D-033. They
  produced no proof snapshots or scientific results.
- Their finalizers `20173757` and `20173758` failed closed as designed.
- The matching pending C3 job `20173756` and finalizer `20173759` were
  cancelled before allocation on August 31.
- D-035 records the fix, regression test, and requirement for fresh C0/C1/C3
  retry directories.
- Source-cluster retry jobs `20914996`, `20914997`, and `20914998` and their
  finalizers did not transfer as live scheduler state; their IDs are historical
  only on this destination.
- D-045 originally split C0 from a sequential C1/C3 pass@128 workbench.
  D-047 now assigns C1, C3, and C0 separate full-node allocations after the
  destination memory ceiling made 64-worker verification unsafe. Every fresh
  condition uses the same frozen scientific payload and 32 verifier workers,
  finalizes and validates independently, and retains its allocation with
  `sleep infinity` for visible adjustment.
- D-046 records an operational failure at the start of job `868001`: the
  transferred Ray `gcs_server` and `raylet` lacked execute bits. The first C1
  attempt failed during `ray.init`, before model-worker creation or any proof
  snapshot, and is permanently excluded. Their original hashes were preserved
  while restoring user execute permission; a node-local Ray smoke passed.
  Fresh `retry2-rayexecfix` then loaded both models but exposed the same
  transfer defect on Triton's `ptxas` at the first forward pass, again before
  any proof snapshot, and is also excluded. A complete standalone-ELF audit,
  explicit permission restoration, and compiled GPU smoke pass. Fresh
  `retry3-nativeexecfix` generated successfully but exposed the frozen
  launcher's missing legacy Lean-home path: three batches produced only
  verifier system errors and were stopped. Linking that absent path to the
  pinned bundled Elan runtime made the verifier's known-correct upstream smoke
  pass completely. Fresh C1 `retry4-verifiersmoke` then confirmed healthy
  generation and verification for three batches, but 64 verifier workers
  exhausted the 755-GiB node during batch 4 and Ray killed all four model
  workers. It was stopped without a final proof snapshot and is permanently
  excluded. Repository and pending-workbench preflights cover Ray, Triton,
  PyTorch's native helper, the compiler boundary, and the frozen verifier-home
  contract.
- D-047 records the memory recovery before another scientific retry. A
  32-worker replay of the exact 128 frozen proofs around the failing batch
  reproduced all four historical correctness counts exactly, raised no
  verifier exception, and peaked at 461.2 GiB, leaving 294.3 GiB available.
  The remaining C1, C3, C0, and matched-control runs therefore use the same
  validated 32-worker infrastructure setting in separate allocations.
- C1 `retry5-workers32` crossed the old batch-4 boundary but is excluded. At
  step 32, Ray reported 754.64/755.57 GiB used and killed the main task; its
  inherited verifier workspace occupied 566 GiB in tmpfs despite the sparse
  source occupying only 4.3 GiB. Retry6 passed sparse staging at 4.34 GiB but
  failed before worker creation on an overlong Ray socket path. Retry7 fixed
  both startup defects and completed nine batches, but was proactively stopped
  when independent C0 retry2 proved that an initially 4.4-GiB verifier
  workspace can grow to 566 GiB during access: C0 completed step 31 and then failed
  step 32 at 718.46/755.64 GiB plus tmpfs `No space left on device`. D-053
  therefore places verifier workspaces on disk-backed `/tmp`, retains the
  validated 32-worker cap by default, and keeps only Ray IPC/caches in short
  `/dev/shm` paths. C1 retry8 subsequently completed 86 batches, but batch 87
  drove 32 concurrent Lean
  REPLs to about 21--22 GiB RSS each; Ray killed the main task at
  739.19/755.57 GiB. The immutable finalizer produced no result, and all 44,032
  partial proposals are permanently excluded. D-073 uses the still-retained
  job `868001` for a fresh C1 retry9 with only verifier concurrency reduced to
  16. Observed memory projects near 350 GiB for the pathological batch, and
  measured timing projects 10.83 hours against 15.15 hours remaining. No prior
  proposal is reused. Its first five steps then matched retry8 exactly on every
  scientific field. The batch-4 stress case completed all proposals at a
  334.93-GiB peak; the observed 1.5689 verifier-time ratio updates the full-run
  projection to 8.57 hours with about 6.5 hours of hard-limit margin. C0 retry3
  independently failed at 739.24/755.64 GiB in the same batch 87 after 86
  complete batches. D-075 excludes that partial, proactively stops C3 retry2
  at 82 complete batches before the now-predictable boundary, and applies the
  validated 16-worker containment to fresh C0 retry4 and C3 retry3. C3 retry3
  is live in retained job `868228`; complete-node 23-hour C0 job `870055`
  allocated on `trig0045` under `rrg-zhijing`. C0's first five batches match
  retry3 exactly; C3's generated mode totals match retry2, while two borderline
  batch-4 Lean timeout outcomes differ. Peaks were 329.17 and 344.18 GiB and
  projected totals are 9.22 and 7.89 hours. D-067 and D-068 make 24-hour
  matched-control retry `869225` eligible. D-078 replaces its zero-runtime
  32-worker evaluation job with dependency-bound 16-worker job `870226`,
  matching C3 for the held-out panel. D-066 makes 24-hour C5 retry `869132` eligible.
  All fresh directories refuse reuse.
- D-056 refines the operational diagnosis: the authoritative verifier is only
  about 4.3 GiB by both allocated and apparent size, so sparse holes alone
  cannot explain a 566-GiB destination. The nodes instead allowed unlimited
  multi-gigabyte core dumps from repeatedly terminated Lean REPL processes,
  using the job-local `core.<host>.<exe>` pattern. The failed expanded trees
  were already removed, so this mechanism is strongly indicated rather than
  directly proven. Core size is now zero for all live C0, C1, and matched-
  control process trees and is inherited by every pending launch; disk-backed
  verifier staging remains as independent containment.
  Both recovered evaluations subsequently crossed batch 4: C1 reproduced its
  historical 273-error and 1,659-cumulative-mode counts exactly at a
  583,052,864-KiB peak, while C0 reproduced 1,998 cumulative modes with one
  timing-sensitive verifier error differing (323 versus 324) at a
  545,911,400-KiB peak. Both returned to about 110 GiB used and continued.
  They have now also crossed the exact batch-32 boundary where the preceding
  C0 retry exhausted tmpfs and the preceding C1 retry was stopped to avoid the
  same failure. C1 batch 32 completed in 534.5 seconds with 395 verifier errors
  and 12,501 cumulative unique modes at a 530,529,524-KiB peak; C0 batch 32
  completed in 545.7 seconds with 499 verifier errors and 15,830 cumulative
  unique modes at a 474,690,440-KiB peak. Both returned near 110 GiB used,
  both disk-backed verifier trees remain exactly 4,555,536 KiB, all sampled
  live Lean workers retain zero core limits, and neither log contains a fatal,
  space, or OOM signature. They continued through batches 40 and 32
  respectively; final registered results do not yet exist.
- C3 pass@128 job `868228` started on H100 node `trig0016` at
  2026-09-01T01:32:05-04:00. Its persistent watcher launched immutable runner
  `dc4090d4...`, staged the verifier at 4,555,536 KiB on disk-backed `/tmp`,
  and verified a zero inherited core limit in both the runner and Ray main
  task. The first complete 512-proposal batch recorded 304 verifier errors,
  208 correct proposals, 487 unique tactic signatures, zero evaluation-time
  blocks, and 367.9 seconds including the startup tail. Node use returned to
  about 114 GiB and no error signature appeared; no finalized C3 result exists
  yet.
- D-042 records the destination memory adaptation: `compute_full_node` grants
  the complete 770,000-MiB physical node, which is the largest available on
  this cluster rather than the source cluster's 1-TB request. Jobs `868001`,
  `868049`, `868076`, and `868228` each request all 770,000 MiB, 96 CPUs, and
  four H100s; memory use and OOM state must be monitored and any incomplete run
  remains excluded. D-047 supersedes the unsafe 64-worker destination setting
  with the targeted 32-worker replay.
- D-038 freezes the pass@128 accumulation, correct-draw rarefaction,
  concentration, suppression/recovery, and proof-representation sensitivity
  panel before any destination pass@128 result exists. The implementation
  reproduces the finalized pass@32 metrics and registered paired test exactly.
  D-043 materializes that pass@32 baseline as a checksummed result before the
  pending pass@128 payload starts.
- D-057 binds completion of all three finalized pass@128 runs to the unchanged
  D-038 analysis at execution snapshot `8dc7563`. A persistent result watcher
  writes `registered_c0_c1_c3_seed42_pass128.json` and
  `registered_c0_c1_c3_seed42_pass128_accumulation.json` atomically only after
  all proposal, proof-log, parquet, classification, and completion gates pass.
  Its pre-result smoke failed closed and produced no output. D-065 corrects
  only its orchestration status gate to recognize the upstream registered
  post-completion sentinel exit `1`. D-073 reroutes that unchanged frozen
  analysis from excluded C1 retry8 to eligible retry9; runner `a48dee62...`
  and watcher `28030377...` retain every scientific validation gate.
  D-069 adds a separate resource-release watcher: only after both registered
  pass@128 outputs reproduce every eligible source path, completion marker,
  metrics hash, and proof-log hash will it cancel the three otherwise-idle
  retained workbenches. This cannot alter an evaluation or analysis and may
  free complete H100 nodes for the pending C5 and matched-control retries.
  D-070 supersedes that conservative waiting rule before any release: each
  node may now be freed immediately after its own finalized metrics, sentinel,
  proposal accounting, parquet, proof-log, manifest, and hardware hashes pass
  independently. D-073 reroutes only its C1 source path to retry9. It also
  waits for the finalizer's terminal log record and
  completion appendix, preventing a metrics-write race and correcting only the
  stale `running` metadata status after completion. The joint D-038 analysis
  still waits for all three durable sources and is unchanged.
- D-039 registers the full seed-42 C3-matched no-blocking control needed to
  isolate blocking from C1/C3 optimizer differences. Its launcher is tested to
  match every non-blocking C3 trainer argument. Destination job `868049` is
  queued for a separate 23-hour four-H100 full-node allocation from execution
  snapshot `8dc7563`; it has not yet produced data. Its fresh runner SHA-256 is
  `2fe8bdf5564481fffb513922498f4f6ea042a3949cfc07c9de3b76c420145609`
  and records the complete native-runtime checks and shared 32-worker verifier
  setting. Its frozen scientific payload is unchanged.
- D-040 freezes the paired training, correct-draw rarefaction, concentration,
  C0-recovery, and archive-eligibility analysis before control data exists.
  Its end-to-end surrogate validation reproduces the existing C1/C3 artifact.
  D-058 now binds finalized control training to that immutable panel and writes
  `c3_vs_matched_control_training_seed42.json` atomically.
- D-064 protects the matched-control training result without changing the live
  trajectory. At step 116, the control had used 4.63 compute hours; scaling the
  completed C1/C3 remaining-step schedules by the observed destination
  32-worker slowdown projected only about 10--20 minutes of margin in job
  `868049`. Actor-only checkpoints cannot preserve optimizer/scheduler state,
  so resume was rejected as scientifically ineligible. Fresh 24-hour job
  `869225` is dependency-bound by `afterany:868049`: after the retained
  workbench ends, it first validates any complete primary with the frozen
  training loader and exits without retraining; only incomplete/ineligible
  primary artifacts start the identical pristine retry in a new directory.
  Immutable runner SHA-256 is
  `2120c329c85ffa12bc0b43a50dfc9bc8069771b90c2e3631e0221e256dd06430`.
  D-064 also corrects the training-analysis execution gate: successful upstream
  completion is the registered sentinel exit `1`, not zero. Sentinel-aware
  runner `da060659...` and watcher `bb1babac...` now wait for finalized metrics
  before executing the unchanged D-040 panel; the stale watcher was stopped.
  At step 130, D-067 supersedes continuation of the 23-hour primary: its
  cumulative 1.176 destination/C3 schedule ratio projected about 23.36 total
  allocation hours, roughly 21 minutes beyond the hard limit. Slurm denied a
  scheduler-only extension without changing job state. Primary `868049` is
  therefore stopped before any final metric, its partial trajectory is
  permanently excluded, and the already-frozen pristine 24-hour job `869225`
  is released and eligible. No partial optimizer, actor, rollout, or proof
  state is reused. D-068 reroutes the unchanged D-040 training analysis and
  D-041 held-out evaluation/analysis to that single eligible retry. The stale
  delayed primary-evaluation allocation is cancelled before runtime; its
  replacement job `869396` was dependency-bound by `afterok:869225` and used a
  fresh run directory with the same registered parquet and evaluation payload.
  D-078 cancels it at zero runtime after timeout evidence showed verifier
  concurrency must be matched, replacing it with 16-worker job `870226` and a
  new fresh directory while preserving the dependency and scientific payload.
  Retry-aware D-040 and D-041 watchers are live; the primary-bound watchers and
  obsolete evaluation launcher were stopped.
  D-071 restores the frozen finalizer-recognized prepared status line in the
  pending control and C5 retries and retry-derived control evaluation metadata,
  while retaining queue and eligibility state as separate bullets; finalized
  metadata will therefore transition cleanly without changing any artifact or
  runner.
- D-044 hardens the registered analyzers before either destination job starts.
  Training and evaluation inputs must now reproduce finalized condition,
  classification, completion, proposal, padding, parquet, and proof-log hash
  invariants; the matched control must additionally have zero intervention
  counters and no archive. All 36 project tests pass, and the stricter loaders
  reproduce the completed training and pass@32 findings exactly.
- D-041 freezes the matched C3-versus-control held-out accumulation,
  rarefaction, theorem-selection, concentration, and representation panel.
  Evaluation preparation/finalization now accepts the control as a distinct
  no-update condition; no matched held-out data exists yet. D-049 supersedes
  the attached evaluator after observed control timing projected only about
  3.5 hours remaining, below D-045's ten-hour gate. A separate delayed 23-hour
  workbench will wait fail-closed for finalized training, validate the zero-
  intervention control, and run the identical 32-worker pass@128 payload. Job
  `868264` is eligible from September 1 at 17:00. Its
  runner SHA-256 after the D-053 disk-staging hardening is
  `2dbc8208e357cd3dd6cdd48e69cec2f98ee2752cacacaca3652eb4de21f39eff`.
  A separate D-058 result watcher binds finalized C3 and control evaluations to
  the unchanged held-out panel and writes
  `c3_vs_matched_control_heldout_seed42_pass128.json` atomically. D-065
  corrects only that watcher's orchestration status gate to require the exact
  upstream sentinel exit `1`; sentinel-aware runner `3e7b7e91...` and watcher
  `8f86fbfe...` are live and continue to fail closed until both registered
  evaluations finalize.
- The completed control and evaluations will determine whether the smallest
  decisive follow-up is replication, mechanism diagnosis, the registered
  StableTopBlock-Restart ablation, or a workload with richer proof variation.

## Experimental work branch: C5 reward rejection

Branch `work/dominant-mode-rejection` implements a stronger, separately named
exploration intervention. Lean correctness remains unchanged and is persisted
as `correct`. When a correct rollout matches the archived dominant tactic
signature, C5 marks it `training_accepted_correct=false`, assigns it binary
training reward zero, and lets ordinary group-relative normalization make it a
negative example whenever an alternative correct rollout is present. C3's
existing `zero_advantage` behavior remains the default.

The pre-run counterfactual replay is frozen in
`results/reward_rejection_replay.json`. Of 917 C3 training theorems with a
blocked rollout, 859 also had an alternative correct rollout. Those groups
contained 12,405 blocked correct and 11,598 alternative correct rollouts; the
proposed reward rule would assign mean standardized advantages -0.686 and
+0.913 respectively. This demonstrates a usable intervention signal but is not
an on-policy C5 result.

The implementation passes all 44 project tests and the complete destination
preflight. The frozen high-signal 16-theorem smoke passed its complete D-048
gate in H200 backfill job `868506`. All 512 proposals were accounted for: 230
blocked Lean-correct rollouts were reward-rejected, 254 alternative correct
rollouts retained positive reward, and 28 were Lean-incorrect. Their mean
group-relative advantages were respectively -0.968, +0.981, and -0.950. The
run performed a real 512-sample optimizer update, saved `global_step_1`, and
finalized in 438.8 seconds. Metrics and proof-log SHA-256 values are
`5d3e79e06f5f87829749f54e16f7a98370873ac623734dd9fd14e3a21b9ab98d`
and `2790fb3c64db5dbce300166d0ca1616b5348f66168c0f9c0b196faaf643acccd`.
This is engineering evidence that the intervention works on policy; it is not
a full C5 scientific result. D-051 authorizes a fresh 604-step C5 run only as a
secondary exploratory condition, preserving the primary matched-control and
pass@128 priorities.

The first full-scale attempt on H200, job `868541`, was stopped after two steps
because the transferred vLLM stack took 153 seconds to generate each of the
same first two seeded batches that took 22 and 16 seconds in the destination
H100 control. Its projected runtime was about 40 hours, beyond the 23-hour hard
ceiling. The partial directory is permanently excluded and contains no proof
snapshot, actor checkpoint, or finalized metrics. Duplicate pending H200 job
`868543` was cancelled without allocation.

Fresh matched-H100 job `868636` started on H100 node `trig0008` at
2026-09-01T01:32:17-04:00 from clean directory
`c5-reward-reject-full-20260901-seed42-a0f1235-h100-workers32`. It retains the
complete 9,655-theorem, 308,960-proposal seed-42 C3 payload and restarts from
the pristine base actor at execution snapshot `a0f1235`. Its fail-closed runner
SHA-256 is
`0683a7c6eb8b97b0713015027f61d39d5328188c7f9a7085288e497a0c56b07b`.
The first 20 optimizer steps completed without an error signature. Across all
20, blocked-correct and reward-rejected counts agree exactly, telemetry
category sums reproduce every update volume, every nonempty blocked-correct
mean advantage is negative, and every alternative-correct mean advantage is
positive. The checkpoint contains 7,840 update rollouts and 418 blocked
correct rollouts. Its 131.46-second mean step time projects another 21.33
compute hours against 22.18 allocation hours remaining, including C5's
137.1-second traversal of the batch position where the matched control took
357.6 seconds. The partition permits 24 hours, but Slurm denied extending the
already-running 23-hour job; no job state changed. D-060 therefore keeps the
valid run unchanged and monitors its rolling completion margin. The runner,
Ray main task, and sampled live Lean REPL workers all report zero soft and hard
core-file limits. The watcher's earlier isolated `unlimited` probe was a
pattern-matching false positive rather than a workload process: exact PID and
executable-name probes confirm the inherited limit. The disk-backed verifier
tree remains 4.4 GiB, the node has about 587 GiB available, and `/dev/shm` is
nearly empty.
Step 25 subsequently exercised the registered 300-second Lean timeout tail and
took 385.8 seconds, while preserving complete intervention accounting. D-061
keeps the primary run unchanged and pre-registers a fail-only operational
retry. D-062 corrects an operational validation assumption discovered from
live buffering: hard-blocking summaries are emitted per optimizer update, not
per dataloader step. Step 28's 224 retained proofs were therefore correctly
buffered into step 29's 704-proof update, producing 29 data-step records and 28
intervention summaries. The tested validator now reconstructs every buffer and
update event, requires each summary to equal its optimizer-update volume, and
separately accounts for any final sub-threshold residual. Replacement 24-hour
job `869132` remains `afternotok:868636`. If released, it first recovers a
scientifically complete primary that failed only at the stale wrapper check;
only a genuinely incomplete primary starts the pristine retry. Dynamic
analysis job `869143` is `afterok:869132` and selects only that
prevalidated primary or the fresh retry. The superseded jobs `869096`,
`869097`, and `869133` were
cancelled with zero runtime. Primary analysis job `868700` remains bound by
`afterok:868636` for the normal success path.
At the step-40 runtime gate, all 39 optimizer updates and 14,912 optimized
proofs reconciled exactly with intervention telemetry. The cumulative mean
advantages were -0.656 for 808 blocked correct proofs, +0.543 for 9,280
alternative correct proofs, and -0.935 for 4,824 incorrect proofs. The full
40-step mean fell to 134.68 seconds and the last-ten mean to 124.43 seconds,
projecting roughly 18 minutes and 1.9 hours of allocation margin respectively.
D-063 therefore continues the unchanged primary while retaining the fail-only
recovery/retry path.
Step 44 then incurred a second registered 300-second verifier tail and took
346.38 seconds. After step 45, the observed mean projected the 23-hour primary
past its hard limit. A stronger schedule-matched estimate composed the measured
destination slowdown and C5 overhead with the exact completed C3 step schedule,
projecting about 23.38 hours total: roughly 23 minutes beyond the primary but
37 minutes inside the prepared 24-hour retry. D-066 therefore stopped primary
job `868636` at 03:22:50 based only on runtime, before any full metric existed.
Step 46 completed and logged while cancellation propagated, so all 46 partial
steps are permanently excluded with no final checkpoint, proof snapshot, or
metrics. Retry job `869132` became eligible at 03:22:57 and remains pending;
analysis job `869143` remains dependency-blocked. The released node `trig0008`
was independently drained by Slurm's health check for unresponsive
`nvidia-smi`, recovered at 03:25, and was immediately allocated to a
higher-priority job. While the retry was still unallocated, D-072 changed only
its Slurm billing account in place from `def-zhijing` to the authorized and
currently underused `rrg-zhijing` association. Job ID `869132`, its dependency,
immutable runner, inputs, run directory, requested hardware, and every
scientific setting remain unchanged. Its multifactor priority rose from about
582,824 to 1,126,546 and Slurm's estimated start advanced from 10:46 to 06:25
on `trig0008`; the live scheduler state, rather than that estimate, remains
authoritative. Slurm subsequently allocated retry `869132` on complete H100
node `trig0033` at 05:36:52. Startup retained the frozen input and runner
hashes, base-model initialization with resume disabled, seed 42, all 604 steps,
32 proposals per theorem, four H100s, 32 Lean workers, and `reject_reward` hard
blocking. The resolved configuration passed its built-in checks; analysis job
`869143` remains dependency-bound until successful finalization. At the D-077
step-22 gate, all 8,608 optimized proofs reconciled exactly across 22 updates:
464 blocked correct, 5,417 alternative correct, and 2,727 incorrect. Their
weighted mean advantages were respectively -0.709, +0.557, and -0.986; every
nonempty per-update category had the registered sign. All 465 physically
blocked proofs were reward-rejected, with one excluded from optimization only
because its prompt had no accepted alternative. Three 300-second verifier
tails occurred, but cumulative timed-step cost was only 9.45 minutes above the
excluded primary through the same 22 batches. Adding that measured excess to
the frozen 23.38-hour schedule projection gives about 23.54 hours total, or
roughly 27 minutes inside the retry's 24-hour limit. The unchanged run therefore
continues under later runtime gates. At D-079's step-40 gate, all 14,944
optimized proofs reconcile across 40 updates: 738 blocked correct, 9,516
alternative correct, and 4,690 incorrect, with weighted advantages -0.730,
+0.539, and -0.978. All 739 physically blocked proofs were reward-rejected;
one all-blocked prompt proof was correctly omitted from optimization. Timed
step cost is 15.81 minutes above the excluded primary through the same batches,
giving a 23.64-hour schedule-matched projection and about 21 minutes of retry
margin. Peak recorded node use is 171.03 GiB, so the run continues unchanged.
At D-080's tail-sensitive gate, evaluated immediately after step 61, all 21,696
retained proofs reconcile across 59 optimizer updates with zero residual:
1,322 blocked correct, 13,778 alternative correct, and 6,596 incorrect, with
weighted advantages -0.733, +0.532, and -0.964. All 1,324 physically blocked
proofs were reward-rejected; exactly two all-blocked-prompt proofs were
correctly omitted from optimization. The complete shared 46-step prefix gives
a 23.58-hour projection and roughly 25 minutes of margin. A more conservative
adaptive C3-schedule projection, which includes the consecutive verifier tails
at steps 56--58, gives about 23.90 hours and only about six minutes of margin.
Peak use is 171.14 GiB with no fatal signature, so the eligible run continues
unchanged under close monitoring.
At D-081's step-80 gate, mechanism accounting remains exact: 27,680 retained
proofs reconcile across 77 optimizer updates with zero residual, all 1,608
physically blocked proofs were reward-rejected, and every nonempty advantage
category has the registered sign. Runtime feasibility, however, is no longer
positive. Retry 1 used 12,619.066 timed-step seconds versus 9,995.476 for the
same C3 positions; scaling C3's exact remaining schedule by that 1.262478 ratio
projects 25.03 allocation hours, about 62 minutes outside the hard 24-hour
maximum. No complete C5 artifact exists. The retry-1 partial is therefore
permanently excluded on a runtime-only gate. Pristine retry-2 job `870750` is
registered `afternotok:869132`, and frozen analysis job `870751` is
`afterok:870750`; both had zero runtime and unfulfilled dependencies before the
transition. Retry 2 preserves the exact base actor, inputs, seed, optimizer,
proposal budget, 32-worker verifier, timeout, and `reject_reward` condition with
resume disabled.
Retry 1 was canceled at 09:17:37 after 3:40:45 and 83 visible excluded steps,
still without metrics or a final checkpoint. Retry 2 allocated the freshly
released `trig0033` node at 09:18:08; superseded analysis job `869143` was
canceled at zero runtime and replacement analysis `870751` remains
dependency-bound. A first-five-batch timing gate will test whether the same-node
runtime failure repeats without altering the condition.
That gate admits retry 2 in D-082. Its first five steps cost 608.530 seconds,
versus 893.026 in retry 1 and 681.364 in the primary; the adaptive exact-C3
schedule projection is about 23.39 hours, leaving roughly 37 minutes. Four
optimizer updates reconcile all 1,792 retained proofs with zero residual, all
106 physically blocked proofs were reward-rejected, every advantage category
has the registered sign, peak use is 172.72 GiB, and no fatal signature exists.
Step 1 matches both excluded predecessors scientifically, but later optimizer
and rollout records diverge despite the same seed; this is a matched stochastic
execution, not a bitwise replay. Eligibility derives only from the pre-result
runtime gate, never from selecting scientific outcomes.
At D-083's step-20 gate, 19 updates reconcile all 7,872 retained proofs with
zero residual; all 404 physically blocked proofs were reward-rejected and the
weighted advantages remain signed -0.664/+0.545/-0.983. Retry 2 is 429.987
timed-step seconds faster than retry 1 and only 149.813 seconds slower than the
primary through the same positions. Runtime estimators disagree: direct-prefix
and all-step projections are 23.42 and 23.36 hours, while a C3-ratio projection
is 24.70 hours because C3's steps 11--20 are unusually fast. The live last-ten
mean is 127.199 seconds. With mechanism and resources healthy and two current
estimators positive, retry 2 continues unchanged to a preselected step-40 gate.
The step-40 local observer was lost during a login-node Munge outage, but the
allocation and telemetry remained live and Slurm access later recovered. D-084
reconstructs the exact step-40 prefix and evaluates the live step-66 gate.
Retry-2/C3 timing ratios improve from 1.210 at step 40 to 1.134 at 60 and 1.126
at 66, giving a conservative exact-schedule projection of 22.40 hours; the
frozen shared-prefix projection remains 23.42 hours. Uniform all-step and
last-20 extrapolations are pessimistic at 24.52 and 25.69 because they smear
observed timeout clusters across the future. Mechanism accounting remains
exact: 22,912 retained, 22,720 optimized, a valid 192-proof residual, all 1,398
physical blocked proofs reward-rejected, and weighted advantages
-0.724/+0.528/-0.950. Peak use is 183.10 GiB with no fatal signature, so the
run continues unchanged to step 80.
At D-085's exact step-80 gate, retry 2 remains scientifically sound but fails
the predeclared runtime requirement. Its 80 timed steps cost 12,470.058 seconds
versus 9,995.476 for the same seeded C3 positions, a ratio of 1.247570. Adding
the measured allocation prefix to that ratio times C3's exact remaining
schedule projects 24.70 hours, about 42 minutes outside the hard limit. All
27,104 retained proofs reconcile across 73 optimizer updates with zero
residual: 1,634 blocked correct, 17,298 alternative correct, and 8,172
incorrect, with weighted advantages -0.751/+0.526/-0.963. Every physically
blocked proof was reward-rejected, peak use is 183.10 GiB, and no fatal event
exists. Retry 2 was therefore canceled at 12:49:39 after 3:31:31, without
metrics, finalization, or a checkpoint, and is permanently excluded.
Pristine fail-only retry-3 job `871169` briefly received the released
`trig0033` node, but the scheduler canceled it before its batch runner executed
and drained that node for `prolog.chk.nvidia-smi.unresponsive`. The retry-3
directory remained untouched. Identical job `871184` is now pending a healthy
four-H100 node, and frozen analysis job `871185` is dependency-bound to its
successful completion. The failed-node event changes no scientific setting.
D-086 supersedes that scheduler routing after Slurm automatically returned
`trig0033` to service and allocated job `871184` there. The allocation was
canceled after 2:17 of startup and before any completed step, metrics, or final
checkpoint; analysis `871185` had zero runtime. Separate pristine job `871191`
is pending with authoritative `ExcNodeList=trig0033`, and frozen analysis job
`871192` is `afterok:871191`. All scientific settings and the complete H100
hardware class remain unchanged. Superseded jobs `871187`--`871190` had zero
runtime and no artifact; only `871191` is eligible to start.
Job `871191` allocated the node-excluding `trig0031` request at 13:15:02 in
D-088. Its first five batches preserve exact C5 mechanism accounting across
1,856 optimized proofs: 113 blocked correct at mean advantage -0.649, 1,064
alternative correct at +0.615, and 679 incorrect at -0.856, with zero residual
and every physical block reward-rejected. Timed cost is 840.692 seconds,
dominated by one 355.882-second verifier tail. That prefix is faster than
excluded retry 1 but slower than retry 2; because prior five-step ratios were
not predictive, the unchanged run continues to an exact step-20 gate.
That longer D-090 gate is positive. Through 20 steps, all 7,840 optimized
proofs reconcile with zero residual: 443 blocked correct, 4,826 alternative
correct, and 2,571 incorrect, with weighted advantages -0.618/+0.558/-0.942.
Every physical blocked proof was reward-rejected. The prefix cost 2,664.161
seconds, only 35.059 seconds above the excluded primary and faster than both
long-node retries. The frozen schedule projection is 23.39 hours; a
tail-sensitive exact-C3 projection using the conservatively later 48:22
allocation observation is 23.70 hours, still about 18 minutes inside the hard
limit. Peak use is 173.02 GiB with no fatal signature, so the run continues
unchanged to step 40.
The D-094 step-40 gate remains positive. Forty updates account for all 15,008
optimized proofs: 801 blocked correct, 9,474 alternative correct, and 4,733
incorrect, with weighted advantages -0.691/+0.534/-0.952 and zero residual.
All 801 physical blocks were reward-rejected. Timed cost is 5,636.892 seconds,
249.764 seconds above the excluded primary but faster than both long-node
retries at the same positions. Frozen-schedule and exact-C3 projections agree
at 23.45 hours; even uniform live-prefix extrapolation is 23.75 hours. Peak use
is 180.30 GiB with no fatal signature, so the unchanged run continues to the
exact step-80 gate.
At D-096's exact step-80 gate, retry 3 remains mechanism-valid but narrowly
fails the hard runtime rule. Its first 80 timed steps cost 12,135.690 seconds
versus 9,995.476 for C3, a ratio of 1.214118. The frozen remaining-schedule
projection is 24.0527 hours, 3.16 minutes outside the limit. All 27,424
optimized proofs reconcile with zero residual: 1,623 blocked correct, 17,413
alternative correct, and 8,388 incorrect, with weighted advantages
-0.750/+0.524/-0.942; all 1,623 physical blocks were reward-rejected. Job
`871191` and zero-runtime analysis `871192` were canceled without a final
checkpoint or metrics and are permanently ineligible. Pristine retry-4 job
`871725` allocated `trig0058` at 16:56:02 EDT with both empirically infeasible
nodes (`trig0031` and `trig0033`) excluded. Its frozen configuration validates
`reject_reward`, 32 proposals, 32 Lean workers, 604 steps, the pristine base
restart, and resume disabled; analysis `871726` is dependency-bound to it.
Every scientific setting is unchanged.
No full C5 result exists until all 604 steps finalize and validate.

D-098 admits retry 4's startup and first five batches. All 1,856 optimized
proofs reconcile with zero residual: 119 blocked correct at weighted mean
advantage -0.612, 1,043 alternative correct at +0.625, and 694 incorrect at
-0.834. Its first optimizer step matches retry 3 on all 47 recorded non-timing
fields, and every physical block was reward-rejected. Correctness is 1,322/2,560
versus C3's 1,324/2,560 and raw unique proofs are 2,165 versus 2,180. The
prefix cost 703.308 seconds and has no fatal signature. Because prior
five-step runtime ratios were not predictive, the unchanged run continues to
the exact step-20 gate; these partial outcomes are diagnostic only.

The D-095 matched-control gate also resolved operationally. Retry 1 completed
exactly 80 visible steps with 12,441.829 timed seconds versus C3's 9,995.476,
a ratio of 1.244746. Applying that ratio to C3's exact remaining schedule and
adding the first visible step-80 allocation prefix projects 24.6669 hours,
about 40 minutes beyond the hard limit. Job `869225` was therefore canceled
without a final checkpoint or metrics and is permanently ineligible as the
registered full control. Pristine retry-2 job `871853` excludes only
runtime-infeasible `trig0044`; frozen training analysis `871854` is
dependency-bound. Its account moved in place to authorized `rrg-zhijing` for
queue priority only. Fresh 16-worker pass@128 evaluation `871859` is bound by
`afterok:871853` with immutable runner SHA-256
`d166f33419e962bbde1dc3bb083bdd06dd12bedbb7b1522bb96a3d47227312ff`.
All scientific settings are unchanged.
At D-099, retry 2 allocates eligible `trig0036` and passes first-batch replay.
All 46 non-timing fields match excluded primary `868049`: 416 accepted and
trained, 96 rejected, 187 verifier errors, 437 cumulative unique proofs, zero
blocks, and zero skipped prompts. Step 1 costs 152.397 seconds versus 138.232
in the primary; peak use is 176.71 GiB with no fatal signature. The unchanged
run continues to the exact step-20 runtime gate with partial diversity sealed.
At D-100, the same eligible control reaches step 5 with 2,560 physical
proposals, 1,301 correct proofs, 2,188 cumulative raw unique proofs, and all
1,728 retained samples trained, with zero blocks or skipped all-blocked
prompts. It costs 667.525 seconds and has no fatal signature. At the same five
batches C5 retry 4 has 1,322 correct and 2,165 raw unique proofs, so the small
raw-uniqueness direction from the excluded step-80 panel is not stable at
shallow depth. Both unchanged runs continue; this prefix is diagnostic only.

The first eligible destination pass@128 source is now complete. C1 retry-9
finalized all 117 batches at 13:14 EDT with metrics SHA-256
`fcdd5a6dcb76c8ab7735bc8b4c445acf349e7a9805c67a0eb9fc369ee35c26b9`:
59,776 registered proposals, 59,904 physical rows, 128 excluded padding rows,
and 29,172 correct registered proofs. MiniF2F records 2,979 correct modes and
121/244 solved at 128; registered validation records 5,489 modes and 154/223
solved. D-087 corrects the release watcher to reconcile failure classes with
registered proposals while preserving physical proof-log accounting. Corrected
watcher SHA-256 is
`98398715b991f8c29b7b3aad082c0f3500e80ca1570e0d758b894d6b5de07f1d`;
it validated the source and released job `868001`. No C0/C1/C3 comparative
result exists until C0 and C3 also finalize and the frozen joint analysis runs.
The eligible C3 retry-3 source finalized all 117 batches in D-092 with metrics
SHA-256 `39bbdd944a20f8e01abe0a532cd880e245e28da373588e98ed726ded26724dd1`:
59,776 registered proposals, 59,904 physical rows, 128 excluded padding rows,
and 27,997 correct registered proofs. MiniF2F records 3,915 correct modes and
123/244 solved at 128; registered validation records 6,529 modes and 154/223
solved. The source guard validated every hash and accounting invariant and
released retained job `868228`. Descriptively, C3 has 10,444 modes versus
C1's 8,468 (+23.3%) while producing 4.0% fewer correct proofs and solving two
more theorems, but equal-correct rarefaction and the registered comparative
claim remain withheld until C0 finalizes and the frozen joint analysis runs.
That D-093 gate is now complete. Eligible C0 retry-4 finalized with metrics
SHA-256 `300a466dc8307f4d45ddf51cc3b21265213d7cad6aa3340802de1d5515969471`
and passed the source guard, releasing job `870055`. The frozen pass@128
comparison and accumulation artifacts have SHA-256 values
`8fc154e23b5380230733f8422923b344f67bbe43d058ea43cf30f8ab12885855`
and `a0943606a80b0c8e6ec01b29191d36b26c70def3b88d1d495c5efaa2be9772f5`.
C3 produces 10,444 tactic modes versus C1's 8,468 (+23.3%) while solving
277 versus 275 theorem/split pairs. At exactly 16 correct draws C3 yields
10.1773 expected modes versus 8.9486 (+13.7%, paired p=1.79e-29); its relative
advantage grows to 17.1% at 32 draws and 20.4% at 64. C3 recovers 70.9% of C0
modes seen at least four times and absent from C1, and 82.1% at count floor
eight. The direction is positive across all six frozen syntactic proof
representations, but C3 remains below C0's 11,477 total modes. Independent
re-execution reproduced both artifacts exactly except timestamps, and all 54
focused tests pass. This establishes a deep syntactic-diversity result without
claiming semantic mathematical diversity.
The immediately prior request `868603` was cancelled before allocation and
without artifacts solely to bind the batch script to its own immutable runner
filename instead of a shared mutable path.
The subsequent request `868606` and dependent analysis `868631` were also
cancelled before allocation and without artifacts after a pre-start audit
found that the telemetry gate compared update-batch category counts with the
larger physical proposal total. The corrected gate compares those counters to
the update volume while the independent proof-level gate continues to validate
all physical blocked proposals.

The causal matched-control request `869225` retained its exact job ID,
immutable runner, pristine inputs, complete four-H100 shape, and 24-hour limit
while its scheduler billing association changed in place from `def-zhijing` to
the authorized, higher-fair-share `rrg-zhijing` account. Priority rose from
about 279,691 to 1,026,466 and Slurm allocated the unchanged job on `trig0044`
at 13:32:43 EDT. This begins the discriminating control needed to separate the
hard-exclusion intervention from optimizer-history effects. No control result
exists until all 604 steps finalize and the frozen training and held-out
analyses validate.
The D-091 step-20 gate admits the live control unchanged. Its first batch
matches excluded primary `868049` on all 40 non-timing fields, and through 20
steps it records 7,488 accepted/trained proofs, zero blocked proofs, and zero
skipped all-blocked prompts. Timed-step cost is 2,804.772 seconds, including a
402.726-second Lean tail. Adding the 266.340-second prefix excess over the
excluded primary to its frozen 23.36-hour projection gives 23.43 hours; a
uniform live-prefix estimate is 23.61 hours. An early exact-C3 ratio estimate
is pessimistic at 24.96 hours because it propagates the single timeout across
all remaining positions. With two positive estimators, healthy resources, and
the causal control intact, job `869225` continues to step 40.
At the D-095 step-40 gate, the control remains scientifically clean but runtime
estimators diverge. It records 14,304 accepted/trained proofs, zero blocked
proofs, and zero skipped prompts. Timed cost is 6,140.924 seconds versus
5,301.079 in the excluded primary and 4,768.814 in C3. Five verifier tails
above 250 seconds occur in the current prefix versus three in the excluded
primary; four newly positioned tails explain most of the 839.845-second excess.
Adding that excess to the frozen control schedule gives 23.59 hours, while
uniform and exact-C3-ratio projections are 25.84 and 25.52 hours. The run
continues unchanged to a predeclared step-80 stop gate: if the cumulative
exact-C3 projection remains outside 24 hours, replace the node using a pristine
restart without admitting partial science.

Before any eligible full C5 output exists, D-054 freezes the direct C5-versus-
C3 training analysis in `scripts/project/analyze_c5_training.py`. It requires
complete finalized runs and checks intervention-specific accounting before
reporting raw coverage, paired theorem deltas, equal-correct-draw rarefaction,
archived-dominant concentration, archive-eligibility strata, chronological
windows, and recovery of C0 modes absent from C3. Its material-support rule is
at least +5% mode coverage at 16 correct draws, at least a 0.05 reduction in
paired archived-dominant share, and no more than a five-point correctness-rate
loss. All 49 project tests pass, and the generalized finalized-run loader
reproduces the existing registered C1/C3 analysis exactly.
Dependent job `868700` will execute analysis snapshot `39ba50d` only after
Slurm observes job `868636` exiting successfully; otherwise it cannot produce
an analysis artifact. Its runner SHA-256 is
`5416e9f6dc8225fd06acd1e2f9f298b77611b73146fcc8fd03ac486241cba062`.
D-059 supersedes pending zero-runtime job `868637`: the corrected wrapper
publishes the registered repository `results/` path only after analysis and
terminal validation both succeed, so a failed validation cannot leave a
result-shaped partial artifact.

## Reproducibility record

- Model: `deepseek-ai/DeepSeek-Prover-V1.5-SFT`
- Model revision: `e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`
- C0 archive SHA-256:
  `fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3`
- Source dataset SHA-256:
  `56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb`
- Combined evaluation parquet SHA-256:
  `f9fb4d92b529499fa684f81a01a51249a2b9e1736cf50412ca374f11dbf4d840`
- Complete configurations, checkpoints, proofs, verifier traces, and hardware
  records are retained under shared cluster storage in `runs/`.
- Portable runtime: CPython 3.11.4, PyTorch 2.3.0 with CUDA 12.1, cuDNN
  8.9.2.26, NCCL 2.19.3, transformers 4.40.1, and vLLM 0.4.2.

Implementation and execution decisions are recorded chronologically in
`research/DECISIONS.md`.
