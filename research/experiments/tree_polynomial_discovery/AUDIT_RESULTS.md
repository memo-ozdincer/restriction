# Offline audit of published tree discovery and score landscape

Ran locally with Python arbitrary-precision integer independent-set
polynomial DP (separate implementation from environment.py) and exact
unlabelled AHU canonical forms. See [registered diagnostic](AUDIT_PLAN.md),
[audit implementation](audit.py), [machine-readable evidence](audit.json).
The cross-check independently enumerated all vertex subsets for 220
random trees (n=2–12), matched shared verifier coefficients, and
checked both canonicalizations invariant under relabeling. Known Galvin
T(5,5) witness independently scores 332,324,762,280 at n=56, i=27.
No learner used the witness.

## A concrete explanation for path collapse

All labeled one-step neighbors under two different move languages
were exhaustively evaluated at the n=56 path. Under the paper's raw
signed determinant (adjacent product minus squared middle), the path
is a weak local maximum at either target index. Under scale-normalized
terminal determinant, most neighboring edits improve at index 27.

| Anchor and target | Edits | Labeled neighbors | Raw strictly better | Normalized strictly better | Verified hits |
|---|---|---:|---:|---:|---:|
| Path i=27 | Edge-delete/reconnect | 29,205 | 0 | 26,828 (91.86%) | 0 |
| Path i=27 | Single Prüfer token | 2,970 | 0 | 2,316 (77.98%) | 0 |
| Path i=28 | Edge-delete/reconnect | 29,205 | 0 | 10,584 | 0 |
| Path i=28 | Single Prüfer token | 2,970 | 0 | 756 | 0 |
| Galvin i=27 | Edge-delete/reconnect | 6,495 | 200 | 0 | 2,700 |
| Galvin i=27 | Single Prüfer token | 2,970 | 40 | 0 | 1,206 |
| Galvin i=28 | Edge-delete/reconnect | 6,495 | 3,970 | 3,970 | 3,670 |
| Galvin i=28 | Single Prüfer token | 2,970 | 1,747 | 1,748 | 1,372 |

Different labels often represent identical trees: path edge-neighborhood
contains 3,360 exact unlabeled classes; Galvin edge-neighborhood contains
only 25. Positive Galvin neighbors are therefore not independent
mathematical solutions. Raw path scores: -11,556,181 (i27), -841 (i28).
Normalization is D/(adjacent product + midpoint squared), calculated
as exact rational with undefined denominator excluded. Path i27
normalized -0.53973; Galvin +0.33558. Thus normalizing the score
genuinely changes local geometry. This does not prove long valleys
or that normalization makes ordinary RL discover counterexamples.
Galvin is a local maximum under normalized objective at i27, but
many neighbors are already valid, and the task predicate does not
require optimizing the positive margin.

## Published 60-vertex positive result: autonomous generator vs full pipeline

Source [Ramos–Sun artifact](https://github.com/ericgramos/TreeUnimodalityPatternBoost/tree/79ef336cce13b2b6bcd68fce2f4f6fa12a8b69a5/60_vertex_output).
All samples evaluated at n=60, index30, with zero-based canonical
mathematical verifier. Source SHA256 and exact best-score triples
in audit.json. Source README describes the final decoded artifact as
150k transformer outputs, but pinned fc_loop.py explicitly prepends
50k prior elite inputs before appending 100k fresh generation requests.
The actual output has 149,999 rows. We verified that **the first
50,000 rows are exactly equal, in order, to the prior elite file
search_output_10.txt**. Do not treat mixed-file acceptance as
autonomous generation.

| Population | Valid / rows | Valid i30 hits | Distinct unlabeled hit trees | Distinct unlabeled all |
|---|---:|---:|---:|---:|
| First epoch local-search elites | 50,000/50,000 | 1 | 1 | 50,000 |
| Prior final-epoch elite prefix | 50,000/50,000 | 37,688 | 37,688 | 38,421 |
| **Fresh final transformer suffix** | 99,980/99,999 | **0** | **0** | 97,287 |
| Final optimized/pruned elites | 50,000/50,000 | 39,766 | 39,766 | 43,595 |
| Independent uniform labeled trees | 10,000/10,000 | 0 | 0 | 10,000 |

No group had any multiple-violation tree. The final elite positives
exactly match the published distribution count; best raw score =
991,960,220 (reported distribution rounds to 9.919602e8).
The fresh suffix includes 19 invalid rows and 577 genuine paths.
No positive examples are duplicated up to unlabeled isomorphism in
the retained elite sets, even though negative shapes can dominate.

**The model learns something, but never independently generates
an accepted object in this recorded final fresh suffix.** Its
starting distributions are shifted relative to uniform:

| Metric, n60 i30 | Fresh transformer | Uniform |
|---|---:|---:|
| Median independence number | 32 | 34 |
| Median raw determinant | -14,462,919,580 | -1,098,527,353,719,307 |
| Median normalized determinant | -0.30225 | -0.13983 |
| Best normalized determinant | -0.03451 | -0.07306 |

The learned median raw defect is ~76,000 times smaller in magnitude,
while median normalized score is worse. This is consistent with the
raw-score scale explanation. It does not establish that all learned
behavior is unhelpful: better tail normalized values and shifted
starting structures might help the local optimizer. Test directly
with matched local verification budget, rather than attributing
the pipeline's positives to model generation. A full local optimizer
also carries prior successes unchanged (source skips already-positive
inputs); fresh and optimized outputs are populations, not paired.

## Local search provenance and conditional followup

Pinned source files:
- [fc_loop.py](https://github.com/ericgramos/TreeUnimodalityPatternBoost/blob/79ef336cce13b2b6bcd68fce2f4f6fa12a8b69a5/PatternBoost/fc_loop.py),
  final generation writes elite tokens into out.txt before sampling;
  decoder preserves line order.
- [problem_erdos_NoPath.jl](https://github.com/ericgramos/TreeUnimodalityPatternBoost/blob/79ef336cce13b2b6bcd68fce2f4f6fa12a8b69a5/problem_erdos_NoPath.jl),
  greedy search lines 200–290: skip positive inputs, shuffle all
  initially absent edges once (order_edges=-1), add each edge,
  score every deletion of its fundamental cycle including no-op,
  greedily maximize score, count only non-no-op swaps, stop after
  10 accepted swaps or exhaustion. No early stop mid-search on
  finding positive. NoPath conversion maps paths/invalid codes to
  stars; actual historical reward included a star penalty condition.
- [search_fc.jl](https://github.com/ericgramos/TreeUnimodalityPatternBoost/blob/79ef336cce13b2b6bcd68fce2f4f6fa12a8b69a5/PatternBoost/search_fc.jl),
  applies local search and database deduplication; 64k is processing
  chunk size, not total verifier budget.
- [run log](https://github.com/ericgramos/TreeUnimodalityPatternBoost/blob/79ef336cce13b2b6bcd68fce2f4f6fa12a8b69a5/60_vertex_output/train.log):
  10 epochs, 100k new samples per epoch, 50k elites, transformer
  4 layers / 64 embedding / 8 heads, 64 local-search threads,
  10 swaps each, about 9 hours. Checked-in NoPath default N=60
  refers to Prüfer length (62 vertices); saved run uses length58,
  so reconstruct actual n and index, not static default.

A reproducible 1,000 + 1,000 proposal bank is prepared outside Git
at /tmp/tree_polynomial_patternboost_79ef336/sample-1000.json,
SHA256 4c8d4d990077fb7a91e3fb7a059a751429cad77d327b548b193a2f4a9a9efeaa,
via `audit_local_search.py --prepare`, pin/source hash in manifest;
uniform independently seeded. Sample excludes invalid rows and
entire prior elite prefix, but includes any valid fresh paths.
The 100+100 first panel uses exact verifier-call cap 500 per start,
same shared mechanical optimizer for both arms. The historical
NoPath penalty is not imposed by default, to diagnose ordinary
proposal usefulness rather than replica of original specific
penalty. Matched cap, not guaranteed equal actual calls: early
swap limit and full-cycle requirement vary realized counts.

## Local optimizer probe — actual learning of useful starts

The registered conditional test compares exactly the same random-order
cycle-deletion local optimizer on the first 100 fresh proposals and
100 independently uniform proposals from the deterministic bank.
No witness included as input. Both use a maximum 500 polynomial calls
per start, no path reset, skip initial success, and do not stop on a
successful intermediate. Cached original tree score saves a repeated
no-op evaluation; ties randomized; full cycles evaluated or not at all.
This is a transparent adaptation, not byte-for-byte reproduction of
the Julia implementation. A separate independent exact replay verified
all saved witnesses and terminal hit scores.

| Budget control | Fresh final hits | Uniform final hits | Fresh calls | Uniform calls |
|---|---:|---:|---:|---:|
| Original-style 10 accepted swaps, cap500 | 1/100 | 0/100 | 22,680 | 12,457 |
| Nearly matched calls (1000 swap cap, 500 call cap) | **12/100** | **4/100** | 49,097 | 49,329 |

The first comparison has a severe actual-compute mismatch; the second
is a registered confound correction on the same 100+100 start bank.
It runs in ~7.7 s with 4 local Python workers. Each start is initially
incorrect. All 16 final hit trees in the matched comparison are
nonisomorphic within their group; all 342 stored intermediate witness
records across groups independently confirmed and nonisomorphic.
The first matched fresh hit starts do *not* rely exclusively on low
independence number: stratified counts (small, exploratory) fresh
alpha31 2/34, alpha32 4/33, alpha33 5/23, alpha35 1/2;
uniform alpha32 1/4, alpha33 1/20, alpha34 1/32, alpha35 1/25.
Fresh final median raw score -63,504 vs uniform -1,530,427.

This is preliminary but valuable evidence: **the published transformer
outputs do not satisfy the goal independently, yet their distribution
can make an unchanged local solver succeed more often** under similar
actual exact evaluation budgets. It is inappropriate to characterize
the learned policy as having learned nothing, or as already being an
autonomous counterexample generator. Its apparent useful experience is
a strong example of the distinction between policy capability and
inference-time search; the experiment measures proposal distribution
quality, not RLVR gradient acquisition. More trials purely to achieve
significance are not needed; a motivated followup might ask whether
this advantage persists after controlling initial independence number,
or whether learned distribution local efficacy transfers to index29.

Results:
- [10-swap pilot](audit_local_search.json)
- [Nearly matched 500-call pilot](audit_local_search_matched.json)
- [Script](audit_local_search.py)

Reproduce (after audit.py download and verified-prefix split):

```sh
python3 audit_local_search.py --prepare
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 audit_local_search.py --limit 100 --budget 500 --max-swaps 10 --workers 4
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 audit_local_search.py --limit 100 --budget 500 --max-swaps 1000 --workers 4 --out audit_local_search_matched.json
```

Bulk source and sample kept in external temporary cache; pinned URLs
and SHA256 in audit.json and local comparator results permit retrieval.
