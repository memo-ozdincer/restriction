# November 23 recovery

Job 1374137 completed three 80-step adapter runs and all 2,816 planned proposals. The independent audit checked exact tokens, adapter hashes, reload probes and all 1,336 distinct verifier records. One mapped proposal on fresh_06_nonzero remains unresolved. Full likelihood led on composition, and the registered source-map advantage failed. Retention counts were base 197/320, full 188/320, mapped 193/320 and rotated 195/320. The scheduler records cancellation after the driver requested release. The batch step exited successfully.

The [compiler-credit release](https://github.com/memo-ozdincer/restriction/releases/tag/compiler-credit-2026-11-19) contains three complementary archives.

- Extract the training and evaluation archives at the portable bundle root. Together they preserve the frozen inputs, adapters, raw proposals, verifier matrix, audit, driver output and accounting.
- Extract november-workspaces-and-launcher-delta.tar.gz at the parent of the portable bundle. It preserves all regular files under the 26 November run directories, including initial failed attempts, partial workspaces, retries, keeper events and launcher snapshots. It also contains top-level workspace files absent from or changed since the November 18 inventory.
- SHA256SUMS covers the two new downloaded archives. Their 24 and 811 members respectively were rehashed against evaluation-inventory.json and workspace-sha256.json. The training archive readback is documented in CONTINUE_ELSEWHERE.md.

The [November 18 recovery audit](../../RECOVERY_AUDIT_2026-11-18.md) documents earlier interrupted jobs, surviving evidence, missing artifacts and bulk-checkpoint exclusions. The [original protocol](../../COMPILER_CREDIT_2026-11-19.md) defines the evaluation criteria. This recovery used the existing outputs without resampling.
