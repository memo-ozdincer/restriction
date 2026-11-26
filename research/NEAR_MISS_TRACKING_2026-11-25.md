# Tracking pre-RL near misses across checkpoints

## Prospective analysis registration

Hypothesis: among C0 failures with an observed accepted one-line neighbor,
ordinary GRPO preferentially retains corrected forms while losing some
near-miss families; alternatives C2/C3 may retain different families.
A competing explanation is finite sampling alone. Use an equal-size independent
C0 reference panel (first 64 samples discover, last 64 observe; first 64 samples
of each trained model observe). Also report full 128-sample descriptive tracking
of the previously identified 1,114 unique C0 failures. No new model or verifier
queries, no tuning on outcomes.

Identity is exact theorem statement/context and literal proof lines.
Each distinct original rejected body is one unit, not each pair or occurrence.
Require resolved original Lean rejection and at least one independently
accepted sibling with a single nonblank line inserted, removed or replaced.
Exclude contradictory identical outcomes. For every such failed body, freeze
ALL accepted one-edit siblings. Track exactly the original rejected text and
any accepted sibling after training: corrected-only, both, failure-only,
neither; unresolved exact original matches separately. A second, stricter
interpretation selects pairs with at least two identical unchanged nonblank
non-fence lines (conservative lexical proxy, comments not fully parsed).
For these units track any accepted or resolved rejected one-edit neighbor
sharing the unchanged skeleton, including the original/known corrected bodies;
this is syntactic family recovery, not semantic strategy identity. Report
both original/known repair exact matches and scaffold-based matches.

Characterize each repair lexically with precedence: scope/induction, missing
line, extra line, same tactic head with changed argument, different tactic
head, formatting/comment, other. These are descriptions of edits, not evidence
of the true semantic source of errors. If several siblings yield different
categories, report ambiguous rather than assign opportunistically. Report
results by repair category and retained-line count. Preserve exact paired texts
and IDs, stratified counts, and examples. No causal attribution for C1/C3
optimizer confound, and absence in finite sampling is not capability erasure.

## External replication registration

The public autores V1.5-RL MiniF2F bank contains exactly 4 sampling attempts
for each of 488 roots, with structured verifier results. Its 467 shared
statements match our C0 statements byte-for-byte. Compare its published
RL model to our pristine public V1.5-SFT, not to its unknown actual training
parent run; the released model family is the same, generation settings differ.
Hypothesis: near-miss exact correction and family loss can be observed relative
to an equal-four-draw C0 control. Discover on first 124 C0 samples for each
shared theorem, then observe last four C0, first four C1/C2/C3, all four public
V1.5-RL. Keep resolved negatives, exclude system errors. Match the verifier's
actual code body (C0 strips completion code fence, external verified_code must
contain exact header and theorem); normalize only trailing newline. As a
sensitivity normalize comments/whitespace via existing project canonicalizer,
explicitly a syntactic comparison. Different sample sources, budgets and
verifier environments prevent causal claims; these are independently published
proof outputs from a known small model on identical statements.

## Internal results

All four proof-log SHA-256 hashes and 467 shared theorem statement/context
pairs authenticate. Each condition uses 59,776 registered proposals; 128
physical padding rows excluded. Full discovery recovers exactly the prior
1,114 distinct near misses across 219 roots. Of these, 408 across 137 roots
have at least two retained lexical proof lines (the strict cohort).

### Exact known repairs, full 128-draw evaluation (1,114 units)

| Condition | Corrected only | Both | Failed only | Unobserved |
|---|---:|---:|---:|---:|
| C1 | 436 (39.1%) | 15 (1.3%) | 22 (2.0%) | 641 (57.5%) |
| C2 | 273 (24.5%) | 9 (0.8%) | 11 (1.0%) | 821 (73.7%) |
| C3 | 440 (39.5%) | 15 (1.3%) | 10 (0.9%) | 649 (58.3%) |

This is recurrence of the exact known accepted alternative, not conversion of
a particular sampled trajectory; each was already reachable in C0.

### Scaffold recovery, full 128-draw evaluation (408 strict units)

| Condition | Corrected only | Both | Failed only | Unobserved |
|---|---:|---:|---:|---:|
| C1 | 173 (42.4%) | 77 (18.9%) | 22 (5.4%) | 136 (33.3%) |
| C2 | 166 (40.7%) | 70 (17.2%) | 30 (7.4%) | 142 (34.8%) |
| C3 | 156 (38.2%) | 118 (28.9%) | 16 (3.9%) | 118 (28.9%) |

C3 recovers more scaffolds with both positive and negative variants. Equal-root
weighting gives unobserved 37.7% C1, 43.0% C2 and 37.7% C3; do not infer a
consistent C3-over-C1 retention advantage from body-weighted counts alone.

### Equal-sampling control, first 64 C0 discovery, 64 independent observations

486 discovered units across 175 roots, of which 149 strict units across 84
roots. Exact accepted siblings appear in 87/486 unchanged C0 observations,
119/486 C1, 74/486 C2, 112/486 C3. Exact failed-only/both/unobserved in the
summary. Thus the apparent GRPO correction gain persists against a same-model
resampling control, but is concentrated in short proofs.

| Condition | Corrected only | Both | Failed only | Unobserved |
|---|---:|---:|---:|---:|
| C0 held-out | 45 (30.2%) | 40 (26.8%) | 14 (9.4%) | 50 (33.6%) |
| C1 | 50 (33.6%) | 28 (18.8%) | 7 (4.7%) | 64 (43.0%) |
| C2 | 57 (38.3%) | 15 (10.1%) | 8 (5.4%) | 69 (46.3%) |
| C3 | 51 (34.2%) | 31 (20.8%) | 6 (4.0%) | 61 (40.9%) |

**Key pattern:** for strict families, corrected-only increases while
correct-and-failed coexistence decreases; broader recovery declines relative
to resampling C0. C1 has 26 families observed in C0 but absent after RL and
12 reverse cases; C2 30/11; C3 26/15. This is observed finite-budget
redistribution, not evidence of erased capabilities. Equal-root unobserved
37.4% C0, 49.6% C1, 54.5% C2, 47.8% C3 corroborates the direction.
All exact original unresolved matches are zero.

### What changes in the proof

Full cohort lexical categories: 560 ambiguous (different accepted neighbors
imply different edit categories), 275 different tactic head, 224 same tactic
head with changed args, 24 extra line, 15 scope/case-head edits, 12 other,
4 missing line. 706 short units lack two unchanged lexical lines; do not
interpret their replacement as preservation of mathematical strategy.
Actual Lean failure messages are not retained in these historical logs, so
the following are concrete text-level repair mechanisms, not a diagnosis of
all failures.

- **Redundant step:** algebra_2varlineareq_xpeeq7_2xpeeq3_eeq11_xeqn4
  removes one duplicate `apply Eq.symm`, preserving seven lines. All trained
  conditions recover accepted scaffold only.
- **Missing mathematical premise:** algebra_amgm_faxinrrp2msqrt2geq2mxm1div2x
  changes the final nlinarith argument from `h₁` to
  `sq_nonneg (x - 1 / (2 * x))`; six lines unchanged. All recover accepted only.
  This illustrates that one-line repairs can inject genuine mathematical knowledge.
- **Alternative simplifier arguments:** algebra_2complexrootspoly_xsqp49eqxp7itxpn7i
  changes a `simp only` list containing `Normalize.normalize_sq` to
  `simp [sq, add_mul, mul_add, add_comm, mul_comm]`, retains three steps;
  C1 unobserved, C2 and C3 corrected only.
- **Case-base execution:** induction_12dvd4expnp1p20 changes
  `| zero => simp` to `| zero => decide`; five unchanged lines.
  C1 and C2 recover failed-only scaffold; C3 corrected only.
- **Extra rewrite:** aime_1983_p9 deletes `rw [← mul_one x, ← mul_one (Real.sin x)]`
  preserving five lines. C1 unobserved; C2 and C3 corrected only.

See [summary](experiments/failed_proof_corpus_20261125/near-miss-tracking-summary.json)
and [complete record archive](experiments/failed_proof_corpus_20261125/near-miss-tracking.json.gz)
for all paired proposal identities and text. Three synthetic tests pass.
The strict scaffold proxy ignores one position, not arbitrary proof similarity.

## Public DeepSeek V1.5-RL replication

All 467 shared public MiniF2F statements match exactly, and external source
prefix and proof body match the same historical verifier header. The different
verification settings, generation protocol (many explanatory comments),
and very small 4-draw budget substantially limit the comparison.
No public literal matches occur. With the existing comment/whitespace
canonicalizer, 15/1,084 exact corrected-only bodies appear in the public RL
bank versus 27/1,084 in four C0 holdout draws (2 failed-only).
Among 398 strict units, public RL recovers 11 corrected-only (2.8%), seven
failed-only (1.8%), zero both and 380 unobserved (95.5%); C0 recovers 20
corrected-only (5.0%), six failed-only (1.5%), zero both and 372 unobserved
(93.5%). C1 has 44 corrected-only, four failed-only and 350 unobserved. This
does not replicate the C1 exact-correction gain; it is consistent with very
sparse cross-model scaffold overlap and cannot isolate RL from protocol.
No new Lean checks were made. See [external summary](experiments/failed_proof_corpus_20261125/external-tracking-summary.json).

The independently published WM8 SFT/GRPO pair was acquired and authenticated
(32 outputs per problem in its registered headers). These raw JSON releases
contain no compiler verdicts; inline model-predicted feedback is NOT a Lean
verdict. Preserve the two banks locally and pin their revisions. They are not
admitted as a measured pre/post replication until independently verified or
published compiler labels are recovered.

## Independent cross-prover generalization registration

Motivating observation: the internal matched control distinguishes exact
correction from family retention, but the public V1.5 comparison has only four
draws and different output formats. The EPFL-LARA compiler-labeled public
benchmark supplies 68,932 distinct natural candidates across three models
(4B/7B/8B) and two datasets. Test whether multi-line near misses exist across
independent models and whether other models independently reproduce the
repaired form or retained scaffold. No assertion that these models are
pre/post checkpoints of one training run.

Exclude wrong-declaration rows and any sources without exactly one anchored
target theorem named by the problem, with a tactic proof (`:= by`). Require
same literal statement/header in discovery and observation. Record all
exclusion counts. Use distinct candidates, not estimated original proposals
(the published release deduplicates globally). Within each model and benchmark,
discover near misses and classify repair types as above. For cross-model
comparison, restrict to shared exact statement/header and groups with at least
16 retained candidates from each model; use first eight (candidate index order)
for source discovery, next eight for same-model observation, first eight target
candidates for cross-model observation. Repeat source direction for each model;
do not select based on success after observing. Use the frozen literal one-line
and scaffold metrics. Report low support rather than loosening criteria after
results. No new generation or verification.

The literal independent benchmark has far fewer one-line neighbors than the
short C0 corpus. The previously registered public V1.5 analysis showed the
specific comment/formatting confound (zero literal overlap vs nonzero
canonical overlap). Apply the same fixed canonical sensitivity to this
independent benchmark; keep all observation budgets and exact statement/header
matching unchanged. This checks the confound, not a result-dependent increase
in sampling or a new matching threshold.
