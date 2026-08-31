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

Restriction-RL recovered 43.3% of base-policy tactic signatures observed at
least twice but absent from the standard-GRPO sample. Recovery reached 58.8%
for signatures observed at least four times in the base distribution.

Machine-readable results are in:

- `results/registered_c0_c1_c3_seed42.json`
- `results/theorem_selection_c1_vs_c3_seed42.json`
- `results/training_dynamics_c1_vs_c3_seed42.json`
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
- Destination job `868001` is queued under `def-zhijing` for one exclusive,
  23-hour, four-H100 `compute_full_node` allocation. It runs the frozen
  `d031de7` C0/C1/C3 pass@128 payloads sequentially, finalizes and validates
  each condition before continuing, and then retains the allocation with
  `sleep infinity` for inspection and justified follow-up work.
- D-038 freezes the pass@128 accumulation, correct-draw rarefaction,
  concentration, suppression/recovery, and proof-representation sensitivity
  panel before any destination pass@128 result exists. The implementation
  reproduces the finalized pass@32 metrics and registered paired test exactly.
- D-039 registers the full seed-42 C3-matched no-blocking control needed to
  isolate blocking from C1/C3 optimizer differences. Its launcher is tested to
  match every non-blocking C3 trainer argument and has not yet produced data.
- The completed evaluations will determine whether to run the registered
  StableTopBlock-Restart experiment next.

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
