# A counterexample turns a failed attempt into a universally valid program

The desired artifact is a model-written constructor that satisfies its full
universal contract after receiving an automatically computed explanation of its
own failure. No correct implementation is supplied. If this works where a
failure notice alone does not, failed rollouts can provide more than a discarded
sample or a zero reward: they can generate checked training interactions.

The previous universal screen scored 0/64 on both contracts, closing its sparse
binary reward gate. This is a new intervention on the information returned after
a failure. It does not change the old counts or reopen that gate by extra seeds.
No parameter updates are authorized by this protocol; a positive result motivates
a separate, prospectively specified learning comparison with feedback removed at
evaluation. Do not claim a training paradigm from a prompted repair.

## Frozen comparison

Select the most frequent exact response from each of the two completed C1 groups,
breaking frequency ties by first occurrence. The quadratic candidate occurs seven
times and has a wrong first-coordinate sign. The Bezout candidate occurs 17 times
and returns the coefficients unchanged. These inspected tasks are development
tasks, not a fresh transfer set. Do not select another candidate after outcomes.

Extract the single polynomial lambda using a restricted parser. Calculate the
residual of the first contract law with symbolic algebra. Enumerate integer input
tuples in the fixed order `product([0,1,-1,2,-2], repeat=arity)` and take the first
nonzero residual. This is a deterministic counterexample, not a closest-to-answer
choice. Lean independently checks the residual identity and the concrete failure.
SymPy supplies feedback, never the acceptance judgment or a corrected program.

Each task has three conditions, all containing the same rejected lambda, the
same complete contract and the instruction to supply a correct implementation:

1. Failure: only the fact that the candidate fails.
2. Counterexample: one input assignment and unequal left/right values.
3. Residual: the exact polynomial left-minus-right error for arbitrary inputs.

Generate 16 proposals per condition, 96 total, from unchanged final C1. Use the
same seed across conditions within each task: 20261125 + 1000*task_index. Quadratic
precedes Bezout; failure, counterexample, residual is the condition order. Freeze
temperature/top-p one, no top-k, 768-token cap, float32 and TF32 disabled. Input
length and information differ by design; report tokens, not matched-token claims.

The strong result requires one *same* feedback condition to yield at least 4/16
accepted proofs on both tasks, while failure-only yields at most 1/16 on each,
with zero unresolved checks. These are practical mechanism thresholds, not a
significance test. Report every cell and complete accepted proofs. One-family
repair or improvements shared with failure-only do not pass the criterion.

Both original positive and zero-function negative fixtures, plus both feedback
certificates per task, must pass before sampling: eight checks. Keep the upstream
Lean verifier and axiom audit unchanged. Full contract validity is required;
fitting the supplied numerical example does not earn correctness. Parse failures
stay in denominators; timeouts stay unresolved. No human patch, extra prompt,
additional counterexample, or second repair round follows this frozen screen.

## Research boundary and next decision

Counterexample-guided synthesis is established prior art, including the original
[SKETCH work](https://people.csail.mit.edu/asolar/papers/Solar-LezamaTBSS06.pdf)
and later [neural counterexample-guided synthesis](https://arxiv.org/abs/2001.09245).
Combining a language model with counterexamples is not a novelty claim. The larger
research question is whether learning from universally checked failure-to-program
transitions creates transferable construction competence beyond successful-proof
replay. The previous full-program supervision result gives no reason to assume it.

If this screen lacks the specified signal, do not train on the inspected pair or
replace failures with authored answers. If it passes, first specify a disjoint
contract-family split and matched replay controls before training. The original
SFT/C3 experiment and all prior failed gates retain their meanings.

Use a bounded def-zhijing H100 keeper, manually launch via SSH, persist each group,
release the GPU at termination, and publish all proposals and feedback certificates.
Commit the protocol and source before generation. Audit results independently.
