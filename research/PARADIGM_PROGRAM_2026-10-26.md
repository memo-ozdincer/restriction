# From proof distribution control to executable procedures

Status: research decision and prospective pilot registration, October 26, 2026.
No new model result exists. This supersedes the old roadmap's immediate-work
ordering for this newly authorized track, not the definitions or outcomes of
the historical C0–C5 experiments.

## Target and priority

The user requests a major training paradigm, with ambitious mechanisms drawn
from computer science and pre-LLM RL, and explicitly rejects marginal benchmark
polishing. A breakthrough is a target, not an assumed outcome. Select work for
plausible mechanism, importance, and ability to falsify it with available
resources; there is no defensible numerical probability of revolutionary success.

The most promising target is **learning a broad set of executable procedures
that remain useful when the training scaffold, theorem, and composition change**.
The key distinction is

    P(correct | x) = sum_s P(start s | x) P(correct | x, start s).

A changed first factor can improve ordinary pass rates without teaching the
second. Our first intervention supplies a controlled initial-state distribution
so that unreliable but valid procedures receive practice. Later work must test
whether learned parts compose into capabilities absent under ordinary training.

| Priority | Mechanism | Discriminating outcome | Reason to stop |
| --- | --- | --- | --- |
| 1 | Protected practice from verified partial proofs | Improved execution under identical starts on unseen theorems, followed by improvement when starts are removed | Only prompt assistance or memorization; no held-out execution gain |
| 2 | Verified procedure contracts and composition | Independently mastered components solve unseen combinations without archive retrieval at evaluation | Only stored-solution retrieval, or no composition benefit |
| 3 | Competence-preserving updates | A single model retains earlier procedures while acquiring new ones and adapts faster | No measured interference, or ordinary replay suffices |

Service scheduling in operating systems motivates reserved practice; options
and intra-option learning motivate procedure execution; compiler interfaces
motivate checked subproof contracts. These are design correspondences, not
novelty claims. In particular, generic gradient isolation already has substantial
prior art, including October 19 Anthropic-affiliated GRAFT. See the dated
primary-source review in `FRONTIER_RL_SOURCES_2026-10-26.md`.

Do not start with cap sweeps, another complete C5 retry, seed multiplication,
or another diversity-count comparison. Later matched evidence favors C2 soft
unlikeliness over C3 hard blocking in held-out tactic richness, with identical
277/467 pass@128 solves. That weakens the case for escalating blocking alone.
Tactic signatures do not establish semantic strategies. The website's earlier
C1/C3 evidence remains valid within its stated scope but is not the full state
of the project.

## First hypothesis: valid starts can expose repairable execution deficits

An archived successful proof establishes that a continuation exists. It does
not establish that the base policy can reliably execute from that start, or
that the supplied start is sufficient to force a semantic strategy. The first
GPU screen tests whether short, valid, nonterminal starts expose a substantial
set of partially competent continuation tasks. This decides whether to invest
in a training comparison; it is not itself a capability result.
Low continuation accuracy can also reflect unfamiliar conditioning rather than
a weak semantic method. The screen alone cannot distinguish those explanations;
held-out conditional execution and root transfer must be reported separately.

Preparation uses only the original C0 **training** archive and registered train
theorems. Check source hashes, discard known padding, preserve exact proof text,
and split selected theorems by identity before inference. Select up to 256
practice theorems and 64 disjoint diagnostic theorems, with up to two distinct
first-tactic routes per theorem. Initial tactic heads are descriptive strata,
not semantic labels. Do not use existing validation or miniF2F-test outputs to
construct this panel.

Prefix eligibility is fixed before looking at continuation outcomes: one or
two complete top-level steps; at least two subsequent steps; no more than
40% of the original proof's tokens and 128 tokens; complete formatted prompt
fits the unchanged 512-token prompt limit. Keep raw text slices rather than
reformatting a proof. Known successful full proofs provide witnesses; a fresh
Lean check and a prefix-only negative control must reject solved or malformed
prefix tasks before inference. A selected archived witness that no longer
verifies is a provenance failure, not a model failure. Report all exclusions.

All task lists, parameters, hashes, and source witnesses are saved before model
generation. The initial screen uses the pristine pinned DeepSeek-Prover-V1.5-SFT
checkpoint, temperature 1, top-p 1, top-k disabled, and 512 new-token cap.
Generate 16 continuations per practice prefix and 32 per diagnostic root/prefix,
with a ceiling of 14,336 generated proposals (512*16 + 192*32). Count supplied
tokens, generated tokens, every Lean call, wall time, and timeouts separately.
Longer total conditioning is an input contribution, not free information.
The 14,336 ceiling is the registered scientific sample. The inherited
four-worker sample-only driver may append up to three explicitly marked padding
rows per panel: at most 48 practice and 96 diagnostic extra continuations.
Count these in physical proposals, tokens, and verification costs, exclude them
from scientific counts and the gate, and reject unmarked duplicates. No padding
is permitted in the later training comparison.

The screen advances if at least 48 practice theorem identities have a prefix
with 1–8 successes of 16, spread across at least four descriptive first-tactic
strata with eight such theorems each. This is a practical signal-availability
threshold, not a significance test or a claim that the underlying success
probability is known. Freeze any selected training subset using practice data
only. Diagnostic outcomes never decide which prefixes receive training.
If the threshold fails, stop this pilot and investigate the failure mechanism
before considering another domain or state representation. Do not relax it
after viewing outcomes and still call the test preregistered.

## Conditional training comparison, only if the screen advances

Restart both arms from the identical pristine base. Use the same theorem
identities and number of independent proposals per theorem, seed, optimizer,
temperature, KL, token limits, verifier, and update rule. The initial mechanism
contrast changes **only the distribution of initial proof states**:

- Root arm: all attempts begin with the theorem statement.
- Practice arm: half of attempts begin at the root; half begin at the frozen
  eligible partial proofs, with reserved per-prefix quotas.

Both arms use suffix-only PPO loss, ordinary binary correctness, within-task
GRPO normalization, no hard blocking, and no learned judge. PPO epochs=2,
KL coefficient=0.10, learning rate=1e-6, rank penalty=0.25 match the stronger
existing C2 configuration. Preserve identical admission rules across arms.
Identical admission rules do not imply identical admitted group counts. Report
admitted/skipped groups, optimized response tokens, optimizer steps, and actual
generation/verification cost for each arm. Changing starts also changes suffix
length and available within-group learning signal; these are mediated effects
of the initial-state intervention, not independently isolated mechanisms.
Each arm is capped at 32,768 proposals and must fit a bounded short run with
frequent proof persistence and a verified complete final checkpoint. The
archive and the guidance are part of the intervention; do not describe the
comparison as isolating scheduler fairness from additional information.

Evaluate both models and the base on exactly the same diagnostic roots and
prefixes at 32 fresh attempts each, without adaptive restriction. Primary
mechanistic endpoint: theorem-balanced conditional correctness on common
prefixes. Report every task and all root/prefix outcomes, as well as paired
theorem-level uncertainty. Root success after removing the scaffold is a
separate transfer endpoint. A larger count of tactic strings is secondary.

A ten-percentage-point conditional improvement over the root arm is the
predeclared material-effect screen, with no more than a two-point decrease in
diagnostic root correctness. This is a decision threshold, not a universal
definition of success. A positive conditional effect without root transfer
supports procedure repair under supplied starts only. It does not establish a
general paradigm. A null short pilot is evidence at that budget, not proof
that the mechanism cannot work.

Before attributing a promising result to a new learning mechanism, add a
verified-success replay comparator using the same source proof bank, and a
uniform-prefix curriculum comparator before claiming adaptive scheduling
benefit. Account for the full demonstration information in each. These
comparators are contingent on a large first effect, not automatically queued
incremental runs. A further experiment must freeze actual theorem-family or
composition shifts before inspecting outcomes; the present random disjoint
theorem panel is not a compositional-OOD benchmark.

## Escalation and stopping

A strong execution result motivates extracting faithful Lean state transitions
and procedure contracts, then testing held-out compositions. It does not
motivate another seed purely for a smaller error bar. An interference result
motivates the competence-preservation mechanism. If a simpler replay method
matches the gains, acknowledge that and move the research question to what
contracts or representations make transfer possible.

New experiments must state the motivating observation, competing predictions,
resources, and decision before launch. Never credit invalid-but-different
proofs; never silently weaken Lean verification or exclude failed proposals.
Save complete configuration, model revision, hashes, outputs, and run status.
Do not claim exact resume from weight-only checkpoints. Pinned historical
runs and source hashes remain intact.

## Compute and publication

Prepared panel: `../runs/execution-pilot-panel-20261026`, manifest SHA-256
`c5513992dc40cda4f62896c2b53b5c4509f2d5934b245b2477da71b2a17fc0b8`.
Actual selection is 256 practice and 64 diagnostic theorems, 432 practice
prefixes, and 168 diagnostic root/prefix tasks. Thus the screen requests 12,288
attempts, and fresh witness/prefix checks add 1,072 Lean calls. Both actual
panels divide by four, so no padding is expected. The manifest's generic
budget table lists all panel sizes at 32 samples; `tasks[].screen_samples`,
this registration, and the runner specify 16 for practice and 32 for diagnostic
screening. The immutable original manifest is retained. Compact provenance is
in `results/execution_pilot_panel_20261026.json`.

Job 1176227 reserves a persistent `def-zhijing` workspace with four H100s and a
24-hour limit, held by a Python loop. It is pending at registration. The keeper
does not launch training. Node access and cgroup placement must be verified
before manually launching the frozen experiment. Preparation and CPU validation
can proceed while queued. See `GPU_WORKSPACE_2026-10-26.md`.

Commit and push reviewed code, decisions, compact evidence, and run provenance
at milestones under the user's standing authorization. Keep bulk checkpoints
and raw archives local with recorded paths and checksums. Refresh the primary
RL evidence when choosing subsequent experiments; this is not a claim to have
read every statement by either lab or their employees.
