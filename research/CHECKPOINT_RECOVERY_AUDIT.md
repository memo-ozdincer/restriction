# C5 recovery audit and acceptance gates

September 20, 2026. Read-only source audit; no new training, changed runner,
checkpoint implementation, or recovery validation is claimed.

Inspected revision: `3c135a70fe602b1549bc9186f87fbd4ec4ef1553`.
The four source files below have no diff against C5's frozen training revision
`a0f1235a97ba4e92b25c53c959c7a942e63ee82c`.

## Findings

| Source | Observed behavior | Consequence for recovery |
|---|---|---|
| `verl/workers/fsdp_workers.py`, `ActorRolloutRefWorker.save_checkpoint` | Exports full actor weights and tokenizer; no optimizer, scheduler or RNG serialization in this method | Weight reload is not full training-state recovery |
| `verl/trainer/ppo/ray_trainer.py`, `_find_latest_checkpoint` | Chooses the largest step-numbered actor directory, without a completion manifest | A directory created by an interrupted save is eligible for selection; loading may then fail |
| `verl/trainer/ppo/ray_lean_trainer.py`, `_save_checkpoint` and `fit` | Actor export, buffer save and proof save are separate operations; actor retention cleanup precedes buffer save | A crash can leave components from different completed save stages; there is no cross-component commit boundary here |
| Same file, `_load_train_batch_buffer` | A missing buffer file becomes an empty buffer; empty buffers are not written by the saver | Absence does not distinguish legitimately empty state from lost state |
| Same file, `_create_dataloader` and `fit` | Recreates a seeded shuffled loader, iterates from the beginning and skips through `resumed_step` | This is replay-based cursor reconstruction, not serialized loader state; actual theorem order must be tested |
| Same file, proof reload | Missing proof snapshot prints a message and continues | Training metrics and proposal accounting can be incomplete despite a loadable actor |
| `verl/workers/sharding_manager/fsdp_vllm.py`, constructor and context manager | Keeps separate `torch_random_states` and `gen_random_states`, swapping CUDA RNG state around generation | Restoring only the currently active CUDA RNG misses explicitly stored generation state |

These are source-level hazards, not evidence that they caused the last timeout.
That run saved no checkpoint. Other backend state may matter too: this audit
does not establish an exhaustive vLLM serialization recipe.

## Proposed minimal recovery contract — not implemented

Scope a first implementation to the registered C5 GRPO configuration and fixed
distributed topology, not every upstream trainer mode. Preserve the scientific
configuration and fresh-base initialization. A continuation must be linked to
its own verified pristine-base run, not bypass the base-restart safeguard for
arbitrary weights.

1. Save only at a defined completed-step boundary, after all actor updates and
   verification for that step. Record completed step, next theorem-batch cursor,
   epoch, optimizer-update count, and total registered training budget.
2. Persist actor and optimizer state in a supported, mutually compatible FSDP
   format, scheduler state, and relevant RNG state per process/rank, including
   the sharding manager's stored generation stream. Identify and test any
   backend sampling state rather than assuming global seeds suffice.
3. Save buffer contents or an explicit empty-buffer marker, plus durable proof
   accounting through exactly the same boundary. Tie all artifacts to one
   checkpoint ID. Keep identifiers/counters sufficient to detect duplicate or
   missing proposals when continuing.
4. Include source/config/dataset/archive/base-model provenance and topology in
   a manifest. Write into a new staging location and publish a completion marker
   only after all required components and their checksums are durable. Readers
   must reject incomplete or incompatible bundles. Retain the previous complete
   checkpoint until the replacement is committed; do not clean up based only on
   directory step numbers.
5. Restore state before the next random draw, rollout or optimizer update.
   Validate theorem order reconstruction, including epoch transitions. Do not
   reduce remaining steps, alter timeouts or change the reward to fit wall time.

## Tests required before trusting a resumed full run

- **Crash consistency:** interrupt after each save stage; select the last complete
  bundle, never a partial newer directory. Corrupt or remove individual required
  files and verify explicit rejection. Distinguish missing from empty buffers.
- **State round trip:** compare optimizer tensors, scheduler counters, RNG state,
  buffer tensors and proof/step accounting before save and after fresh-process
  restore. Test fixed world-size/rank mapping and incompatible-manifest refusal.
- **Trajectory split:** with the actual distributed actor and rollout backend,
  compare an uninterrupted short run to the same run stopped at a checkpoint
  and resumed. Include a boundary with nonempty accumulated data if the recipe
  permits it, and one following an actor update. Compare next theorem IDs,
  generated tokens, verifier outcomes, rewards/advantages, update counts and
  resulting model/optimizer state. An uninterrupted repeat establishes any
  backend nondeterminism floor; do not silently call approximate agreement exact.
- **Failure accounting:** wall-clock verifier failures can differ even with the
  same tokens. Record these separately from RNG/state divergence; neither can
  be ignored when asserting equivalence.
- **Runtime feasibility:** measure full save/restore overhead and peak memory
  with the actor loaded; budget checkpoint overhead and shutdown margin. The
  pending model-free verifier benchmark cannot satisfy this gate.

CPU unit tests can cover manifest and accounting logic; they cannot substitute
for the distributed trajectory and memory checks. Passing a short test supports
the tested configuration only, not universal bitwise reproducibility.

## Decision

Saving weights more frequently alone is insufficient as a recovery plan. It can preserve
partial weights for inspection, but those must not be presented as an eligible
completed C5 result or exact continuation. The current benchmark remains the
approved 32/64-worker diagnostic. No new full-run submission is authorized by
this document. Implementation and a bounded model-loaded recovery/feasibility
test should be scoped explicitly before another full training attempt.
