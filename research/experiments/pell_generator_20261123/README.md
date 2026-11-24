# Bounded witness-generator learning: completed result

The program-trained model produced one verified conditional generator that reaches
`(1351, 780)` after five state updates, although training examples needed at most
two. This was a training discriminant, D=3. Every unseen-discriminant cell failed;
the registered generalization result is **false**.

| Evaluation task | C1 | Literal adapter | Generator adapter |
|---|---:|---:|---:|
| D=11, power 2 | 0/16 | 0/16 | 0/16 |
| D=11, power 4 | 0/16 | 0/16 | 0/16 |
| D=11, power 6 | 0/16 | 0/16 | 0/16 |
| D=13, power 2 | 0/16 | 0/16 | 0/16 |
| D=13, power 4 | 0/16 | 0/16 | 0/16 |
| D=13, power 6 | 0/16 | 0/16 | 0/16 |
| D=3, power 6 | 0/16 | 0/16 | 1/16 |
| D=7, power 6 | 0/16 | 0/16 | 0/16 |

All 384 proposals are included, including two generator parse errors. The independent
audit reproduces 280 unique Lean checks and 48 fixture checks, with zero unresolved
judgments. No primary cell had an accepted proof, so no registered fuel ablations
were selected. Neither numerical nor mechanism criterion passes.

## Concrete sampled behavior

[The complete accepted proof](accepted-generator.lean), sample index 11, computes
`(2,1) -> (7,4) -> (26,15) -> (97,56) -> (362,209) -> (1351,780)`.
Its conditional step becomes stationary above 362; the fixed eight-iteration
recursor therefore performs five state changes and three stationary iterations.
Lean verifies `x² - 3y² = 1` and `362 < x ≤ 1448`. The saved execution trace is
an arithmetic interpretation of this proof, not an additional Lean fuel ablation.

The algorithm and eight-step budget were authored supervision. This is a rare
longer execution on a familiar discriminant, not learned unbounded iteration,
autonomous Pell discovery, or demonstrated transfer to new discriminants.

## Training and execution

Both rank-eight adapters start from the same final ordinary-GRPO C1 checkpoint,
with identical initialization, example order and 32 update steps. This is supervised
learning, separate from the original pristine-SFT/C3 comparison. Literal targets
contain 540 supervised tokens; generator targets contain 4,404. They are matched
by examples and updates, not tokens or procedural information. First-to-last epoch
mean NLL falls from 1.607 to 0.153 for literals and 1.271 to 0.119 for generators.
Lower training loss did not establish transfer.

The [protocol](../../PELL_GENERATOR_2026-11-23.md) and source were frozen at
`97ada184a9da2c6173a345609c9753e359ef5306` before sampling. Job 1399388 used one H100
on trig0028 under def-zhijing for 12m29s. Its wrapper completed successfully and
released the keeper allocation. Both rejected authoring panels are preserved;
the corrected panel passed before model sampling. The verifier was unchanged.

## Preservation and decision

The evidence archive includes both actual adapters, every sampled response,
verifier outputs, training records, model identity, frozen source, allocation
records, and all three authoring attempts. Bulk C1 weights and optimizer states
are excluded. Publication and download verification are recorded separately.

Do not extend this run with more epochs or seeds to chase the failed criterion.
A future experiment must change the learning mechanism and explain why the
observed interface dependence or rare verified program creates a useful signal.
Earlier failed gates and this study's registered outcome remain unchanged.
