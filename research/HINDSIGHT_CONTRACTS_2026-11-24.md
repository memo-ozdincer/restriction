# Learn where a failed program is valid, then construct the missing alternative

## Result sought

The model learns to produce the correct quadratic constructor for the original
target even though training contains no successful response to that target.
Its only positive examples are its own unchanged programs, under specifications
that a symbolic solver infers and Lean verifies. A contrast between valid and
invalid contexts should teach when the familiar algorithm applies; we want a
different correct algorithm to emerge on the original and changed targets.

The preceding certificate audit found actual algorithm errors in all 221
supported outputs. Neither proof formatting nor textual failure feedback repaired
them. This intervention changes the training signal: failed programs can have a
valid mathematical meaning under another contract. Original correctness is never
relabeled as success. The goal is to learn conditional construction competence,
not to count easy hindsight tasks as solving the original target.

## Infer contracts before training

Use only the original 64 quadratic-composition responses from job 1399519,
in their saved order. Do not use the feedback bank or evaluation samples.
For each supported direct polynomial function (F,G), solve the coefficient
identity

`F² + c*d*G² = (a²+c*d*b²)*(x²+c*d*y²)`

for the single unknown c. Admit only a unique solution in {-1,1}, with all
polynomial coefficients zero and the corresponding two basis laws satisfied.
The quadratic family and sign alternatives are human-specified; the solver
infers the coefficient. This is not unrestricted specification discovery.
Use the signed contract's basis law `f d a b 0 1 = (-c*d*b,a)` and its unit law.
Keep each complete model response byte-for-byte unchanged; recheck it under
the inferred contract using Lean. No sign repair or new proof certificate.

The original target has c=-1. Choose the first eight distinct complete responses
that pass a c=+1 contract and are algebraically invalid under c=-1. Require all
checks resolved and a rejected zero-function control. If fewer than eight exist,
stop before training; do not insert authored answers or generate more candidates.
The selected responses share one mathematical law; eight proof strings are not
eight independent skills. The failed two-family gates remain failed.

## Matched learning comparison

Start two rank-eight q/v adapters independently from unchanged final C1, with
identical initialization, selected responses and order. Thirty-two optimizer
steps, four passes through eight examples, AdamW lr=1e-4, zero weight decay,
gradient norm cap one, model.eval and float32 with TF32 disabled. Save exact
tokens, reference/final probabilities and weights. Re-encode each unchanged
response for training and check exact decoding; this is offline learning.

Both arms evaluate each response under the positive and original negative
prompt. Let p and n be response-mean log probabilities under those prompts;
p0,n0 are frozen-parent means. Let A be the average squared per-token logprob
change over the two contexts. The objectives are:

- Replay: `-p + 0.02*A`.
- Context contrast: `-p + softplus(1 - [(p-p0)-(n-n0)]) + 0.02*A`.

The negative-context anchor and its forward passes are present in both arms.
Only the contrast term differs. It penalizes the same invalid response in its
original context while increasing its probability where verified correct. The
anchor is not a full-distribution KL. Use sequential backward passes for the
two contexts to bound memory, with no optimizer step between them; confirm the
gradient equals the joint objective on synthetic tensors before GPU training.
This objective is an offline contrastive update, not ordinary on-policy GRPO.

## Evaluation frozen before updates

Evaluate unchanged C1 and both adapters on eight complete constructor contracts:
each sign for (1) the original coefficient d and variable names; (2) the same
law with all variable names changed; (3) coefficient 2*d; (4) coefficient d²+1.
The original negative prompt is a training-negative context, not held out.
The renamed/scaled/nonlinear variants are distinct specifications not used in
updates; they remain close mathematical relatives, not cross-domain transfer.

Sixteen samples per cell per arm, 384 total, 768-token cap, temperature/top-p one,
no top-k. Use seed 20261126+task_index identically across model arms. No hindsight
relabeling, candidate program, residual, external skill, or compiler certificate
is supplied at evaluation. Full original universal contracts must verify.
Author fixtures validate each specification before inference and never enter
training. No successful c=-1 response enters any update.

The desired comparative result requires context contrast to achieve >=8/16 on
all three distinct c=-1 variants, with base and replay <=1/16 on each, no
unresolved checks, and context contrast no more than two accepted proposals
below replay on any c=+1 retention cell. Report the original contexts separately.
These are practical screening thresholds, not a statistical significance claim.
No epoch, seed or task replacement follows a null result.

## Prior art and boundary

[Hindsight Experience Replay](https://arxiv.org/abs/1707.01495) learns from goals
actually achieved during failed attempts. [Hindsight Instruction Relabeling](https://proceedings.mlr.press/v202/zhang23ab.html)
already combines language-model relabeling with a contrastive instruction loss.
Neither relabeling nor contrastive contexts is a novelty claim here. The specific
test is kernel-checked universal goal inference and target construction without
positive target demonstrations. Even a strong result would be a research lead,
not proof of a revolutionary paradigm.

Keep code, protocols, failures and evidence on GitHub. Use a bounded def-zhijing
H100 keeper with manual SSH launch; release it on completion or failure. Preserve
both small adapters and all proposals with verified archive readback. This track
does not change the original pristine-SFT/C3 experiment or its historical gates.
