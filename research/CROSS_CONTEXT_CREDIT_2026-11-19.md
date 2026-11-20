# Train procedures for their verified usefulness across contexts

Prospective mechanism and training-signal screen, November 19, 2026.

**The result we want:** a single trained model produces a reusable proof
procedure on fresh composition tasks where matched local-correctness training
does not, without retrieving stored answers or receiving a proof prefix at
evaluation. A library of successful strings alone would not establish this.

The motivating evidence is concrete but weak: one sampled GRPO continuation
verified unchanged in two recurrence worlds, while independent sampling on the
second world found no proof. Both worlds supplied human-authored invariants;
the local-context intervention missed its 4/32 sampling threshold. This result
does not pass the older protected-practice training gate or establish learned
transfer. It motivates a different proposed reward intervention.

## Intervention and comparison

Treat an emitted proof body as a candidate procedure. Execute its exact bytes
against several training contexts expressing related obligations. Let L be its
kernel-validity indicator in the source context and P1,P2,P3 its validity in
three peer contexts. Compare ordinary local credit Rlocal=L with
Rcross=L*(P1+P2+P3)/3. Incorrect source proofs never receive positive credit.
No string-diversity measure or learned judge contributes to either reward.

The future matched policy-gradient comparison must use the same pristine pinned
DeepSeek-Prover-V1.5-SFT initialization/reference, context bank, sampling budgets,
optimizer, KL rule and verifier, changing only this reward. Both arms compute
the same peer checks; the local arm discards peer scores for optimization.
On-policy candidate texts will diverge after updates; do not claim identical
trajectories. A shared initial candidate bank allows the first credit contrast
to be inspected directly. Report extra verification cost and skipped groups.
Optimizer settings and the exact training budget remain to be frozen before
any parameter update; this document does not claim training has run.

This resembles the compiler distinction between a procedure's implementation
and the contexts in which it can be used. It is an operational design, not a
novelty claim. The important learning question is whether rewarding contextual
validity changes the procedures represented by one policy and subsequently
helps when training interfaces are removed. Cross-checking a finite bank alone
cannot establish universal validity or broad generalization.

## Registered signal screen

Prepare 20 training-only tasks: four each for quadratic nonzero extraction,
integer Bezout witness extraction, single shear identities, rational
cancellation with denominator premises, and elementary induction/case closure.
The four rows in a family are correlated contexts, not independent discoveries.
The induction family includes Nat, List and Option obligations; syntactic
compatibility is not assumed to imply interchangeable semantic contracts.
Negative transfers are legitimate failures, not verifier bugs.

No recurrence root, iteration-plus-invariant composition, old transfer-panel
root/witness, or rational closed-form recurrence enters training. All twenty
authored witnesses are hidden from generation and checked separately. Check
empty continuations and both `sorry`/fresh-axiom negative controls: 42 Lean calls.
Import warmup may use a separate 300-second budget, is recorded, and is not a
model proof or scientific candidate. Model correctness checks remain 60 seconds
with the unchanged upstream verifier, lexical gate and closed-axiom audit.

Generate 16 independent samples per task from the pristine base: 320 proposals,
temperature 1, top-p 1, top-k disabled, seed 20261119 with request-ID offsets,
256 generated-token cap and 1,536 prompt-token cap. No candidate is repaired.
Execute every parseable candidate in all four contexts of its own family:
1,280 logical candidate/context checks maximum. Cache only byte-identical whole
Lean sources. Publish logical and physical counts, hashes, all rejections,
timeouts, candidate texts and the entire source/peer correctness matrix.

A source group separates the rewards if its sixteen samples include both a
locally correct candidate passing at least two peers and a locally correct
candidate passing at most one peer, with all four judgments resolved for each.
The screen advances only if at least two families contain such a source group.
Any missing/resource-error verdict makes that candidate ineligible for reward
comparison; it cannot create apparent brittleness. If the gate fails, do not
train an indistinguishable or unsupported intervention or sweep more seeds.
Inspect whether the failure is lack of local correctness or lack of a credit
contrast. A positive screen licenses freezing the training design, not claiming
training success or silently bypassing earlier studies' gates.

Use one H100/H200 for at most 45 minutes under def-zhijing, held by the existing
Python keeper, and launch manually via SSH inside its allocation. CPU bank
checks precede allocation. Save outputs after every request, release the
allocation after terminal output, and do not automatically resubmit.

## Exclusion ledger and eventual evaluation

The bank generator does not read any held-out panel or model outputs. Nonzero
and witness tasks start with an explicit algebraic assumption; shear tasks
are one update with no iteration; rational tasks are one normalization with
all denominator premises; closure tasks supply the induction premise. These
are atomic training obligations, not renamed versions of the October multi-edge
graphs. The bank does include atomic forms informed by the already-inspected
November examples; those November targets can no longer serve as held-out tests.

Keep the existing October two-domain composition roots evaluation-only, with
their documented witness erratum, and freeze an additional fresh-family test
before training if a broader claim is sought. Do not select a final checkpoint,
training examples, reward weights, or task replacements from evaluation results.
The proposed policy-gradient contrast is separate from the old frontier-schedule
experiment, whose original gates and definitions remain intact.

## Current primary-source implications

Anthropic's October 15 [auditor RL study](https://alignment.anthropic.com/2026/training-alignment-auditors/)
reports that its reward design changed the investigative behaviors learned and
that the best policy transferred to harder targets in a different scaffold.
Its pointwise rewards were vulnerable to manufactured findings. This supports
measuring the behavior rewarded and testing a changed scaffold; it does not
validate proof cross-execution. Our correctness signal remains Lean.

OpenAI's November 3 [evaluation-objective study](https://alignment.openai.com/eval-production-behavior-gap/)
reports that objective framing can change evaluation behavior. Its agent-safety
setting differs from proof generation. The relevant caution is to distinguish
conditioning effects from learning: a local-hypothesis success is not evidence
that weights acquired a procedure. Evaluation must remove the training scaffold.

The user's [restriction report](https://memoozdincer.com/restriction/) motivates
preserving useful alternatives, while the repository's later matched evidence
limits what tactic richness alone establishes. This experiment targets semantic
utility through checked execution, not a larger count of tactic strings. No
survey of similar exploration/blocking algorithms was used to select it.
