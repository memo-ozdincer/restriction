# Project State

Last updated: 2026-08-31

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
- D-042 records the destination memory adaptation: `compute_full_node` grants
  the complete 770,000-MiB physical node, which is the largest available on
  this cluster rather than the source cluster's 1-TB request. Jobs `868001`,
  `868049`, and `868076` each request all 770,000 MiB, 96 CPUs, and four H100s;
  memory use and OOM state must be monitored and any incomplete run remains
  excluded. D-047 supersedes the unsafe 64-worker destination setting with the
  targeted 32-worker replay.
- D-038 freezes the pass@128 accumulation, correct-draw rarefaction,
  concentration, suppression/recovery, and proof-representation sensitivity
  panel before any destination pass@128 result exists. The implementation
  reproduces the finalized pass@32 metrics and registered paired test exactly.
  D-043 materializes that pass@32 baseline as a checksummed result before the
  pending pass@128 payload starts.
- D-039 registers the full seed-42 C3-matched no-blocking control needed to
  isolate blocking from C1/C3 optimizer differences. Its launcher is tested to
  match every non-blocking C3 trainer argument. Destination job `868049` is
  queued for a separate 23-hour four-H100 full-node allocation from commit
  `4d435f2`; it has not yet produced data. D-046 supersedes only its
  operational runner hash with
  `7df38267a19e690bb288edb0e395b158988272f84941f62c92c4e2fb79f5b9a3`
  to add the complete native-runtime check. D-047 additionally requires the
  shared 32-worker verifier setting; its frozen scientific payload is
  unchanged.
- D-040 freezes the paired training, correct-draw rarefaction, concentration,
  C0-recovery, and archive-eligibility analysis before control data exists.
  Its end-to-end surrogate validation reproduces the existing C1/C3 artifact.
- D-044 hardens the registered analyzers before either destination job starts.
  Training and evaluation inputs must now reproduce finalized condition,
  classification, completion, proposal, padding, parquet, and proof-log hash
  invariants; the matched control must additionally have zero intervention
  counters and no archive. All 36 project tests pass, and the stricter loaders
  reproduce the completed training and pass@32 findings exactly.
- D-041 freezes the matched C3-versus-control held-out accumulation,
  rarefaction, theorem-selection, concentration, and representation panel.
  Evaluation preparation/finalization now accepts the control as a distinct
  no-update condition; no matched held-out data exists yet. A fail-closed
  attached evaluator is ready to reuse job `868049` only after its training
  metrics and final checkpoint exist; its operational runner SHA-256 is
  `81361510a6f5776b8c15cd239ef4f53145a32ceff3d26fbd8d72d0eaef4b32ee`.
- The completed control and evaluations will determine whether the smallest
  decisive follow-up is replication, mechanism diagnosis, the registered
  StableTopBlock-Restart ablation, or a workload with richer proof variation.

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
