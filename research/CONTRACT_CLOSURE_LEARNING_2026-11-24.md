# Learn construction from the verified closure of a failed program

## Concrete result sought

A sampled, self-contained proof constructs a universal norm-composition program
for an arbitrary coefficient function `w : ℤ → ℤ`, although demonstrations only
use degree-at-most-two polynomial coefficients. The model supplies the entire
program and certificate without a compiler, supplied source lemma, external
retrieval, or response repair. A renamed version should work too. This would
show useful abstraction from a small automatically constructed curriculum.

The previous compiler derives eight valid programs from one unchanged failed
model program and its inferred, verified hindsight contract. Hindsight replay
alone failed every original-sign target. The present question is whether closing
that experience under specification transformations teaches transferable
construction, and whether abstract-contract proofs help beyond direct programs.
This remains one mathematical family, not evidence of a revolutionary paradigm.

## Four arms and fixed data

Use final ordinary-GRPO C1, preserving all historical pristine-SFT/C3 boundaries.
Evaluate unchanged C1 and three independent adapters:

1. Hindsight: the eight previously selected unchanged responses under their
   inferred positive contract, with ordinary anchored likelihood training.
2. Executable: the eight verified compiler wrappers from the final transport
   stage, each paired with the same fixed simplification/ring certificate.
3. Transport: the exact same eight target statements as executable, but prove
   each by locally proving the source contract with the unchanged sampled proof
   and then reusing that abstract contract at the inferred argument.

Executable versus transport shares targets, mathematical functions and data
origin. Hindsight differs in target coverage and is the baseline for whether
closure data helps. It is not a representation-only control. Executable versus
transport differs in proof representation and length; log exact tokens and do
not claim compute-matched or token-matched training. The source lemma in transport
is inside the response and must itself be proved; it is never a test-time gift.

All adapters use 32 updates, cycling eight examples four times in fixed order;
rank-8, alpha-16 q/v LoRA, initialization seed 20261120, zero dropout, AdamW
lr=1e-4, zero weight decay, gradient cap 1. Mean response-token negative log
likelihood plus .02 mean squared deviation from frozen reference token log
probabilities. Float32 with TF32 disabled throughout. This is offline supervised
learning of compiler-generated experience, not an on-policy RL claim.

## Evaluation before outcomes

Eight new development specifications, 16 fresh responses per arm per task:
both signed norms with coefficient d³-2d+3, both with (d²+2d+2)²+1,
both with an arbitrary coefficient function w(d), and both arbitrary-function
targets with all variables renamed. Add the original two signed specifications
as training-target diagnostics: ten tasks, 640 proposals total. No coefficient
function or degree-above-two target is used in training. Test reference functions
are fixture-only; model prompts contain only the complete requested theorem.
These are authored related-family targets, not a blind external benchmark.

Uniform temperature 1, top_p 1, top_k 0, 768-token response cap, seeds 20261127
through 20261136 in listed order. Every proposal counts, including parse errors
and truncations. Unchanged Lean verifier, axiom audit, four workers. No repair,
selection of seed, additional samples, training extensions, or code changes
after model outcomes. Verify all training responses and positive/zero-function
test fixtures before allocating a GPU. Retain any authoring failures separately.

Primary closure-data gate: at least one compiled-data arm obtains >=8/16 on at
least three of the eight new targets, including an arbitrary-function target and
its renamed family; unchanged C1 and hindsight must each be <=1/16 on those
same three cells. This is a curriculum-transfer result, not proof that the
transport representation is needed.

Separate abstraction gate: transport obtains >=8/16 on at least three of the
four arbitrary-function cells, and exceeds executable by >=4 successes on at
least two of those four cells. Report both gates, all cells and actual accepted
proofs. Require no unresolved judgments for either gate. No broader paradigm
claim follows even from both passing. If direct executable training matches
transport, prefer the simpler representation and reject an abstraction advantage.

## Integrity and publication

Freeze protocol and implementation before GPU execution. Save raw sources,
fixture verdicts, exact tokens, frozen-reference probes, all updates, parent
hashes and exact serialized adapter equality. Independently rebuild all edges
and counts from raw responses. Publish actual adapters and compact raw evidence,
then verify a fresh download member by member. Use a bounded persistent
def-zhijing Slurm allocation with manual SSH execution and release on completion.
