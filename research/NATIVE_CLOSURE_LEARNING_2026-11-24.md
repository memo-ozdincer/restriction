# Learn verified contract closure at C1's authenticated proof boundary

## Result sought

The corrected learning interface yields reliable, self-contained constructors
for arbitrary coefficient functions, including renamed variables, from only
eight polynomial-contract demonstrations. No source lemma, compiler or proof
start is supplied at evaluation. Existing adapters trained at the legacy boundary
are evaluated at the same native interface, separating a training-format effect
from an inference-format effect.

The preceding audit confirmed a material implementation confound: native C1
training places BOS immediately before the proof, whereas standalone adaptation
omitted it and trained on decoded responses without the BOS that C1 generated.
The format-only control still solved zero of 256 constructor attempts. This
experiment therefore asks about adaptation, not whether changing a prompt alone
solves these tasks. It is a prospective correction, not an epoch or seed sweep.

## Fixed data and six evaluation arms

Reuse the exact train/test JSON content from the completed closure-learning
experiment (job 1400174): eight examples per trained arm, eight new coefficient
specifications and two original training-target diagnostics. Reconstruct and
hash-check the data; do not mine new successes or alter the proof templates.

Train three independent rank-8 q/v LoRA adapters on unchanged final C1 using
the native prompt (no leading BOS, one trailing BOS) and response tokens without
extra BOS: hindsight, executable and transport. The only change to the old
training protocol is the authenticated prompt interface. Keep 32 updates, example
order, four epochs, initialization seed 20261120, alpha 16, no dropout, AdamW
lr=1e-4, zero weight decay, gradient cap 1 and mean response NLL plus .02 mean
squared reference-log-probability deviation. Float32/TF32 disabled, PEFT 0.10.0.
The three arms differ in their existing data/representation, not optimizer.

Evaluate six arms, all with native prompts:

1. unchanged C1;
2. new native-trained hindsight;
3. new native-trained executable;
4. new native-trained transport;
5. exact saved legacy-trained executable adapter;
6. exact saved legacy-trained transport adapter.

The two old adapters get no additional updates. Authenticate their hashes and
exact saved reference probes before evaluation. Native versus legacy-trained
within each compiled-data representation shares evaluation tokens, data, parent,
steps and optimizer; it tests the training-interface change. Historical evaluation
under legacy prompts remains a separately recorded comparison, not reused in
the new primary counts.

Ten tasks × sixteen proposals × six arms = 960 fresh proposals. Use the prior
per-task seeds 20261127 through 20261136, temperature 1, top_p 1, top_k 0 and
768 generated-token cap. No continuation prefix, source theorem, compiler,
retrieval or response repair. Explicit tokenizer insertion settings are mandatory;
assert native tokens against the authenticated formatter for every training and
evaluation prompt. Verify 44 existing fixture edges again before updates.

## Predeclared decisions

Retain the original closure-data gate: at least one native compiled-data arm
gets >=8/16 on at least three new targets, including an arbitrary-function cell
and a renamed arbitrary-function cell, while native C1 and native hindsight are
each <=1/16 on those same cells.

Retain the representation gate: native transport gets >=8/16 on at least three
of four arbitrary-function cells and exceeds native executable by >=4 accepted
responses on at least two of those cells.

Add a training-interface gate: for at least one representation, native-trained
exceeds the corresponding legacy-trained adapter by >=4 accepted responses on
at least two new targets, including at least one arbitrary-function target.
All six arms use native evaluation for this comparison. Report all three gates,
every cell and concrete accepted programs. Require all judgments resolved for a
passing gate; timeouts and parse failures remain distinct and in denominators.

No new gate constitutes a revolutionary paradigm or cross-domain generalization.
The data are inspected variants of one mathematical law. Unequal response lengths
remain reported, not hidden as matched compute. No training extension, seed
change or target selection follows outcomes. If the corrected comparison remains
weak, stop this curriculum/representation branch under this budget rather than
continuing to adjust its small examples.

## Integrity and publication

Freeze source before execution. Preserve exact IDs, all updates and reference
probes, unmodified parent hashes, adapter serialization equality and every raw
continuation/verdict. Reconstruct counts independently. Use one bounded persistent
def-zhijing allocation, manually launch through SSH, release on completion, and
publish actual new adapters and exact reused dependencies with complete download
verification. Preserve the old results and their interface qualifications.
