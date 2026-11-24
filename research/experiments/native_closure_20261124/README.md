# Native-boundary training yields sparse transfer and no crossover advantage

The native executable adapter generates five accepted responses across three new
specifications: cubic 1/16, arbitrary-function 1/16, and renamed arbitrary-function
3/16 (all negative-sign variants). The legacy executable adapter, evaluated at
the same native boundary without updates, generates seven accepted responses
across five new specifications. Neither transport adapter solves a new target.
**All three predeclared gates fail.** Stop this small curriculum/representation
branch under this budget; do not extend its epochs or tune its seeds.

| Task/sign | C1 | Native hindsight | Native executable | Native transport | Legacy executable | Legacy transport |
|---|---:|---:|---:|---:|---:|---:|
| cubic/-1 | 0 | 0 | 1 | 0 | 1 | 0 |
| cubic/1 | 0 | 0 | 0 | 0 | 0 | 0 |
| quartic/-1 | 0 | 0 | 0 | 0 | 0 | 0 |
| quartic/1 | 0 | 0† | 0 | 0† | 2 | 0 |
| arbitrary function/-1 | 0 | 0 | 1 | 0 | 1 | 0 |
| arbitrary function/1 | 0 | 0† | 0 | 0 | 0 | 0‡ |
| renamed arbitrary function/-1 | 0 | 0 | 3 | 0 | 1‡ | 0 |
| renamed arbitrary function/1 | 0 | 0 | 0 | 0 | 2 | 0 |
| original/-1 | 0 | 0 | 1 | 1 | 0 | 1 |
| original/1 | 6 | 16 | 3 | 10 | 3 | 9 |

Every cell has 16 proposals. The original two rows are training-target diagnostics,
not new-target transfer. † Six response judgments are unresolved across five
unique 60-second timeouts: native hindsight quartic/+1 (four), native hindsight
arbitrary-function/+1 (one), and native transport quartic/+1 (one). ‡ Two parse
failures: legacy executable renamed/-1 and legacy transport arbitrary-function/+1.
All remain in denominators. Even accepting every unresolved proposal would not
meet any gate's numerical thresholds; failure is not solely the all-resolved rule.

## Concrete sampled programs

The [native arbitrary-function response](executable-opaque_-1-sample-0.lean)
constructs `fun w d a b x y => (a*x - -(w d)*b*y, b*x + a*y)`.
The [native renamed response](executable-renamed_-1-sample-5.lean) constructs
`fun metric rho u v p q => (u*p - -(metric rho)*v*q, u*q + v*p)`
and proves its full universal contract with `intros` and `ring`. These are actual
unassisted sampled programs, with Lean checking the norm-product identity and
both basis laws for every function and integer input. No constructor or source
lemma was supplied at evaluation. All twelve accepted new-target responses from
both executable arms are preserved as complete Lean files, with their source
hashes in [the index](accepted-transfer-programs.json).

These direct formulas are interesting individual successes, but the corrected
training does not produce reliable transfer or beat the old adapter by the
registered margin. The best new-minus-legacy cell difference is +2/16 on the
renamed negative-sign target, below the required +4 on two targets. The observed
counts do not establish a statistical advantage for either training interface.

## Controlled comparison and audit

The [frozen protocol](../../NATIVE_CLOSURE_LEARNING_2026-11-24.md) uses the exact
prior eight-example curricula and ten-task panel, byte-for-byte unchanged.
Three independent adapters receive 32 updates from the same C1 parent at its
authenticated prompt boundary: no leading BOS and one BOS immediately before
the proof. All training response IDs remain unchanged. Two exact legacy-trained
adapters receive zero new updates and pass their saved reference probes. All six
arms use native evaluation prompts, identical per-task seeds and generation
settings. This isolates the training-format correction within each representation.

All 44 preparation fixtures pass. Independent auditing reconstructs all 960 raw
continuations, 610 unique evaluation checks, prompts, token boundaries, reference
probes, serialized adapters, cells and gates. Audit success includes recording
unresolved judgments correctly; it does not mean those proofs were invalid.
Three new adapters serialize exactly, and parent model hashes match the preceding
C1 run. All 24 training prompt/response concatenations match joint tokenization.

The updates use rank-8 q/v LoRA, alpha 16, zero dropout, float32/TF32 disabled,
AdamW lr=1e-4 and mean response NLL plus .02 reference-log-probability deviation.
Response tokens per epoch are 521/802/3272 for hindsight/executable/transport:
matched steps, not matched token compute. This is offline supervised adaptation,
not on-policy RL. The inspected tasks all instantiate one mathematical law;
these counts are not evidence of broad abstraction or GRPO capability suppression.

Generation totals 64,153 tokens: base 7,068; native hindsight 7,977; native
executable 16,648; native transport 8,097; legacy executable 16,034; legacy
transport 8,329. No response first generates BOS. Literal `have source_contract`
and `rcases source_contract` occurrences are zero across all 960 continuations;
these string counts are descriptive, not a semantic strategy classifier.

Execution source: `4a65334da108338b4a7cde1417bffaac9156275a`, def-zhijing,
H100 at trig0010, job 1400728. The allocation ends after 31m58s; the batch exits
successfully and the wrapper releases the GPU. No allocation remains active.
Publication of all three new adapters, both reused adapters and raw evidence is
being completed; bulk C1 weights and optimizer states are excluded.
