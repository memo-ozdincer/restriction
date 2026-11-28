# Existing-data and exact local-landscape diagnostic

Registered before calculating results. Hypotheses motivated by Ramos–Sun:
1. Their learner's structurally degenerate path preference may partly reflect
   magnitude-sensitive raw signed scores rather than an inevitable local
   search barrier. Compare exact raw and normalized scores and enumerate
   the complete specified one-step neighborhoods at the 56-vertex path and
   known Galvin T(5,5) witness, targeting indices 27 and 28, using both
   edge-delete/reconnect and single-symbol Prüfer edit moves. No claim
   about multi-step impossibility from one-step neighborhoods.
2. Their 60-vertex artifact offers a positive comparison: distinguish
   final raw transformer proposals from optimized/pruned elites, audit
   exact acceptance, unlabeled structure diversity, degree and independence
   number distributions, and compare same-size uniform random trees.
   The hypothesis is that useful output distribution is meaningfully
   shifted beyond random; magnitude normalization may change what is
   retained. This published run is not the 56-vertex failed experiment.
   It cannot establish causality or recreate pre/post matched edits:
   indices of the populations are not paired. Raw versus final elites
   includes local optimization and pruning; do not attribute the entire
   difference to local search.

Pinned source: https://github.com/ericgramos/TreeUnimodalityPatternBoost
commit 79ef336cce13b2b6bcd68fce2f4f6fa12a8b69a5. Files: epoch-1 and epoch-11
elite lists (search_output_1.txt, search_output_11.txt), final raw
transformer-output-decoded.txt and reported distributions. Source is
downloaded to external temporary cache; no upstream bulk data committed.
Audit uses exact independent polynomial DP and unlabeled tree canonical
forms; cross-check shared verifier at small n. Historical labels are
1-based. Recalculate scores with actual sample n=60 index30, while
checked-in Julia source defaults N=60 Prüfer length and thus does not
represent the exact saved run configuration; compare reported counts
with exact reconstruction. Their `NoPath` implementation treats paths
as stars for reward and applies a separate penalty; report actual
mathematical scores rather than conflating this historical behavior
with the verifier. Corpus could contain repeated labels, invalid inputs,
or numerical errors; verify, never assume positive published counts.

Compute cost: <=250k exact polynomial checks and <=100k one-step checks;
no training. Report audit counts, source file SHA256 and elapsed time,
record independently checkable witness examples. Future interventions
conditional on result. A normalized score is diagnostic reward change,
not a same-reward exploration intervention.

**Upstream clarification discovered during audit:** Although the README
calls the final decoded output raw transformer samples, the pinned
fc_loop.py writes the prior 50k elite training examples into out.txt and
then appends fresh samples before decoding. Thus the 149,999-line mixed
file is not an independent fresh generation. Verify the exact prefix
against search_output_10.txt, then audit the retained elite prefix and
fresh suffix separately. This requires another ~150k exact checks,
motivated by resolving the now-observed confound, not replication.

**Conditional followup (now motivated by observed zero fresh successes):**
The final fresh decoded suffix contains no counterexamples although raw
scores substantially improve over uniform trees. Test whether this
learned proposal distribution nevertheless enables the same local
optimizer to discover more accepted examples than uniform Prüfer starts.
Use deterministic 1,000-row uniform sample from valid fresh suffix
(exclude prior elites, verify exact prefix match), independent uniform
1,000-code bank. First 100 per group, paired optimizer RNG by within-group
row, same 500 actual-verification upper budget per start and same
random-order cycle greedy optimizer (10 accepted changes), historical
NoPath mapping optionally enabled in both. Report actual calls since
maximum cap and accepted-change early exit differ. A full-budget/path
reset variant requires meaningful outcome, not merely more seeds.
Retained witnesses used only for output checking.

**Matched-budget correction after first pilot:** 10-swap variant yields
one fresh and zero uniform hits but uses 22,680 versus 12,457 verifier
calls. This large realized-compute imbalance motivates repeating the
same fixed 100+100 starts, same RNG and optimizer, with a nonbinding
max-swaps=1000. Hypothesis: learned start distribution improves hit rate
even when actual candidate calls are nearly equal; this panel resolves
the observed confound. The original-style 10-swap results remain
archived separately. Do not draw conclusions from one hit alone.
