# Conditional execution training: prospective protocol

Status: implemented and CPU-tested; no training panel has been prepared from real
outcomes and no training has been launched. This implements the conditional
comparison in `PARADIGM_PROGRAM_2026-10-26.md`. The queued base screen remains on
its immutable `57b2d3013e6888dee4a4ad7520252ae4c47791e2` snapshot. Live trainer
changes described below apply only to a later, separately reviewed training
snapshot.

## Hypothesis and decision

Practice from short, verified, nonterminal proof starts can improve execution of
partially competent procedures. At equal fresh proposal budgets, a model trained
with reserved prefix practice should outperform root-only training on the fixed,
disjoint diagnostic prefixes. Root evaluation after removing the supplied starts
separately tests transfer. A conditional gain alone supports repair under supplied
starts; it does not establish autonomous transfer or a general training paradigm.

The material-effect screen remains a ten-percentage-point improvement over the
root arm in theorem-balanced diagnostic prefix correctness, with no more than a
two-point decline in diagnostic root correctness. Do not choose further runs,
alter budgets, or soften thresholds automatically from unspecified outcomes.
Replay and curriculum comparators remain contingent research decisions.

## Preconditions and authenticated inputs

`scripts/project/prepare_execution_training.py` performs CPU preparation only.
It requires the exact frozen panel manifest SHA-256
`c5513992dc40cda4f62896c2b53b5c4509f2d5934b245b2477da71b2a17fc0b8`, the existing
base-screen output directory, and its immutable source snapshot. It rejects a
failed or incomplete screen before creating a training directory.

Preparation rechecks the pinned source tree, panel files, original dataset/C0
source hashes, exact archived witnesses, tokenizer/configuration hashes, and
screen runtime certificates. Recorded model shards must be the two pinned base
shards; training independently rehashes those complete shards before launch.
Preparation verifies the recorded account/job/node/cgroup identity, commands,
runtime parquet copies, complete proof-log hashes, process completion,
six-hour screen envelope, and every fresh witness/nonterminal check. It does not
accept the `advance` flag by itself. It recomputes the complete screen analysis
from the authenticated raw logs and requires exact equality with the saved
analysis, followed by `gate.advance == true`.

The original verifier Python source has SHA-256
`ec9c2e9b5dae10634fd2661ca3ee7fb589b11d04cb471a47104c6eb9eea52532`.
Applying the already-audited result-handoff and lake-path patches yields
`d452842a8816e19f60c79a4cf4b7ddfa4fd026c44cd8e9e3d946bd3405a3f573`.
The gate checks these fixed source/staged hashes, the pinned patch hashes, and
the bundle's Lean toolchain. These are operational patches already used by the
screen; no correctness rule changes.

## Frozen selection and matched exposure

Only practice prefixes with **1–8 correct continuations out of 16** are eligible.
The original requirement of at least 48 eligible theorem identities and four
first-head strata with at least eight eligible theorems each is independently
rechecked. Diagnostics never rank or select training rows. No diagnostic theorem
appears in either training parquet or the trainer's validation-file input.

Allocate exactly 512 prefix slots across all eligible practice theorem IDs:

1. Hash-order theorem IDs using seed 42 and the `theorem` namespace. Each gets
   `floor(512/N)` slots; the first `512 mod N` get one additional slot.
2. Within each theorem, hash-order its eligible source row IDs using seed 42 and
   the `route` namespace. Distribute that theorem's slots cyclically over those
   routes, so route quotas differ by at most one.
3. Hash-order the resulting `(theorem, route, repeat)` pairs using the
   `pair-order` namespace. For each pair, emit two aligned rows in both arms.
   The practice arm receives root then prefix. The root arm receives root then
   root, with exactly the same theorem at both positions.

Hashes use the existing `rank(seed, *parts)` helper and JSON encoding. The
materialized JSONL/parquet rows, source row IDs, route assignments, quotas, and
file hashes are frozen in a fresh training-panel directory. Every repeated slot
has its own `pilot_row_id`; `source_pilot_row_id` identifies the original frozen
root or prefix, and `matched_route_id` preserves the pairing. Repeated slots are
fresh rollouts, never reuse of sampled responses.

| Quantity | Root arm | Practice arm |
| --- | ---: | ---: |
| Root rollout tasks | 1,024 | 512 |
| Prefix rollout tasks | 0 | 512 |
| Fresh proposals per task | 32 | 32 |
| Total fresh proposals | 32,768 | 32,768 |
| Batches of 16 tasks | 64 | 64 |

The same seeded DataLoader shuffle acts on the same theorem row order, preserving
theorem matching at every rollout position. Half-prefix allocation is a total
quota; individual shuffled batches need not be half prefix. Training permits no
padding. The runtime loader reauthenticates the screen and independently rebuilds
the full schedule before accepting either parquet, including nested fields.

## Shared training configuration

Both arms initialize actor and frozen reference from pristine
DeepSeek-Prover-V1.5-SFT revision
`e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`. Neither arm initializes from the screen,
another training arm, or any learned checkpoint.

The command fixes learning rate `1e-6`, weight decay `0.01`, zero warmup steps,
PPO epochs `2`, KL coefficient `0.10`, rank penalty `0.25`, PPO minibatch size
`256`, actor microbatch size `8` per GPU, binary Lean correctness, within-task
GRPO normalization, and advantage-threshold admission enabled. Hard blocking and
rejection sampling are disabled. Temperature/top-p are `1`, top-k is disabled,
prompt and generated-suffix limits are `512` tokens, and both arms use four GPUs,
tensor parallelism `2`, rollout memory fraction `0.5`, and seed `42`.

The existing proof-prefix path supplies prefixes as prompt context and verifies
the assembled proof. Only generated suffix tokens enter the PPO action/loss
tensors. The experiment changes the initial-state distribution, with consequent
changes in input information, generated suffix length, admission, and available
learning signal. Those are mediated effects and reported costs.

Both training arms use 64 Lean workers and the same 32 GiB verifier-memory cap.
This worker count differs from the sample-only screen's 32 workers. The October 4
actor-loaded run established memory feasibility for 64 workers but did not
establish a throughput improvement. No throughput advantage is assumed here.

Admission and dynamic buffering preserve C2 behavior. Groups without useful
within-task advantage are skipped. Buffered admitted groups update once the
existing 256-response threshold is reached. The existing final-step sentinel
can leave fewer than 256 admitted responses in the buffer; those are reported
as `residual_buffer_rows`, not counted as optimized responses or silently
flushed through a changed update rule.

## Execution and bounded lifetime

`scripts/project/run_execution_training.py` runs exactly one explicitly selected
arm per manual invocation. It neither submits a job nor waits for an allocation,
chains arms, performs evaluation, retries, or resumes. Invoke it by SSH on the
assigned node of existing job `1176227`, from a reviewed immutable git-archive
snapshot containing the new implementation. The allocation must still be
`RUNNING`, account `def-zhijing`, with this process in the exact job cgroup and
on its assigned node. Source files, panel/source certificates, full pristine
base weights, and node preflight must all pass before training starts.

The first arm requires at least twelve hours plus a fifteen-minute allocation
margin; the second requires at least six hours plus that margin. The allocation
deadline is checked again immediately before launching the trainer. Each arm's
preflight/staging/training/cleanup envelope is at most six hours, with process
group termination grace reserved inside that envelope. Final CPU-only artifact
authentication follows model execution and reports hashes. A shared
`.execution-training-1176227.active.json` lock prevents concurrent arm launch
through this runner. An existing arm directory is never reused. A second arm
requires a complete first-arm certificate from the same panel and source commit.

The manual preparation interface is:

```text
python scripts/project/prepare_execution_training.py
  --bundle /absolute/bundle
  --panel /absolute/frozen-panel
  --screen-run /absolute/completed-screen
  --screen-source /absolute/pinned-screen-snapshot
  --output /absolute/new-training-panel
```

The allocated-node interface, separately for each arm, is:

```text
python /absolute/reviewed-snapshot/scripts/project/run_execution_training.py
  --bundle /absolute/bundle
  --training-panel /absolute/authenticated-training-panel
  --training-sha256 FULL_MANIFEST_SHA256
  --output /absolute/bundle/runs/new-comparison
  --arm root
  --job-id 1176227
  --commit FULL_REVIEWED_TRAINING_COMMIT
```

Use `--arm practice` only in the separate manual invocation. These are interfaces,
not evidence that either command has been executed. A stale lock or ambiguous
transport outcome requires inspection of durable process and artifact evidence;
there is no automatic relaunch.

## Persistence, optimizer accounting, and evaluation eligibility

Save cumulative proofs every rollout step. Save actor checkpoints at steps 16,
32, 48, and 64, retaining the latest two actor checkpoints (`save_limit=2`). The
unchanged proof cleanup logic leaves the per-step JSONL snapshots available.
Always retain partial proofs/logs and the actual return code on failure. The
historical `Exception: Stop` sentinel is accepted only together with the finish
marker, all expected artifacts, exact fresh proposal counts, and complete runtime
accounting.

The new `EXECUTION_TRAINING_TELEMETRY` environment variable enables explicit
observational calls in the live trainer and actor. It does not replace an
optimizer, alter gradients/admission, or install a startup hook. It records the
resolved runtime configuration and environment, each rollout/admission count,
each actor update, each completed optimizer-step decision, and checkpoint-save
completion. Per-worker files are flushed and fsynced. The applied count increments
only after the actual `actor_optimizer.step()` returns; finite/gradient-threshold
skips remain unchanged. All four ranks must agree on applied/skipped steps.
Synchronized optimizer steps count once, not once per GPU. Response token exposure
sums across ranks; applied minibatch exposure includes repeated PPO epochs.

`ARM/training_complete.json` is written only when all of the following hold:

- All 64 fresh rollout batches and 32,768 unique proposals are present, with
  exact frozen theorem/prefix metadata and no padding or diagnostic leakage.
- Every proposal's runtime identity matches the authenticated resolved config,
  fixed command, and source/model/verifier environment.
- Complete telemetry attests at least one actual synchronized optimizer update,
  admitted/skipped groups, applied/skipped optimizer steps, response token
  exposure, residual buffer, and a completed final checkpoint save.
- `artifacts/actor/global_step_64` contains a complete HF actor checkpoint:
  shard indexes, tensor names/shapes, offsets/payload lengths, compatible dtype,
  model configuration, and tokenizer semantics match the pristine-base runtime.
  All checkpoint files receive hashes. Tokenizer comparison uses a fresh offline
  base tokenizer normalized through the unchanged loader/save path; ordinary HF
  serialization changes are not misclassified as tokenizer changes.

The certificate includes `evaluation_eligible=true`, source/panel/command hashes,
the final proof hash, `checkpoint_manifest`, and complete `telemetry`. Failed or
timed-out arms receive no eligible certificate. A smaller completed step, an
actor/lr metric, or a checkpoint-directory name alone cannot establish training.
These HF checkpoints contain actor weights/tokenizer rather than full optimizer,
sampler, and RNG state. No exact-resume claim is made.

The later diagnostic evaluation must authenticate these certificates and use only
the final step-64 actor from each arm, on the original common diagnostic tasks at
32 attempts each. Report conditional execution and root transfer separately;
do not use the resulting diagnostics to change this training panel.

The implemented allocated-node evaluator is
`scripts/project/run_execution_diagnostic.py`:

```text
python /absolute/reviewed-snapshot/scripts/project/run_execution_diagnostic.py
  --bundle /absolute/bundle
  --training-panel /absolute/authenticated-training-panel
  --training-sha256 FULL_MANIFEST_SHA256
  --training-run /absolute/comparison/root
  --output /absolute/bundle/runs/new-root-diagnostic
  --arm root
  --job-id 1176227
  --commit FULL_REVIEWED_TRAINING_COMMIT
```

Repeat with the corresponding practice paths and arm. The evaluator recomputes
the complete training certificate without rewriting it, authenticates the actual
checkpoint bytes, and rechecks them after evaluation. It shares the training
allocation lock and permits no overlapping model process through these runners.
The three-hour envelope includes source/data authentication, staging, inference,
verification, and finalization. It uses the base screen's sample-only settings,
including 32 verifier workers. Exact accounting requires all 168 rows and 5,376
proposals, with no padding. Runtime telemetry must attest zero actor updates.
The resulting `evaluation_complete.json` links the model, training certificate,
commands, inputs, proofs, runtime, and analysis hashes.

After authenticating both evaluation certificates, compare their final
`artifacts/proofs/global_step_11.jsonl` logs and the base screen's diagnostic log
with `scripts/project/compare_execution_diagnostics.py`. It applies the fixed
10-point conditional-gain / 2-point root-loss screen and reports paired
theorem-bootstrap intervals (seed 20261026, 10,000 draws). The intervals resample
theorems together with all their prefixes; they do not estimate training-seed
uncertainty. The comparison script authenticates scientific records and frozen
tasks, but deliberately does not infer model identity from a registered model
revision. The linked execution certificates are required separately. A material
conditional effect with flat root performance supports supplied-start execution
repair only; broader transfer requires the separately frozen composition tests.

## CPU validation

Tests prepare and revalidate a synthetic passing screen end to end. They cover
failed/recomputed/forged gates, corruption of source logs/runtime certificates/
commands/witness checks/parquets, deterministic balanced quotas, unique slot IDs,
exact per-theorem and per-position matching, diagnostic-outcome invariance,
32,768-proposal completeness, allocation deadlines, actual optimizer skip
boundaries, incomplete or inconsistent worker telemetry, and incomplete/changed
checkpoint tensors and tokenizers. Existing screen/waiter tests remain unchanged.
No synthetic fixture is a Lean result or evidence for the research hypothesis.

The final combined project check passed 179 tests. Historical C1/C3 checkpoint
configuration files were also inspected: their differences from the base are
exactly the allowed serialization fields (dtype, Transformers version, original
model path), supporting the checkpoint validator's normalization boundary.
