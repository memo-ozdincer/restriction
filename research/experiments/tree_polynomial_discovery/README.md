# Exact tree-polynomial discovery experiment

## Registered hypothesis before training

The published independence-polynomial learner concentrates on path-like
trees while targeting a verified property at n=56, i=27, although a
mathematically different witness exists at that same size and index.
The raw signed defect can itself favor small-coefficient incorrect
objects. Distinguish reward-scale effects from discovery and selection
effects rather than presume dominant exclusion or exposure is necessary.

1. Recheck exact known witnesses and native polynomial recurrence.
2. Examine existing PatternBoost corpus and local neighborhoods of
   representative paths and known witnesses. Compare raw/normalized
   scores and structural isomorphism, not mere labeled sequence counts.
3. Establish CPU-scale random, local-search and ordinary small-policy
   baselines at n=26,i=13, n=56,i=28 and n=56,i=27. Compare published
   raw terminal margin, scale-normalized terminal margin, and binary
   success as separate objectives, not a single-factor intervention.
4. Directly target >=2 violations, independence n=70 and domination
   n=101, with certified feasible witnesses held out. Prior paper
   optimized one index, so its failure to find two is not evidence of
   failure under the new objective.
5. Compare structural abundance balancing vs ordinary and random
   matched withholding; generic mathematically legal recombination vs
   ordinary independent samples/matched random edits only within the
   same objective and learner. Evaluate the final ordinary generator
   without extra search; distinguish discoverer/search performance
   from acquired policy capability. A fixed-size learner cannot establish
   cross-size transfer. State-continuation is conditional on observed
   state concentration; do not introduce a new edit interface and call
   it a pure reset comparison.

Main decisions: whether scale normalization changes path attraction;
whether ordinary learning has nonzero signal and meaningful discovery
headroom; whether structural balancing or generic recombination
finds different verified objects or only improves search; whether
multiple-violation direct search succeeds without mathematical motifs.
Negative evidence is informative; no extra seeds just to polish.

Sources and exact anchors:
[prior proposal](../../TREE_POLYNOMIAL_DISCOVERY_EXPERIMENTS_2026-11-27.md),
[paper](https://arxiv.org/html/2510.18826),
[domination paper](https://arxiv.org/html/2605.02193v1),
[PatternBoost tree data](https://github.com/ericgramos/TreeUnimodalityPatternBoost).
All graph objects here are benign abstract undirected trees.
Use exact integer verification and unlabelled tree canonicalization.
No known analytical witness injected into training, no heuristic
motif reward or learned judge. In contrast with the original Lean
project, this is a new independent small CPU policy experiment.

## Operational readiness

Local historical Lean/GPU preflight ran and reported missing CUDA/Ray/
scratch Lean environment on Mac, irrelevant to this independent CPU
experiment. Local Python 3.14.6/NumPy 2.4.2 available; Trillium CPU
SSH verified, def-zhijing association valid, debug 1h, 192 cores/node.
Use one job and exact source checksums; no training before local tests.

## Registered CPU panel

Five targets, three paired seeds (42–44), 186 runs, each exactly
131,072 training verifier calls (24,379,392 total). See panel.py for
complete arm registry and budgets; 128 candidates per group, 1024
ordinary batches, local search initial batch counted, pattern-lite
3 local edits per generated proposal and 256 batches. Fresh generator
evaluation every 128 ordinary updates or 32 pattern-lite
updates, 256 samples per checkpoint including initial; nonlearned
methods' fresh evaluations are uniform, not search outputs.
No cross-size generalization claim: small fixed-size categorical
autoregression uses position, previous-token and token-count logits.
CEM is elite-imitation search, not on-policy policy gradient. Pattern-lite
is a deliberately smaller comparator, not exact published PatternBoost
replication. Balancing dense terminal samples uses within-batch exact
tree IDs; matched withholding matches counts within each arm's batch.
Recombination uses each run's own prior FIFO archive, not cross-lineage
exchange. Random donor/primitive edits controls match augmented fraction
and verifier budget, not realized edge edits or CPU time. All arms report
actual counters. Three seeds support discriminating behavior, not
publication-scale statistics.

13 tests pass locally (verifier and learner); independent review found
no blocking correctness issue. Exact polynomial-only local throughput
26/56/70 independence ~21.9k/7.6k/5.35k/s, 101 domination ~1.4k/s;
learner end-to-end smoke ~6715,2551,740/s at 26,56,101 respectively.

## Submission

Trillium job 2956895 on def-zhijing/debug, requested 192 CPUs, 40-minute
limit. Isolated remote directory
`/scratch/memoozd/rrl/tree-poly-pilot-20261127-6f0f8dc`.
Source snapshot commit 6f0f8dc; all six source SHA256 checks passed
remotely before submission. Monitor this job; do not resubmit blindly.

## First-panel results and numerical correction

Job 2956895 completed exit 0 on tri0002, 192 CPUs in 5m48s. All 186
run records and source/output checksums retrieved. Every one of
24,379,392 assigned-goal training verifier calls returned failure;
all final unassisted samples failed. One off-target violation at
index28 found by a pattern-lite raw run assigned i27 (exact margin
48,424). All binary PG runs had zero updates. For fixed-index raw PG
at n26/i13, n56/i27 and n56/i28, best tree was a path in all nine runs;
raw policy outputs overwhelmingly/all paths. Dense normalized CEM
converges to stars, not solutions; normalized PG produced similar
collapse in original runs, but see D-170 numerical issue below.
Structural balancing and recombination did not produce target wins.
This is a finite-budget result for small fixed-n categorical policies,
not a statement about ordinary RL in general.

Independent replay initially flagged 32 of 33 normalized-PG runs:
16,120 artificial updates on exactly constant-score batches from
floating-point variance roundoff. See [D-170](../../DECISIONS.md).
Preserve all original outcomes and mark affected PG comparisons
provisional. Corrected exact equality guard and regression test at
commit 2149260; all 33 matched normalized-PG reruns submitted as
job 2957103, def-zhijing/compute, 192 CPUs, 15-minute limit, remote
`/scratch/memoozd/rrl/tree-poly-pg-guard-20261127-2149260`, seven
source checksums passed. Initial job unaffected CEM and binary arms
remain valid.

Separate [historical data/landscape audit](AUDIT_RESULTS.md):
raw path exact local optimum, normalized escape directions abundant;
99,980 fresh valid historical generator proposals zero counterexamples;
same local solver at nearly matched budgets 12/100 learned starts
versus 4/100 uniform. [Complete-cycle followup](CYCLE_PLAN.md) launched
as job 2957070. The positive historical finding motivates stronger
local-search comparisons instead of blind repeats.
