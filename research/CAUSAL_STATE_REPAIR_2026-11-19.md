# Can one earlier state-binding decision unlock a complete failed proof?

The desired concrete result is a saved, wholly unsuccessful base-model proof
becoming kernel-correct after changing only the induction's variable scope.
The remaining proof body must stay byte-identical. This would identify a
repairable execution decision inside a failed strategy, rather than merely
increase the frequency of an already successful whole rollout.

## Why this mechanism now

The completed four-arm pilot produced real updates but cross-context credit
tied its length control. All policies failed the sixteen original composition
roots. Saved errors show induction hypotheses about the initial registers,
while the recursive call uses changed registers. The model often selects
induction and algebra, but fixes state variables before constructing its
induction hypothesis. The needed hypothesis is quantified over those variables.

Prioritize **causal repair and credit for earlier structural decisions** over
more static cross-context reward updates. The compiler connection is lifting
state into an explicit argument of a reusable procedure. The operating-system
connection is rolling back an earlier commitment while replaying the same
continuation. Here a continuation is literal Lean proof text, the state interface
is a list of quantified theorem variables, and success is a closed kernel proof.
This analogy does not establish that arbitrary LLM reasoning has this structure.

The longer-term training idea is to turn unsuccessful attempted strategies into
verified repaired trajectories, and test whether causal credit at the repaired
decision makes that strategy executable from an ordinary root without repair.
It must be compared with the same repaired-data replay and terminal-reward
training. No update or generalization claim follows from the repair screen alone.
This follows the proposal's distinction between choosing a strategy and executing
it, and its request to develop weak attempted methods. It does not involve a
related-work search for exploration methods.

## Frozen finite intervention

Use all 256 pristine-base samples on the sixteen original October roots from
job 1373310. These roots and outputs have now been inspected: this is explicitly
a post-hoc causal diagnosis, **not held-out evaluation**. Do not select a model,
seed, proof or root after observing repair success. Previously recorded original
proof verdicts are fully resolved and all are negative.

For each candidate, look for exactly one supported, line-initial induction on
`n`. For the integer-update roots, add `generalizing a b c d`; for the rational
roots, add `generalizing x`. These are the recursive state arguments already in
the theorem, not a supplied invariant, lemma or complete proof. Preserve every
other proof byte. Core `induction` inserts the clause before `with`; supported
`induction' ... with ...` inserts it after the case-binder names. Exclude existing
generalization, block comments, ambiguous multiple matches, and unsupported
syntax explicitly. Do not repair those other cases opportunistically.

Check every applicable repair using the unchanged parser, Lean kernel, axiom
audit, 60-second timeout and eight verifier workers. Deduplicate only identical
complete Lean sources. Count all 256 source candidates, including ineligible
ones. Charge a separate at-most-300-second import warmup. No new model proposals
or GPU allocation are needed for this stage.

For **every** accepted repair, check every leave-one-variable-out version. This
tests whether the newly available state parameters are necessary for that exact
continuation. For the single rational variable, the ablation is the original
proof and uses its pinned resolved verdict. Record unresolved checks separately;
never treat a timeout as rejection. Primary cap: 256 logical repair checks;
ablation cap: 1,024 logical checks, with exact-source caching. The original
verdicts are reused only after source and evidence hashes are authenticated.

## Interpretation and next decision

A repaired proof with an originally rejected, otherwise identical body is a
causal within-proof example. Several roots from one authored schema remain one
schema, and an automated edit is extra inference computation and human-specified
structural knowledge. Do not call it learned competence, spontaneous model
discovery, or a new paradigm.

The screen's training-feasibility gate requires at least four distinct repaired
proof bodies, successful repairs in at least two target schemas, and no unresolved
primary or ablation checks. This asks for usable material beyond one template.
If it passes, design a fresh training/test split before collecting any training
data, with same-information replay and inference-only repair controls. If it
does not, do not manufacture a training win by demonstrating the edited proof or
resampling this inspected panel. Use the exact failures to decide whether this
specific causal repair mechanism has enough scope to pursue.
