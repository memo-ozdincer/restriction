# November 18 recovery and GitHub migration audit

The user requested recovery of the latest work from unstable cluster storage,
including broken Codex sessions, and publication to GitHub so the project can
continue elsewhere. Large checkpoints were explicitly lower priority. This
operation preserves research state and does not resume GPU experimentation.

## Source recovery

The checkout and remote research branch initially agreed at `fe8e029`. Three
uncommitted files survived: the SSH login-shell fix, its regression tests, and
the historical one-shot execution-screen recovery launcher. They were reviewed,
credential-scanned, tested (eight tests), and pushed in `e5f6e39`.

Git object recovery found two unreachable historical blobs (old project state
and decisions), not a newer implementation. Both are included in the evidence
archive. Existing committed work includes the conditional training/evaluation
pipeline, procedure-replay and closed-contract instruments, transfer-panel
preparation, source research, and the proposal.

The latest main JSONL transcript survives. Numerous September/October session
paths recorded in the state database no longer exist. Read-only queries and
offline `.recover` on **copies** of damaged databases salvaged older records;
the recovered history database passes `quick_check`. Two log-backup SQL imports
report a reserved `sqlite_sequence` creation error, while their recovered user
tables are readable and pass `quick_check`. This is partial content salvage,
not a full repair of Codex or proof that every session was recovered.

Project-filtered extracts preserve 3,079 assistant messages and 461 patch
records. The surviving September recovery conversation is included separately.
October log metadata confirms repeated `failed to project durable rollout`
errors. Inter-agent messages in those logs are encrypted; no decryption was
attempted. The session inventory records found/missing transcripts, recovered
row counts, historical transcript hashes, and publication scope. Raw databases,
system/developer instructions, hidden reasoning, account metadata, and unrelated
projects remain outside the public backup.

## Corrected last-run status

The old project-state entry describing job 1176227 as pending was stale.
Accounting reports it started October 26 at 22:32:44 and ended October 27 at
22:32:46, with allocation state `TIMEOUT`. No job was active at this audit.

The initial launcher failed before creating output because its SSH environment
lacked `scontrol`. The manual login-shell recovery staged the verifier and
passed preflight, then failed the nonterminal-prefix gate: all 536 full
witnesses passed, but four prefixes were already complete. There were 1,072
physical Lean calls, zero model proposals, and zero new training updates. The
four invalid rows all belong to the training split. Neither practice nor
diagnostic generation output exists.

The failure, checksums, four row IDs, and recovery status are now recorded in
`results/execution_screen_20261026_recovered.json`. The proposed four-row panel
repair and v2 panel were **not found**. The handoff treats that repair as pending
work; it does not invent an implementation from a session intention.

## Evidence preservation

The release archives contain 1,524 files, 7,191,472,153 uncompressed bytes:

| Asset | Files | Compressed bytes |
|---|---:|---:|
| `research-evidence.tar.zst` | 1,442 | 221,502,856 |
| `large-proof-records.tar.zst` | 71 | 388,261,482 |
| `historical-supplement.tar.zst` | 11 | 811,896 |

Contents include run records across 100 run directories, raw proof logs,
historical failed runs, frozen panels and witnesses, C0 archive, external
operational scripts, environment locks, tokenizer/model metadata, and reviewed
session extracts. Code and the six tracked datasets remain in Git. A Git bundle
provides an additional source-history backup.

The checked-in `recovery/2026-11-18/evidence-inventory.json` gives each archived
path, source, size, modification time, SHA-256, asset, and explicit exclusions.
All three archive payloads were independently streamed and checked against that
inventory, including hard links, duplicate-member rejection, and path checks.
The supplement preserves nine ignored historical repository logs and two small
compiled contract artifacts needed for optional evidence readback tests.
The readback results are in `archive-verification.jsonl` alongside the inventory.

Known-token/private-key patterns were scanned before packing. Extracts were
limited to project material; raw account/session databases are excluded. This
does not represent an exhaustive credential-classification guarantee.

Model weights and installed runtime/toolchain trees are not backed up by these
archives. Omitted weight/compiled-file paths total 124,386,740,512 logical bytes;
hard links may duplicate physical data in that count. Their metadata does not
substitute for the missing payloads. The portable handoff identifies how to
reacquire the pristine base and what still requires cluster-to-cluster copying.

## Validation and continuation

The initial broad test attempt lacked the prover import path and failed to
import one module. With the recorded prover and repository on `PYTHONPATH`,
**197 tests ran successfully, with four optional compiled-evidence tests
skipped**. This recovery did not rebuild the environment or run GPU training.

`CONTINUE_ELSEWHERE.md` supplies download, checksum verification, clone/bundle
restore, dependency pins and local patches, environment checks, known portability
limits, and the precise next research step. Historical absolute paths and
manifests are preserved; relocation is not silently presented as identical
execution provenance.

GitHub's default branch remains `dominant-mode-blocking`; current work is on
`work/dominant-mode-rejection`. No force push or default-branch change is used.

## Publication and restore receipt

Published [recovery-2026-11-18](https://github.com/memo-ozdincer/restriction/releases/tag/recovery-2026-11-18)
from source commit `d4bafbdb3cc21c4fcbe431ddee50177125731504`.
All seven assets are public and total **624,548,497 compressed/download bytes**.
Their GitHub-reported sizes and SHA-256 digests match the local originals.
All assets were downloaded again to a separate directory, and the six payload
checks in `SHA256SUMS` passed. The checksum file itself was also checked against
its independently recorded digest. URLs and digests are tracked in
`recovery/2026-11-18/github-publication-receipt.json`.

A separate checkout was cloned from the full Git bundle. The contract-run
records and compiled evidence were restored from the verified archives.
**All 197 tests passed with zero skips in that restored checkout**, using the
existing pinned cluster Python/prover environment. This tests source and
artifact restoration, not a clean GPU-environment rebuild on another machine.
The test output is preserved in `restored-checkout-tests.txt`.

The branch additionally carries this publication receipt; the immutable release
bundle remains at the recorded source commit. Historical verifier whitespace is
preserved byte-for-byte and excluded from whitespace normalization using the
narrow `.gitattributes` rule.
