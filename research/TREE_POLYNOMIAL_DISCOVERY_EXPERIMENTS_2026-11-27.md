# Tree-polynomial discovery: diagnostic and intervention proposals

Three independent agents (diagnostics, intervention design, mathematical
benchmark) examined the primary literature. This is an open proposal,
not a registered training run. See [four deep dives](CREATIVE_RLVR_FOUR_DEEP_DIVES_2026-11-27.md).
User requested experiments for set 1 and potential interventions.
Keep strategy discoveries open ended; never reward a human-defined motif.

## Important corrections to the initial discovery narrative

[Ramos–Sun independence polynomial](https://arxiv.org/html/2510.18826)
and [Du et al. dominating polynomial](https://arxiv.org/html/2605.02193v1)
use PatternBoost (elite imitation plus greedy local search), not
ordinary terminal-only policy gradient RL. The latter optimizes one
defect at gamma+1; the former optimizes a fixed index. Failure to
discover multiple violations incidentally is not a demonstrated failure
under a reward explicitly asking for multiple violations. The original
independence paper also says the then-known multiple witnesses were
beyond its explored size. Establish size-matched witnesses, and train
on the actual target objective before attributing failure to RL.

The exact native property is a strict log-concavity violation at an
interior support index i: a[i-1]*a[i+1] > a[i]^2, with positive
coefficients. a counts independent sets or dominating sets by size.
This does NOT necessarily imply non-unimodality (the sequence can still
increase then decrease). Do not conflate the two mathematical questions.

## Independently computed finite witness anchors

Benchmark agent computed exact coefficients using generic rooted-tree
DP, as an analytical feasibility check, not a learning experiment.
The counts below are to be independently rechecked in the implementation
before accepting a discovered result; no new optimality claim.

| Polynomial / family | n | Violation indices | Adjacent coefficient triples | Exact defect(s) |
|---|---:|---|---|---|
| Independence, Galvin T_(5,5) | 56 | 27 (alpha=30) | (46769362,573580,14140) | 332324762280 |
| Independence, Bautista–Ramos TG_(2,5) | 70 | 34,36 (alpha=37) | (1497204822,10079627,107908); (107908,445,2) | 59961497473247; 17791 |
| Dominating, W_(2,5) | 101 | 34,36 (gamma=33) | (2,567,363489); (363489,53658657,8926707427) | 405489; 365508484889154 |

Sources: [Galvin construction](https://arxiv.org/abs/2502.10654),
[Bautista–Ramos](https://arxiv.org/html/2511.00334),
[Du et al. W family §4](https://arxiv.org/html/2605.02193v1).
W_(2,t) sizes 29,47,65,83,101 for t=1..5 give respectively 0,0,0,1,2
violations. TG_(2,t) sizes 22,34,46,58,70 give 0,0,0,0,2.
These are minima within tested families, not global minimum sizes.
Known witnesses stay out of learner inputs, training archives and reset
distributions. Use only to certify feasibility and as offline probes.

## Experiment A: reproduce and diagnose the 56-vertex blind spot

Hypothesis: published path collapse reflects either magnitude-sensitive
terminal scoring, representation degeneracy, or structural exploration
barriers; discriminating them precedes choosing an intervention.

Use same-size targets n=56, i=28 (easier), i=27 (hard, same-size
Galvin witness). Calibration n=26, i=13 has two known nonisomorphic
counterexamples. Paper initially fails i=27; epoch-five elite 50k
contains only 42,608 relabelings of path and 7,392 single-leaf variants.
Path replacement later discovers six counterexamples, none Galvin;
score jumps from strongly negative to ~1e9 in epoch seven.

First use [existing code/data](https://github.com/ericgramos/TreeUnimodalityPatternBoost)
to reproduce the published pipeline. Audit generated graphs before/after
local optimization, not just final elite corpus. Compare random
Prüfer proposals, local search, annealing, published PatternBoost,
and small policy gradient learner. Do not call a change in reward
the same intervention as a change in exploration.

Three separate scoring baselines, shared exact acceptance predicate:
1. published signed defect D_i = a[i-1]*a[i+1]-a[i]^2;
2. terminal normalized defect D_i/(a[i-1]*a[i+1]+a[i]^2), explicit
   handling of out-of-support/zero denominators;
3. binary terminal success, primary RLVR once mixed reward groups occur.

Raw negative score can be made less negative by shrinking all
coefficients rather than approaching a violation. Path bias might
be a scale artifact. Normalization removes overall scale, not all
geometry effects. If normalization resolves the failure, that is
a worthwhile finding without any proposed exploration intervention.

Metrics: first hit, exact nonisomorphic hits per verifier query,
actual search/evaluator costs, independence number, generated versus
retained diversity, probability of successful families across
checkpoints. AHU canonicalization of unrooted trees treats isomorphic
relabelings as same mathematical object (not semantic equivalence
for different trees). Audit uniform labeled vs unlabelled distribution
and distinct-label probability, not just count labels.

## Experiment B: mathematical landscape diagnostics (cheap)

At path, near-path and exact known witnesses, enumerate legal single
edge-swap neighbors; separately consider single-symbol Prüfer edits.
Measure exact defect and normalized defect distributions, fraction
accepted, sign-change rate. Sample longer unconstrained excursions
to assess valley evidence, not prove barrier from failed sampling.
Compare probability of relabelings of the same graph with other
classes. Determine whether collapse comes from reward geometry,
local move landscape, representation bias, or learning dynamics.
Only call a local optimum when all specified one-step neighbors
are measured. A known witness is not required to be found by agent;
a new nonisomorphic witness is equally valid.

## Experiment C: intentional multiple mathematical violations

Hypothesis: learning effective single-violation construction does not
necessarily yield capacity to construct multiple violations under the
actual target reward; can an ordinary small learner discover such
composition? First establish ordinary performance under the task itself,
not extrapolate from PatternBoost's single-index objective.

Start with independence n=70 >=2 violations (known witness as above);
domination n=101 >=2 as second domain. Binary terminal goal count>=2.
Dense baseline (separate factor) second-largest normalized violation
margin, requiring valid interior support, exact integer signs. Also
track #violations without rewarding particular chosen indices or motifs.
Train single-violation and direct double-violation baselines separately;
possible single-to-double transfer comparison, but eval task unchanged
within each arm. Evaluate across n and target counts with independently
certified feasibility. Never infer a size is feasible merely because
an asymptotic theorem exists. Direct multi-target ordinary RL may
already solve it; positive outcome is informative.

## Candidate interventions (not committed; choose after diagnosing)

1. **Structural duplicate balancing:** in published dense-score
   learning, group by exact unlabelled isomorphism; balance or withhold
   overrepresented objects irrespective of their shape, compare equal
   random withholding and ordinary. For binary RLVR, original Restriction
   means mask dominant *correct* modes only; failure balancing is a
   separate sampling mechanism, not original hard exclusion. If all
   correct groups empty, no learning signal created by masking.
2. **Native recombination:** independent lineages discover trees; sample
   arbitrary equal-size rooted subtree donors from own or other lineage,
   preserve size and tree validity, continue ordinary objective. Compare
   independent lineage/no crossover, random donors (including generated
   nonelite), generic matched-cost edge edits. No handpicked useful
   subgraphs or analyst witness. Does composition of earlier discoveries
   become useful, or just make search stronger? Evaluate frozen unaided
   policy from standard starts, new n/count; charge all generation costs.
3. **Outcome-neutral state continuation:** start editable tree policy
   from archived failed and successful trees, compare uniform tree
   starts, ordinary states and coverage-only sampling. Relevant only
   if diagnostics show state concentration. Do not supply solvability
   oracle whose computation itself solves construction, and do not
   compare editing vs autoregressive generation as just reset changes.

Candidate 1 is simplest given actual duplicate collapse; candidate 2
most creatively interesting if multi-violation ordinary learning has
headroom; candidate 3 conditional on evidence. None rewards branching,
independence number, named subtree family or similarity to known witness.

## Verification and compute

Exact arbitrary precision rooted DP, independent small-n subset
enumeration, root/label invariance tests, valid connected acyclic
n-vertex graph checks. Independence: polynomials for root chosen/not
chosen. Domination: chosen, internally dominated, requires parent.
Do not silently replace big integers with approximate floating scores.
Use exact comparisons even if normalized training score uses floating
conversion. Keep verifier separate from learned policy, no learned judge.

CPU pilot can screen raw generation, local neighborhoods, exact evaluator
throughput; then estimate realistic training budget. Paper reports
5–15 min per epoch on RTX Ada5000, 1 to several hours per run. No
timing for our implementation established. Compare matched actual
verifier calls and local-search work, not solely epochs/proposals.
Record hypothesis and discriminating decisions before training.
