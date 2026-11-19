# Interface discovery: completed null result

Audited November 19; model execution completed November 18, 2026. Neither
cached 7B model solved a downstream target in this experiment. Supplying the
correct quadratic invariant did not unlock a proof. This instrument therefore
does not yet establish the consumer capability needed to test useful discovery.
It provides no positive evidence for a new training paradigm.

| Consumer | Bare | Authored invariant | Irrelevant lemma | Selected model lemmas |
|---|---:|---:|---:|---:|
| Base SFT | 0/512 | 0/128 | 0/128 | 0/256 |
| C1 GRPO | 0/512 | 0/128 | 0/128 | 0/256 |

Each bare cell comprises four separate 0/128 targets. Each oracle/control cell
comprises four separate 0/32 targets. Each selected-artifact/target cell is
0/16; eight artifacts were crossed with both consumers and both targets in
their respective worlds. The complete matrix, completion-text multiplicities,
token counts, parser rejections, and source hashes are in
`experiments/interface_discovery_20261118/completed/independent-audit.json`.

There were 2,048 downstream proposals: 2,028 physical Lean checks and 20 lexical
parser rejections. No verdict was missing, and no verifier system error or
timeout occurred. All 1,024 bare proposals reached Lean. The finite 0/128
results do not establish impossibility. Original and continuation tasks,
prompts, sample identities, exact checked source hashes, and all accepted
axiom audits passed the independent request/source audit.

The original 64 producer samples were reused without resampling. After the
documented parser repair, 2/32 base and 7/32 GRPO proposals were valid. First-four
selection retained eight, predominantly tautologies plus a recurrence
restatement. No selected artifact met the prospective strong-result criterion.
Across producers and consumers there were 2,112 distinct proposals, 105,279
generated tokens and 370,496 supplied tokens, counting repeated supplied context
per sample. The corrected producer checks plus downstream checks total 2,090
physical Lean calls; the original superseded producer verdicts add 21 calls.
Authored validation and diagnostic checks are additional and preserved separately.

The H100 driver completed in 1,395 seconds. Its keeper allocation 1360929 lasted
1h00m06s and ended TIMEOUT, releasing the GPU. Original H200 allocation 1359079
lasted 31m39s before cancellation. Charge both full retained allocations, including
idle time, rather than only generation time. No new model training occurred.

The base model sometimes referenced the invariant but chose incorrect Bezout
coefficients; other completions ignored the lemma. This motivates the separately
registered local-context probe in `INTERFACE_MATERIALIZATION_PROBE_2026-11-18.md`.
Six actual Lean checks validated its invocation prefix and negative controls.
Its attempted November 18 launch refused to start because fewer than eight
minutes remained. **It generated zero proposals.** The failed launch is not a
scientific null result and must not be counted as a completed follow-up.

All raw completions, both original/repaired producer verdicts, consumer verdicts,
source snapshots, validation failures, panel files, launch logs and model hashes
are preserved in `interface-discovery-evidence.tar.gz`: 113 files, 3,586,752
uncompressed bytes. The tracked inventory gives every file's SHA-256; local
archive readback verified every member. Publication/download verification is
recorded separately in the completed experiment directory. Bulk weights and
installed toolchains remain excluded as previously documented.
