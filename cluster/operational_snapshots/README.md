# Operational snapshots and publication scope

September 20, 2026. These eight scripts are byte-identical copies of the
corresponding files under `/scratch/memoozd/rrl/`, checked with `cmp` before
publication. They preserve the actual C2/C5 training, evaluation, analysis,
and verifier-benchmark execution entry points used outside the repository.
They are historical snapshots, not instructions to resubmit expired jobs.
Some specify historical accounts; the scheduler's recorded account changes
are documented in PROJECT_STATE.md. Prefer def-zhijing for future work.

The active code branch is `work/dominant-mode-rejection`; the GitHub default
branch `dominant-mode-blocking` is intentionally not overwritten or merged
without reviewing its independent history. New commits use Memo Ozdincer's
GitHub-linked noreply identity. A .mailmap canonicalizes the older cluster
identity without changing pinned experiment commit hashes.

## Run evidence archive

The September 20 GitHub release `audit-2026-09-20` accompanies the code/report
checkpoint with `run-provenance.tar.gz` and `run-inventory.json`. The archive
contains eligible small text evidence from the repository's sibling `runs`
directory: metadata, logs, configs, metrics, and operational scripts. Selection
is explicit in `scripts/project/package_run_provenance.py`: permitted textual
extensions, at most 16 MiB per file, excluding actor/critic/buffer state.

Archive SHA-256:
`762f2dc04ab31c73b5419970edf8134defc7b8f573c436ca02707bcad255ac8d`.
Inventory SHA-256:
`6b0194d3e8778c8937b89d4e77342f4d714f733e138e75198c985827687b139b`.

The inventory marks every included/excluded regular file under `runs` at
packaging time and hashes included files. It does **not** back up excluded
files. In particular raw proposal JSONL, datasets, model checkpoints and
larger files remain local. The separate `models` directory and software
environments are outside that archive. The runs/models directories occupy
about 59/65 GiB respectively on disk; no claim is made that all of those
bytes are uploaded to GitHub. Credentials were not included. A pattern scan
found no common GitHub/OpenAI token or private-key markers in the selected
text categories; this is a bounded scan, not a guarantee of absence of secrets.

Future milestones must update the reports, inventory/publication record, and
reviewed Git commits. Do not present a draft, failed upload, or local-only
artifact as published: verify the remote commit and release assets.
