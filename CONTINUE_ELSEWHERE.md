# Continue this project on another machine

Recovery date: **November 18, 2026**. The current research branch is
**`work/dominant-mode-rejection`**. GitHub's default branch is older; explicitly
select the research branch. Start with this file and `PROJECT_STATE.md`.

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
