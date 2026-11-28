# Andrews–Curtis: independent experiment pitches and critique

Three agents independently proposed experiments and cross-critiqued
one another's designs. Background: [four deep investigations](CREATIVE_RLVR_FOUR_DEEP_DIVES_2026-11-27.md).
Exploratory recommendations, no experiments launched; final specifications
must be registered before any training.

## What we know and must preserve

AC trivialization is a verifier-driven symbolic transformation problem;
the latest PPO uses mathematical substitutions, cyclic attention, length
shaping and fixed train presentations among its evaluation benchmark.
Do not mistake the 607/1190 headline for held-out transfer. The environment
already has mathematically motivated composite moves (2025 supermove
mining, 2026 substitution actions), automorphic generated training
examples, and strong classical solvers. See [2025 paper](https://arxiv.org/html/2408.15332v2),
[Two-Hump](https://arxiv.org/html/2606.21611v1),
[ACSolverX](https://github.com/Math-AI-Caltech/ACSolverX).
No claim of novelty for macros or automorphic curricula alone.

## Pitch 1 — mathematical transport: measure what was actually learned

Frozen policy audit, no training first. Use 30–50 certified parent
presentations with 3–5 held-out automorphic images each, matched unrelated
presentations and simple symmetry controls (relator swap, cyclic rotation,
inversion). Generate only mechanically valid images, verify each moved
witness independently; the policy sees the input, not the witness.
Keep original terminal criterion and primitive action budget. Match
length, witness-expanded horizon and classical difficulty as far as
possible; record residual mismatches, first-hit frequency and actual
primitive transitions. Split by generation ancestry/parent before training,
deduplicate exact and simple canonical states, audit AC-1M provenance
leakage. All known trivial presentations are in the same equivalence
class; do not claim class-level split. Frozen checkpoint availability
must be verified, else reproduce a modest ordinary baseline.

Hypothesis: successful behavior on a parent may not transport through
mathematically meaningful changes of representation. A symmetry failure
may instead be tokenizer/interface brittleness; matching classical
difficulty and primitive witnesses helps separate it.

Conditional intervention: random legal automorphism exposure generated
without selecting a particular skill, ordinary root evaluation, compare
ordinary sampling and the published automorphic curriculum. Existing
AC-1M generation overlaps substantially; novelty would need to come
from a distinct transfer result, not use of automorphisms.

## Pitch 2 — independently certified barriers

Select small endpoint-to-endpoint equivalence problems with replayable
witnesses and exact bounded-graph distances. Pair tasks with similar
shortest path lengths, start lengths and branching but distinct required
maximum intermediate length. Compute barrier in the exact action and
canonicalization convention used by the learner. Record probability
of crossing, time to first crossing, conditional success afterward,
length trajectory, and actual elementary move count.

The [certificate paper](https://arxiv.org/abs/2607.23611) and
[artifacts](https://github.com/joe-carr-data/ac-certificates) provide
motivating examples. AK3 itself is unresolved; never use it as a
certified-solvable trivialization task. Length-19 bound is a substitution-
graph result, not elementary primitive result; lower bound 27 for the
other branch does not establish connectivity or solvability within 27.
The cap-27 graph has ~13.5M states, not a cheap first toy. Endpoint
reachability is a distinct objective; do not claim trivialization
transfer without independent testing.

Hypothesis: failures cluster before necessary nonmonotone crossings,
rather than uniformly along solution lengths. Compare published shaped
reward to binary terminal reward as a distinct ablation; possibility
that long detours are penalized by shaping must not be confused with
an intrinsic failure of terminal-only RLVR.

Candidate interventions after diagnostic:
- Uniform branch-restores from native checkpoints from own failed
  trajectories (not selected by solution distance or preferred moves).
  Compare against ordinary extra rollouts, depth-matched on-policy
  snapshots, and arbitrary feasible restores if independently available;
  charge all generation, resets and primitive actions. Evaluate from
  original roots; test held-out roots separately.
- Coherent long-horizon exploratory policy mixtures: select independent
  checkpoint/lineage once per rollout versus independent per-step mixing,
  match action marginals/entropy where feasible, actual primitive budget
  and inference cost. Evaluate both ensemble search and a standalone
  learned policy separately. Tests whether temporal coherence matters
  more than simply additional action noise. No supplied detour.

## Pitch 3 — good states inside failures

Audit same frozen rollouts with a bounded independent solver. Count failed
attempts that enter states with a replayable completion within the actual
remaining primitive budget; compare analogous random states matched
for depth and length. Analyze whether policy later executes such
completions more often. A solver's failure to find a suffix is unknown,
not proof of dead end; exact finite graph only where tractable.
No solver-generated labels or suffixes fed to the learner in this audit.

If substantial unexploited opportunity, compare model-blind uniform
failed-state branching with ordinary extra rollouts, matched successful
prefixes, and random starts. Another possibility is relabeling native
segments as endpoint reachability then root specialization (explicitly
changes goal distribution, overlaps HER; compare random endpoint control).
Distinguish local skill acquisition from obtaining more positive rewards.

## Pitch 4 — independent discovery of executable abstractions

After diagnostics, allow generic model-authored chunks consisting of
sequences/repetition/counts over existing legal primitives or reusable
model-defined slots. No human-specified mathematical operation library
in the intervention. Charge expanded primitive moves and verifier cost,
replay every successful solution. Controls: primitive policy, independent
random chunks matched in length/count, frequency-mined supermoves
(existing precedent), published substitution action oracle for headroom.
Separate canonical representation, multistep actions and architecture
changes rather than conflating them.

Hypothesis: learned action composition makes useful coherent transformations
available that step-by-step training rarely discovers, then transfers to
unseen presentations and longer relators. Judge chunk effects across
independent inputs, not literal n-gram frequency; identities, loops,
memorized fragments and length-specific legality are not abstractions.
Generic sequences may reproduce cyclic alignments rather than new
mathematics (many elementary moves in published substitutions are
conjugations). Do not reward novelty, frequency or elegance.

Two evaluations: library on (algorithm/search acceleration) and library
off (ordinary primitive policy capability). Flattening a macro for
verification alone is NOT a capability-transfer result. Keep primitive
decoder trained/shared throughout or declare separately matched
self-replay control, to avoid simply removing an untrained interface.
Actual primitive-only generation must solve independently.

## Cross-critique and ordering

All three reviewers recommend a cheap paired transport audit first.
Barrier/failed-state audits second, conditional branching or coherent
mixtures next if evidence supports them. Self-invented chunks the more
ambitious research direction, not first expensive experiment. A direct
mathematical experiment is attractive, but no need to presuppose that
abstractions, barriers, or transfer explain existing failures.

First practical panel: native upstream policy, 30–50 certified parents,
3–5 images/parent, symmetry and unrelated controls, modest fixed
proposal budgets. Preserve original task/reward in evaluation. Use exact
witness checks offline, no known path in the policy input. Select
independent finite barrier graphs and residual-state diagnostics alongside
only if feasible. Register all criteria, provenance and compute accounting
before running. This document makes no result or novelty claim.
