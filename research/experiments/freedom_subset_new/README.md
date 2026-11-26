# Whole-candidate subset-sum freedom experiment

Registered before sampling. Hypothesis: for a one-shot exact combinatorial
optimization task with no native sequential state, temporarily loosening the
terminal constraint can expose useful whole-candidate learning signals,
which may increase exact success after restoring the constraint. Arbitrary
start states are irrelevant because a policy produces a complete bit vector.

Fixed 20-item positive integer subset sum, seed 20261127, target generated
from a hidden uniform subset; exact uniqueness checked by meet-in-middle.
No witness shown to learner. Factorized Bernoulli policy (20 logits), terminal
REINFORCE, identical initialization, optimizer, 600 batches of 256 full
candidates, 2048 fresh exact evaluations at checkpoints. Eight paired seeds
42..49 as an initial compact mechanism panel, not publication replication.

Arms:
- exact throughout;
- tolerance-only (binary abs(sum-target)<=16384 throughout);
- tolerance-switch (same tolerance first 30%, then exact);
- tolerance-anneal (geometric decrease to zero by 30%, then exact);
- random-bit constraint switch (each early batch sees a fresh mask of six
  uniformly chosen bits of the numerical sum; exact after 30%);
- random-bit constraint anneal (mask size expands to all bits by 30%).

All conditions compute full integer sum, no per-variable or per-step reward.
Relaxed terminal predicates explicitly change the training objective; they
are crutches, not an unchanged-verifier state intervention. Every final
evaluation checks exact equality. All candidate-generation budgets match.
The test distinguishes whether nearby scalar sums or arbitrary subsets of
the exact constraint provide transferable credit. No target-dependent
choice of bit positions or human-selected partial solution. Full candidate
state, not an agent trajectory; no reset.

## Results

48 runs completed. At final exact evaluation, 47 runs had zero
hits in 2,048 trials. Seed 49 tolerance-anneal achieved 398/2,048,
with 267 exact training hits (first observed at step 480, >300
updates after the relaxed objective ended). Early relaxed training
produced only two positive rewards. All other variants failed to
produce a comparable policy. Tolerance-only sometimes accumulated
tens of thousands of relaxed hits without learning exact equality.

The exact uniqueness and final policy probability audit finds 19.92%
for the breakthrough policy; next best final probability across
all arms is 0.00563% (tolerance-only). Independent fresh sampling
and scalar sum verification yield 408/2,048 exact successes.
This is a rare outcome, not a reliable training method. A full
candidate observation contains no sequential state, and changing
the terminal criterion is an explicit intervention in the objective.
The early scalar interval is still a human-chosen geometry; random
bit masks intentionally avoid ranking or pointing to useful bits,
but performed worse. None receive intermediate credit or reference bits.
See results.json and audit.json; reproduce run.py and audit.py.

Audit of random-bit relaxation: for an output differing from target in
m of W bit positions, a uniformly sampled size-k mask accepts with
C(W-m,k)/C(W,k) (zero if W-m<k). It is therefore implicit Hamming
shaping in expectation, despite binary individual rewards. Tolerance
similarly supplies a human-defined scalar closeness predicate. Neither
should be advertised as unchanged-verifier RL. They are separate
constraint-removal experiments.
