# Two-round critiques: substantive experiments for intrinsic mathematical RLVR

User instruction (verbatim):

> lets send a set of subagents to iteratively suggest experiments to test substantive parts or formulations of this

Three independent agents proposed hypotheses, then each critiqued the others'
proposals. Scope: Luna Low/Medium and Terra Low/Medium, native Lean correctness,
no learned judge, no predefined mathematical objects, no intermediate rewards.
The experiments below are prospective; no new rollouts were generated in this
round. They isolate phenomena in frozen inference before investing in training.

## 1. Hidden sibling transfer: is discovery a reusable product of proof search?

Freeze pairs of distinct theorems sharing mathematical definitions before any
calls; hide G2 from the producer. Producer freely proves G1 and may introduce
any Lean declarations. Keep all independently verified declarations, not a
human-selected subset. G1 itself is legal. Receiver attempts G2 in three arms:
blank context, G1 theorem alone (if verified), and all verified declarations.
Identical target, model/effort and budget; charge producer work even on failure.
Only completed original target proofs count. If an accepted receiver proof
uses an imported declaration, replay the exact proof with that declaration
omitted (when possible) and authenticate the original assembled proof.

Hypothesis: a model can discover reusable mathematical knowledge without
knowing what later problem that knowledge will help solve. Especially strong
example: Luna Low fails G1, but discovers a verified general lemma that a
fresh Luna or Terra uses to solve G2. G1-only control distinguishes benefit
from additional artifacts vs merely having the earlier answer. Direct reuse
of G1 is still a success, not a banned behavior. Full-bank benefit may also
reflect added context or smaller search cost; exact omission establishes local
dependence, not general necessity. If G1 directly entails G2, report direct
transfer separately; do not remove such observations post hoc.

## 2. Matched vs swapped HELP: does mathematical assistance depend on state?

On the same theorem obtain two independent free actor attempts/questions.
Actor may provide a complete proof; do not force a question. For two question
branches, partner answers each once, freely, including full proof if desired.
From each frozen actor history make two final attempts: give its corresponding
entire question-and-answer exchange, or the other complete exchange labeled
as another conversation on the same theorem. Use the identical actual answer
bank, not newly sampled answers. Also compare a no-assistance/direct portfolio
with charged equivalent call allocation. Count nonrequests and completed first
proofs in overall accounting; conditional paired diagnostic only where there
are two actual questions. No forced question replacements or quality filter.

Hypothesis: actor-selected information works because of the particular
reasoning direction, not only because of answer quality. Matched > swapped
suggests question-specific usefulness; swapped > matched suggests self-
diagnosis or anchoring may be counterproductive; equal but both > blank
suggests generic useful information. Swapping answers alone could break
pronouns, symbols and local assumptions; transfer the full Q&A to reduce
this confound. Even a matched advantage is not proof of latent-state
matching or novel mathematical discovery. Record whole-target delegation
and actual use retrospectively, never as reward. This is the cheapest direct
consumption/coordination test.

## 3. Two failed proofs: does independent partial work compose?

Use a frozen pair of rejected attempts on the same root. Give the same
receiver either both complete attempts and native errors, either attempt
alone, or neither. Charge both original attempts in each branch; same final
model and effort. Receiver can abandon all prior work. The existing failed
bank can support this diagnostic without new discovery generations.
Hypothesis: independently discovered partial mathematical reasoning can
combine into a closed proof neither original attempt nor either individual
trace achieves. Both-only closure is a candidate, not proof of composition;
inspect actual distinct contributions and exact omission where native
objects exist. Stochastic re-generation or tactic similarity alone does not
establish necessity. Negative result: no added benefit or merely repeated
sampling. Do not force a synthesis strategy or reward combining traces.

## 4. Native scratch space: does the representation itself unlock work?

Producer can freely write checked Lean declarations (including original
root). Freeze one generated bank. Receiver gets identical checked declaration
content and verification status in two arms; in one those declarations are
installed as native named facts, in the other they are ordinary text that
can be reconstructed. Same root and receiver. Hypothesis: executable
availability, not just additional mathematical content, changes reachability.
Do not compare checked bank with unfiltered invalid text, which confounds
validation with native representation. Direct-target delegation counts but
is not evidence for independent mathematical discovery. This distinguishes
execution/representation from discovery, not learning.

## Additional lower-priority forks

- Producer freely chooses what to communicate after failure, compare with
  entire raw failed proof + exact Lean feedback and blank receiver. Tests
  whether model-selected compression preserves discoveries or throws away
  useful formal error information. No mandatory idea or lemma format.
- Bidirectional unrestricted consultation: A may solve or ask B; B may
  solve or ask A. Compare A/B/A independent-call portfolio and same-model
  dialogue with matched role budgets. Whole solutions always legal.
- Continue same actor history vs fresh session with identical public text:
  only informative if there is a genuine history difference (otherwise same
  distribution); avoid attributing context effects to hidden mental state.

## Ranking and decisions from critique

All three agents regard matched/swapped HELP and hidden sibling transfer as
the substantive leading tests. Two favor matched/swapped first for low cost;
one ranks hidden sibling first for stronger discovery evidence. Scratch
space alone ranks lower because it can be ordinary bookkeeping. Two failed
proofs is a cheap special case of compositional transfer using existing data.

Recommended order by scientific question rather than publication redundancy:
1. Matched/swapped HELP for endogenous communication/consumption.
2. Hidden sibling transfer for reusable discovery beyond direct outsourcing.
3. Both-vs-either frozen failed traces for compositional work.
4. Native-vs-text same bank if representation remains the live explanation.

None can demonstrate actual RL gradient expansion or autonomous learning
without training and separate unassisted evaluation. The only task reward
in a later trainer should remain original theorem validity. Use budgets to
account for resources; never reward human-rated insight, intermediate
success, mandated decomposition or refusal to outsource. Terminal correctness
is not by itself proof that all alternative mechanisms preserve RLVR's
learning dynamics; that is an empirical question.
