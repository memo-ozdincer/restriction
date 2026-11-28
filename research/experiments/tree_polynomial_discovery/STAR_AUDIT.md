# Opposing terminal-score traps: exact 56-vertex star diagnostic

## Registered hypothesis and decision

The first training panel observed raw-score learners concentrating on paths
and normalized-score learners concentrating on stars, despite no target
successes. The earlier exhaustive path audit demonstrated that all legal
one-edge swaps and one-symbol Prüfer changes fail to strictly improve
the raw path score, while many improve normalized score.

Hypothesis: normalized score produces an opposing structural local maximum
at the star. Evaluate the complete same two neighborhoods at the 56-vertex
star, targeting i=27 and i=28, using exact integer arithmetic and rational
normalization; compare strict better, equal, worse counts against raw scores.
Counterexample: if any valid normalized neighbor improves, star convergence
cannot be explained as a one-step normalized local maximum in that move
language. This is a direct follow-up to the observed opposing traps,
not an attempt to improve statistical precision.

Cross-check each evaluated polynomial using the independent historical
audit implementation and the shared verifier, and compare to closed-form
star and near-star polynomials. Every nontrivial one-edge star swap must
produce the same unlabeled near-star structure (one leaf attached through
another leaf, other star leaves unchanged). One-symbol Prüfer edits to
the all-center code likewise produce exactly this structure.

This diagnostic uses no training or known solution as input. It cannot
establish a global optimum, barrier height, or learning dynamics beyond
the specified neighborhoods.

## Result

The registered hypothesis is verified. Both neighborhood languages
contain 2,970 distinct labeled trees, each representing exactly one
unlabelled near-star isomorphism class. Every polynomial was checked
against two independent DP implementations and the analytic formula.

| Anchor and index | Move language | Neighbors | Raw strictly better | Normalized strictly better | Normalized strictly worse | Hits |
|---|---|---:|---:|---:|---:|---:|
| Star i27 | Edge-delete/reconnect | 2,970 | 2,970 | 0 | 2,970 | 0 |
| Star i27 | Single Prüfer token | 2,970 | 2,970 | 0 | 2,970 | 0 |
| Star i28 | Edge-delete/reconnect | 2,970 | 2,970 | 0 | 2,970 | 0 |
| Star i28 | Single Prüfer token | 2,970 | 2,970 | 0 | 2,970 | 0 |

For the star on n vertices its independence polynomial is
`(1+x)^(n-1) + x`. Each neighbor has independence polynomial
`(1+2x)(1+x)^(n-3) + x(1+x)`: condition on whether the center
is selected. With the center excluded, an isolated edge is left
alongside n-3 isolated vertices. With it selected, only the detached
outer leaf is available.

Let normalized score be D/(a_(i-1)a_(i+1)+a_i^2). Exact fractions:

| Index | Star normalized | Near-star normalized |
|---|---:|---:|
| 27 | -1/28 | -31/851 |
| 28 | -1/28 | -3431/94067 |

The star's normalized margin is -0.0357143 at both indices;
all single-move neighbors have worse margins (-0.0364277, -0.0364740).
The raw margins strictly improve from the star's
-1,008,663,239,761,398,285,522,521,879,200 to
-599,529,423,170,576,567,725,452,673,984 (i27) or
-572,020,425,722,538,432,665,747,531,824 (i28).

Combining this with the earlier path audit:

| Score | Path i27 improving edge neighbors | Star i27 improving edge neighbors |
|---|---:|---:|
| Raw determinant | 0/29,205 | 2,970/2,970 |
| Normalized determinant | 26,828/29,205 | 0/2,970 |

**Normalization resolves the one-step path barrier but creates the
opposite one-step star barrier.** The observed opposite learning
concentrations are therefore consistent with exact objective geometry,
not only labeling bias or a lack of rollout width. This does not
show that either anchor is a global optimum or that an ensemble of
reward functions would improve true discovery.

No training launched; 5,940 exact labeled neighbor checks (plus
anchor), 2.96 seconds locally. See [code](star_audit.py) and
[exact evidence](star_audit.json).
