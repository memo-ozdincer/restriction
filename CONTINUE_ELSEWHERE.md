# Continue this project on another machine

Recovery date: **November 18, 2026**. The current research branch is
**`work/dominant-mode-rejection`**. GitHub's default branch is older; explicitly
select the research branch. Start with this file and `PROJECT_STATE.md`.

November 19 update: the interface-discovery pilot is complete with zero
downstream successes. Its later raw evidence is an additional archive, described
in `research/INTERFACE_DISCOVERY_RESULT_2026-11-19.md`; it is not contained in the
original recovery tarballs. Consult its publication receipt for the download.
The local-context follow-up also completed: two sampled successes, and an exact
GRPO proof continuation that verifies in both recurrence worlds. Its full
result and separate raw-evidence archive are described in
`research/INTERFACE_MATERIALIZATION_RESULT_2026-11-19.md`. Both small-run archives
are attached to the `interface-discovery-2026-11-19` release; bulk weights remain
excluded. Their own allocations were released after those experiments.

A subsequent cross-context-credit screen passed its reward-signal gate, but
its rewards mostly agree with preferring shorter proofs. Its complete result
is in `research/CROSS_CONTEXT_CREDIT_RESULT_2026-11-19.md`; the additional archive
includes the raw matrix and an isolated PEFT wheel/runtime fixture. Consult
`research/ADAPTER_RUNTIME_2026-11-19.md` before attempting adapter training.
The subsequent matched policy-update pilot has now trained four small adapters:
local correctness, cross-context credit, a length-matched reward control and
successful-proof replay, each with 40 optimizer steps. The full-root evaluation
and independent audit are complete: cross-context credit ties the length control,
and neither solves the original sixteen composition roots. See
`research/CROSS_CONTEXT_POLICY_UPDATE_RESULT_2026-11-19.md` and `PROJECT_STATE.md`.

## New policy-update adapters and exact training evidence

The [policy-update release](https://github.com/memo-ozdincer/restriction/releases/tag/policy-update-2026-11-19)
contains actual adapter weights, exact token/probability trajectories, Lean
rewards, training metrics, source snapshots and the failed first runtime attempt.
The training archive is 59,043,341 bytes; all 83 members were downloaded and
verified against their checksums. Its SHA-256 is
`10aa1cd65623c6296741e9415467570b59ee0e43a1432f184dfd7cae1a13c356`.
These files are additional to the November 18 recovery archive. The same release
also contains `policy-update-evaluation-20261119.tar.gz` and
`evaluation-inventory.json`, preserving all 3,200 sampled evaluation proofs,
698 full-source Lean judgments, analysis and independent audit. Extract that
archive into the same restored `restriction-rl` directory.

From the recovery directory after creating `restriction-rl`:

```bash
gh release download policy-update-2026-11-19 --repo memo-ozdincer/restriction \
  --pattern policy-update-training-20261119.tar.gz --pattern training-inventory.json
sha256sum policy-update-training-20261119.tar.gz
# Compare the checksum above before extracting into the restored bundle.
tar -xzf policy-update-training-20261119.tar.gz -C restriction-rl
```

The four final adapters are under
`runs/interface-discovery-workspace-20261118-1373310/policy-improvement/{local,cross,length,replay}/adapter`.
Use each adjacent `complete.json` and `reload-probes.json` to authenticate it.
These are final adapter weights, **not full model or optimizer-state checkpoints**.
Download the pinned pristine base separately. The repaired run uses float32
model computation with TF32 disabled, plus the isolated PEFT 0.10.0 wheel in
`archives/training-runtime-20261119`. The matching execution source is archived
under `runs/policy-update-launch-20261119-1373310/source.tar`, commit `87d64fe`.
The runner's `add_adapter` helper preserves float32 adapter parameters on reload;
do not merge them into a bfloat16 model and assume identical predictions.
The frozen panel/config is `runs/policy-improvement-panel-20261119-fp32`.

## Later causal repair evidence

The post-hoc state-scope repair closes 43 previously rejected invariant proofs
without altering their remaining bodies. All 172 omission controls reject.
It uses no new model sampling or training and does not pass its broader
training-feasibility gate. See `research/CAUSAL_STATE_REPAIR_RESULT_2026-11-19.md`.
The separate `causal-state-repair-2026-11-19` release contains the complete repair
and original-comparison evidence; its inventory and download receipt are tracked
under `research/experiments/causal_state_repair_20261119/`. Extract its archive
into the same restored `restriction-rl` bundle directory.

## Download the code and preserved evidence

The [November recovery release](https://github.com/memo-ozdincer/restriction/releases/tag/recovery-2026-11-18)
contains the actual archived files, not just an inventory. It complements the
repository's code, tests, research documents, results, and six tracked datasets.

On a Linux machine with Git, GitHub CLI, tar, and zstd:

```bash
mkdir restriction-recovery
cd restriction-recovery
gh release download recovery-2026-11-18 --repo memo-ozdincer/restriction
sha256sum -c SHA256SUMS
tar --zstd -xf research-evidence.tar.zst
tar --zstd -xf large-proof-records.tar.zst
# Clone before overlaying historical repository logs, so the target is empty.
git clone --branch work/dominant-mode-rejection \
  https://github.com/memo-ozdincer/restriction.git restriction-rl/repository
tar --zstd -xf historical-supplement.tar.zst
python3 restriction-rl/repository/scripts/transfer/verify_research_archive.py \
  evidence-inventory.json research-evidence.tar.zst large-proof-records.tar.zst \
  historical-supplement.tar.zst
```

The archives restore the `restriction-rl/runs`, `archives`, model metadata,
environment inventories, and historical workspace scripts. Session extracts
are under `recovered-session-evidence`. They include historical claims and
intermediate patches; **do not replay those patches automatically** over the
current source. A complete Git bundle is also provided as an independent source
history backup. If GitHub cloning is unavailable after downloading the bundle:

```bash
git clone --branch work/dominant-mode-rejection restriction-history.bundle \
  restriction-rl/repository
```

The bundle captures the release's source commit; later publication receipts can
exist on the branch. `git bundle verify restriction-history.bundle` can be run
inside the cloned repository. Keep downloaded archives until local verification
passes. Approximately 7.2 GB is needed for the uncompressed evidence, plus code
and any environment or models you subsequently install.

## What is and is not portable yet

This release is a **source and research-evidence backup**, not a complete
ready-to-run GPU environment. It contains 1,524 archived files, including all
selected raw proof records, the exact original execution/transfer panels, C0
archive, run configurations, failures, launch scripts, and model/tokenizer
metadata. Every included file has a size and SHA-256 in `evidence-inventory.json`.

Model weight files, installed Python/CUDA packages, most Lean build outputs and
toolchains, and runtime caches were left on the cluster. Their omission is
explicit in the inventory. Roughly 124.4 GB of weight/compiled-file paths are
listed as omitted; this is logical size and may count hard-linked data more
than once. **Metadata and hashes are not backups of those weights.**

To preserve trained C1/C2/C3 weights later, transfer the paths in the omission
inventory with resumable copying. They cannot be reconstructed from tokenizer
metadata or analysis reports. The pristine base can instead be downloaded from
`deepseek-ai/DeepSeek-Prover-V1.5-SFT`, pinned to
`e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`.

The older `scripts/transfer/README_TRANSFER.md` describes transferring a *full*
portable bundle. Its assertion that no downloads are needed does not apply to
this smaller GitHub recovery release. The archived August `MANIFEST.sha256`
describes that older full bundle; use the new evidence inventory for this release.

## Restore the research environment

The exact captured inventories and dependency patches are tracked under
`research/recovery/2026-11-18/`. Recreate a separate environment rather than
installing the repository's older upstream requirements uncritically:

| Component | Recorded version / revision |
|---|---|
| Python | 3.11.4 |
| PyTorch / CUDA runtime | 2.3.0 / 12.1 |
| Transformers / vLLM | 4.40.1 / 0.4.2 |
| DeepSeek prover source | `2c4ba9119eef74d0d611f494261b2c5bae98c69a` |
| Mathlib | `2f65ba7f1a9144b20c8e7358513548e317d26de1` |
| Lean | `leanprover/lean4:v4.9.0-rc1` |
| REPL | `c6199a81de2a7e16cb27d6f85f56cff7043cd27f` |

Use `requirements.lock.txt` and `requirements.installed.txt` from that directory,
including the recorded FlashAttention wheel, when rebuilding the Python stack.
The historical wheel and CUDA packages are platform-specific: a clean rebuild
on a different GPU/OS has **not** been validated by this recovery operation.
`dependency-provenance/git-revisions.json` pins all nine dependency checkouts;
the saved Mathlib manifest and patches preserve the local REPL resolution and
file-mode differences. Avoid an unpinned `lake update`.

After installing the pinned runtime and rebuilding the verifier, use your own
absolute paths (replace `/path/to/restriction-recovery` below):

```bash
export RRL_MIGRATION_ROOT=/path/to/restriction-recovery/restriction-rl
export RESTRICTION_VENV="$RRL_MIGRATION_ROOT/environment/venv"
export ELAN_HOME="$RRL_MIGRATION_ROOT/lean/elan"
export DEEPSEEK_PROVER_ROOT="$RRL_MIGRATION_ROOT/verifier/DeepSeek-Prover-V1.5"
export RESTRICTION_BASE_MODEL_PATH="$RRL_MIGRATION_ROOT/models/base"
export PATH="$ELAN_HOME/bin:$RESTRICTION_VENV/bin:$PATH"
export PYTHONPATH="$RRL_MIGRATION_ROOT/repository:$DEEPSEEK_PROVER_ROOT"
cd "$RRL_MIGRATION_ROOT/repository"
bash scripts/project/preflight.sh
python -m unittest discover -s tests
```

The four optional closed-contract evidence tests require
`PROCEDURE_CONTRACT_RUN` and the corresponding compiled `.olean` artifact.
The small historical supplement preserves these two contract artifacts; set
`PROCEDURE_CONTRACT_RUN="$RRL_MIGRATION_ROOT/runs/procedure-contract-check-20261026-d"`
to include the evidence readback tests. This reads saved results; it does not
claim the destination has successfully rebuilt Lean.
Verify the rebuilt Lean wrapper with positive/negative controls before any new
GPU experiment. The original acceptance rules must remain unchanged.

## Where research actually stopped

The October screen **never generated model proposals or trained a model**.
The original SSH launch failed because `scontrol` was missing from the remote
non-login PATH. The recovered login-shell fix passes its eight tests. A manual
recovery then ran 1,072 Lean checks: all 536 full witnesses passed, but four
training prefixes already solved their goals. Validation stopped before
sampling. Job 1176227 subsequently timed out on October 27; it is not live.

The exact failure is in `results/execution_screen_20261026_recovered.json` and
the archived `runs/execution-base-screen-20261026-1176227`. No repaired v2 panel
or implementation of `repair_execution_pilot_nonterminal.py` was recovered.

The next authorized research step, when research resumes, is to implement and
register a deterministic new panel version omitting only those four invalid
training-prefix rows, retaining all 256 training and 64 diagnostic theorem
identities. This was a proposed repair, **not completed work**. Authenticate the
new manifest, explicitly adapt counts/padding and downstream hard-coded pins,
then rerun witness checks and the base screen. Preserve every original artifact.
Only a valid screen passing its registered gate permits matched root/practice
training. The conditional training/evaluation code is already in Git.

Use `research/PARADIGM_PROGRAM_2026-10-26.md`,
`research/EXECUTION_TRAINING_PROTOCOL_2026-10-26.md`, and
`research/PROCEDURE_TRANSFER_DESIGN_2026-10-26.md` for the research objective,
gates, and limitations. No revolutionary training result has been established.

Historical launchers contain Trillium paths, job IDs, accounts, and nodes. Treat
them as provenance; prepare new destination-specific launch configurations and
record the changes before execution. Do not rewrite historical manifests to
make them appear native to the destination. Prefer `def-zhijing` where available
and keep the requested persistent Python keeper inside a valid Slurm allocation.

## Recovery limits

The surviving latest main transcript and older readable records yielded 3,079
assistant messages and 461 patch records in the public extracts. Several session
files are absent. Offline SQLite salvage recovered partial older project history;
October log backups confirm projection errors but do not supply missing plaintext
subagent transcripts. Two unreachable historical Git blobs were also preserved.
Raw account databases, unrelated conversations, credentials, and private prompts
were not published. The original Codex databases were not repaired or replaced.

See `research/RECOVERY_AUDIT_2026-11-18.md` and the session inventory for the
evidence and explicit gaps. This recovery launches no new experiment.

## Repaired prerequisite consumer evidence

The [repaired-library release](https://github.com/memo-ozdincer/restriction/releases/tag/repaired-library-2026-11-19)
adds all 768 proposals, 651 distinct Lean checks, dependency replays, execution
source and producer provenance. Download `repaired-library-20261119.tar.gz` and
`inventory.json`; all 40 members have passed downloaded checksum verification.
Archive SHA-256: `e1748b72f45ee5d4ea66a231d940314af0e1914976f79f657bf2475232dad999`.
Extract into the restored `restriction-rl` bundle. Run evidence is under
`runs/interface-discovery-workspace-20261118-1373856/repaired-library`; frozen
source is in `runs/repaired-library-launch-20261119-1373856/source.tar`.
The result is 27 nonzero proofs dependent on the repaired invariant, zero witness
proofs; the two-schema criterion fails. No training occurred. See
`research/REPAIRED_LIBRARY_RESULT_2026-11-19.md`.

## Typed procedure composition evidence

The [typed-composition release](https://github.com/memo-ozdincer/restriction/releases/tag/typed-composition-2026-11-19)
contains `typed-procedure-composition-20261119.tar.gz` and `inventory.json`.
All 33 members have passed downloaded checksum verification. Archive SHA-256:
`d5c9340b0412123a19185d14a32700755408c5f2b3a1fab9ac563d1e8d4e71a6`.
Extract into the same restored bundle. The initial runtime failure is under
`runs/typed-procedure-composition-20261119`; the corrected experiment is under
`runs/typed-procedure-composition-20261119-runtime-fixed`. Both are preserved.

Explicitly connected model components prove all four witness roots; fixed-depth
search finds none. The registered automatic-composition criterion fails.
No training or GPU allocation occurred. Use the result report and independent
audit, not just the four accepted proof examples, when continuing this work.

## Compiler-credit adapters and exact supervision

The [compiler-credit release](https://github.com/memo-ozdincer/restriction/releases/tag/compiler-credit-2026-11-19)
contains three actual 80-step adapters and all demonstration tokens/masks,
reference probes, training metrics, frozen source and panel validation. Download
`compiler-credit-training-20261119.tar.gz` and `training-inventory.json`.
The archive and all 50 members passed downloaded checksum verification. SHA-256:
`9bb43bb1de3f15d342e088878db0996160eab89fed1920da2dd24897b5aefd8e`.
Extract into the restored bundle. Adapters are under
`runs/interface-discovery-workspace-20261118-1374137/compiler-credit/{full,mapped,rotated}/adapter`.
Use pinned base weights and the PEFT 0.10.0 overlay described above. Optimizer
state is excluded; these are final adapter checkpoints. Evaluation evidence
is separate; check PROJECT_STATE.md for its current publication status.

The final evaluation is now archived and independently audited. See the
[November 23 recovery notes](research/recovery/2026-11-23/README.md) for archive
paths, checksum manifests, the unresolved verdict and recovery of partial runs.

## November 23 Pell construction training and interface sensitivity

The [Pell training release](https://github.com/memo-ozdincer/restriction/releases/tag/pell-training-2026-11-23)
preserves the expression and literal adapters, exact training tokens, 336 main
evaluation attempts and 64 crossed-interface attempts. Download both archives
and their inventories; extract them into the portable `restriction-rl` bundle.

- `pell-training-1399226.tar.gz`: 29,109,687 bytes, 54 verified members; SHA-256
  `2f3a98390bcb3fe87af48df1703b078bfb8f8e2e8531901dffa0fb9d279c3ff1`.
- `pell-names-1399296.tar.gz`: 231,393 bytes, 25 verified members; SHA-256
  `fc0ac5aaecf7330f35556bac5dba8a8b40242761372d6304e36e69e928035e05`.

The first run is under `runs/pell-training-20261123-1399226`; the crossed check
is under `runs/pell-names-20261123-1399296`. These adapters require the final C1
parent checkpoint (`models/c1-final`) and isolated PEFT 0.10.0, not the pristine
SFT parent used for the earlier compiler-credit adapters. Frozen execution code
is included in the second archive. Read the full training report for the
renaming, ordering and bare-equation limits; the headline transfer alone is
not evidence of a general learned solver. Both allocations have been released.

## November 23 bounded generator adapters and evidence

The [generator release](https://github.com/memo-ozdincer/restriction/releases/tag/pell-generator-2026-11-23) preserves both adapters, all
384 proposals, 280 unique Lean judgments, training records, source, and all three
authoring attempts. All 94 downloaded members match their hashes.
The registered generalization criterion failed; one longer execution on a familiar
discriminant succeeded. See `research/experiments/pell_generator_20261123/README.md`.

Download `pell-generator-1399388.tar.gz` and `inventory.json` from that release.
Archive SHA-256: `0629a525f9190582154ed8732dfa6d438cfa86af3cc712796ad998088a137232`.
Extract into the restored `restriction-rl` bundle. Adapters are at
`runs/pell-generator-20261123-1399388/{literal,expression}/adapter`. They require
the final C1 parent, whose complete file hashes are in the tracked model identity,
not the pristine SFT parent. Bulk parent weights and optimizer state are excluded.
Use float32 with TF32 disabled and PEFT 0.10.0 as in the frozen execution source.

## November 23 universal-constructor screen

The [universal-constructor release](https://github.com/memo-ozdincer/restriction/releases/tag/universal-constructor-2026-11-23) contains the complete
128-proposal screen, all verdicts and frozen execution. Both tasks scored 0/64;
no training followed the failed reward-support gate. All 40 downloaded members
were verified. Archive SHA-256:
`52aef0c3fa689d828ddfb7c6e55ce97d3cc3e3be5d84e5dc6f5ceb8202566f95`. Extract
`universal-constructor-1399519.tar.gz` into the restored bundle. No adapter was
trained; the unchanged C1 parent identity is tracked beside the result report.

## November 24 checked constructor feedback

The [feedback release](https://github.com/memo-ozdincer/restriction/releases/tag/constructor-feedback-2026-11-24) preserves all 96 new proposals,
prior responses used for selection, checked feedback, complete verdicts and frozen
execution. All six cells scored 0/16; no training followed. All 43 downloaded
archive members were verified. Archive SHA-256:
`f133dce91aff78e34325cad925a165f8dca1689fc3aa76ddc91c75b1a1d6b951`. Extract
`constructor-feedback-1399674.tar.gz` into the restored bundle. No adapter was
trained; the parent hashes match the preceding C1 universal-constructor screen.

## November 24 certificate-only diagnostic

The same [feedback release](https://github.com/memo-ozdincer/restriction/releases/tag/constructor-feedback-2026-11-24) includes the additional
`certificate-audit-20261124.tar.gz` and `certificate-inventory.json`. It preserves
the CPU replay of 224 saved proposals: 221 extracted functions are invalid and
three proposals remain unclassified. All 16 downloaded members verify, including
the original response banks. Archive SHA-256:
`370f34e876e943e33be1e3973657556596cbcceb4dd82fcbbca2f75d21c15c9d`. Extract into the restored bundle.
See `research/experiments/constructor_certificates_20261124/README.md` for scope,
checks and timing. No GPU or model update was used for this diagnostic.

## November 24 hindsight learning adapters

The [hindsight-contracts release](https://github.com/memo-ozdincer/restriction/releases/tag/hindsight-contracts-2026-11-24) contains both actual
adapters, exact training records, all 384 evaluation proposals, verified hindsight
mining, source and allocation evidence. All 101 downloaded members match their
hashes. Archive SHA-256:
`da2afea37ea8e9e5ec1f0d2f03e726833acdbaee4e5bbf47b9d6563809df96aa`. Download
`hindsight-contracts-1399987.tar.gz` and its `inventory.json`, verify, then extract
into the restored bundle. The adapters are at
`runs/hindsight-training-20261124-1399987/experiment/{replay,contrast}/adapter`.

Use the final C1 parent, whose hashes are recorded in the experiment directory,
with float32, TF32 disabled and PEFT 0.10.0. Parent weights and optimizer state
are excluded. Replay reaches 16/16 on the relabeled training law; contrast reaches
3/16 on its scaled variant but solves none of the original-sign targets. Both
registered comparative criteria fail. See the complete result before continuing.

## November 24 verified contract transport

The same [hindsight-contracts release](https://github.com/memo-ozdincer/restriction/releases/tag/hindsight-contracts-2026-11-24) now includes
`contract-transport-20261124.tar.gz` and `transport-inventory.json`. All 35
freshly downloaded members verify. Archive SHA-256:
`8a59f219a27d94e54a4bc33e62700400a99dbc83299917d90ed055e6303756a2`.
Extract into the restored bundle to recover both complete attempts, frozen
execution sources, all verdicts and the original source-program provenance.
The final compiler constructs 8/8 executable wrappers and 8/8 abstract-contract
proofs; the first attempt's unfinished proof is preserved. This is CPU compiler
construction on inspected specifications, with no new model success or adapter.
See `research/experiments/contract_transport_20261124/README.md` before extending
this into a learning experiment. Existing C1/hindsight adapters remain in their
separate documented release archives; bulk model weights remain excluded.

## November 24 contract-closure learning adapters

The [contract-closure release](https://github.com/memo-ozdincer/restriction/releases/tag/contract-closure-2026-11-24) preserves all three actual
adapters, 640 proposals, 453 unique evaluation judgments, source, exact training
records and source-program dependencies. All 131 freshly downloaded files verify.
Download `contract-closure-1400174.tar.gz` and `inventory.json`, check hashes, then
extract into the restored bundle. Archive SHA-256:
`67ca48159ef43383af2609b166f4cbe552c2861dd7b526fb7ce6a47c2a5c1c1d`.

Adapters are at
`runs/contract-closure-20261124-1400174/experiment/{hindsight,executable,transport}/adapter`.
Use the recorded final C1 parent with float32, TF32 disabled and PEFT 0.10.0.
Bulk parent weights and optimizer states remain excluded. The two novel accepted
examples are a quartic wrapper and a renamed arbitrary-function constructor,
each 1/16. Both registered gates fail. Two hindsight verifier timeouts remain
unresolved; do not read the successful integrity audit as resolving those proofs.
See `research/experiments/contract_closure_20261124/README.md` for the full results
and limitations. The H100 allocation has been released.
