# Tensor flip-graph rank slack and Sokoban native state exposure

## Registered hypotheses (before construction or smoke runs)

Both pilots use small finite mathematical environments, exact terminal verification,
and a shared stochastic policy trained by same-start group-relative terminal reward.
A policy can benefit from experience unavailable to ordinary trajectories, but extra
freedom may also dilute signal. The scientific question is whether increased reward
access survives after withdrawing the freedom, under an unchanged ordinary evaluation.
These are mechanism pilots inspired by published methods, not reproductions of their
large-scale learned solvers. No reference solution, distance, or intermediate score
is used in training.

### 1. Tensor algebra: temporary intermediate rank slack

Inspired by flip/plus graph search over exact tensor decompositions in
[Kauers and Moosbauer, 2023](https://arxiv.org/html/2212.01175) and the
[2026 flip-plus graph construction](https://arxiv.org/html/2609.17533v1).
The literature documents rank-constrained connected components and very rare
rank reductions; it already explores rank-increasing plus moves. The pilot
uses 2x2x2 binary tensors, not a 2x2 matrix-multiplication tensor (the latter
is 4x4x4). Each state is a canonical set of nonzero rank-one terms, with
identical terms cancelling over F2. This quotient differs from multiset
representations in the papers; each candidate transition will be independently
checked against the original tensor. Ordinary cap = 4 terms, exposure cap = 5;
both permit the same flip/plus rewrite types, and only rank masking differs.
The goal is a decomposition with the independently certified minimum term
count. The root is a four-term coordinate expansion. Determine the task
mechanically before learning: among 2x2x2 tensors with exactly four nonzero
coordinates and minimum term count 2 or 3, choose the lexicographically
first maximizer of ordinary shortest-path distance to a minimal decomposition,
subject to finite ordinary distance >=2 and strictly greater root-connected
state coverage under cap 5 than cap 4. Exact finite graph enumeration is
an offline audit, not a policy observation or action label. No learner outcomes
are used for instance selection. Horizon is max(8, twice the ordinary shortest
distance). Root start fixed in every condition; rank slack is the sole
intervention. Evaluate from root with cap 4 and same horizon after each
checkpoint. Compare cap4-only, cap5-only, cap5-to-cap4 (switch after 30% of
updates); paired initialization/optimizer/rollout counts and identical reward.
If no eligible tensor exists, report that outcome rather than select a
different case post hoc.

### 2. Sokoban: fixed board and all boxes, native reversible reachability

Inspired by the sparse long-horizon reward bottleneck and simpler-box curricula
in [Feng et al., NeurIPS 2020](https://proceedings.neurips.cc/paper_files/paper/2020/file/2051bd70fc110a2208bdbd4a743e7f79-Paper.pdf).
This is an original small Sokoban-like board, using standard movement and push
rules, no published game assets. All boxes and goals stay fixed in number,
goals and walls stay in place. A random reset is a uniformly sampled solvable
configuration in the *same* board, excluding terminal configurations. Solvable
configurations are enumerated offline using reverse reachability from all
terminal player placements; this gives no distance or solution labels to policy.
Select the root by a deterministic farthest-distance rule, tie-broken by state
tuple order. Root and every reset are reachable to the same terminal checker.
The horizon equals shortest root path + 4, making ordinary success feasible.
Compare root-only, uniform-solvable-only, uniform-solvable-to-root (switch at
30%). Same action set, observation, optimizer, terminal reward, padded
primitive action budget and evaluation. Uniform resets may be closer to goal
than root; measure reset-distance distribution separately from policy.
This is a straightforward reverse-reachability curriculum, substantial prior
art; scientific novelty would come from measured post-removal transfer.

## Budget and decisions

Paired seeds 42-45 for a small discovery panel (only expand if a specific
observed mechanism demands it). Initial 300 updates, 32 same-start groups of
8 trajectories per update, explicit horizon as above. Evaluation 256
ordinary-start trajectories each 30 updates. No success/failure filtering in
training. Record terminal success counts, groups with mixed rewards,
policy action slots, active moves, reset count, evaluation and elapsed time.
A useful signal-access result alone is insufficient: require switched policy
ordinary evaluation to improve compared with root and persistent-exposure
controls before calling transfer. If no arm learns, inspect signal access
and graph geometry before changing horizon or architecture. CPU runnable via
NumPy; no external credentials/model weights. No cluster submission is
authorized by this implementation task; parent coordinates full-node jobs,
per cluster/TRILLIUM_CPU_QUICKSTART.md.

The Sokoban board is fixed before inspection (one-based interior edges are
ordinary walls, G denotes goal). Two boxes and one player occupy arbitrary
distinct non-wall tiles; standard pushing is allowed, pulling never is.

    #######
    #.....#
    #.G#..#
    #..#..#
    #..#G.#
    #.....#
    #######

An additional uniform-all-nonterminal-legal-start-only and corresponding
switch control records whether offline solvability filtering is actually
needed. Illegal move attempts leave the state unchanged and consume a move.
All legal states (including dead ends) remain available to ordinary policy.

## Geometry result and more substantive tensor follow-up (registered before testing)

The 2x2x2 tensor pilot did **not** exhibit sparse initial reward: exact
uniform-policy root success is 0.517505 at cap4, compared with 0.236138 at
cap5 (81 vs 404 accessible representations, shortest distance 3 both).
This is a useful negative geometry control (more reachability, less signal),
not a justification for large training runs.

New question: can temporary rank slack improve learned search over the actual
2x2 matrix multiplication flip graph? Use the standard eight-multiplication
coordinate scheme over F2, goal any exact rank <=7 scheme (Strassen upper
bound and published optimum). The tensor is 4x4x4, and the generator uses
the papers' shared-factor flips, plus transformations, and multi-term
linear-dependence reductions. Canonical F2 sets cancel duplicate terms;
rank refers to the resulting set, not transient raw term count. This differs
from a multiset graph and does not quotient by symmetries in training.
All legal destinations are generated then de-duplicated. Ordinary cap8,
auxiliary cap9, fixed horizon32, terminal exact tensor equality and rank<=7.
Both policies generate the same transformation vocabulary then mask rank.
Reward 0 or 1 only at completion; no automatic selection of reducing moves.
Root standard scheme fixed. Ordinary feasibility and some actual cap8 success
must be verified offline before any training panel; use a bounded symmetry-
quotiented search or published certificate with native replay. The original
paper documents the rank8 component including a rank7 solution after eight
transformations (their graph representation need not exactly match ours).
If this implementation cannot certify access, stop, do not train an
unreachable ordinary baseline.

Use a simple learned energy over raw rank-one term IDs to score destinations.
This policy is a new small baseline, not the original C random-walk solver
or state-of-the-art multiplication algorithm. The policy learns a common
weight for each term via same-state grouped terminal reward, no target
optimization labels. Lazy local adjacency (bounded LRU cache) avoids global
state enumeration. Record candidate scores, active/padded action slots,
cache cost, reset cost (zero), runtime, successful trajectories. Cap8-only,
cap9-only and cap9-to-cap8 at 30%, paired seeds; all ordinary eval cap8.
The intervention changes legal ranks, not root or task. Candidate computation
varies by visited state; budgets match padded action slots, not wall-clock.
Do not run a full panel until a geometry/feasibility audit demonstrates a
meaningful sparse regime. Local smoke tests only for this assignment.

After offline feasibility certification, register an initial non-learning
diagnostic: enumerate cap8 across the GL(2,F2)^3 symmetry quotient
(retaining counts of all labeled destination neighbors) to calculate exact
uniform-policy first-hit probabilities within horizons 8, 16, 32 and 64.
Evaluate both caps with 32 random episodes at horizon32 (same seed 42,
uniform over distinct legal destinations). This is a reward-access sanity
check, not a measure of learning. Cap9 full enumeration is intentionally
omitted because the extra rank may expand the graph dramatically. The
full learning runner defaults to 120 updates of 2 same-start groups of 8,
but is not authorized to execute here beyond a two-update local smoke.

### Matrix geometry results (offline audit, not training)

The ordinary graph contains **1,356 reachable GL symmetry orbits**, including
one absorbing terminal orbit. An independent replay of the eight-move
rank7 witness checks all 256 pairs of binary input matrices. Under uniform
choice of distinct legal destinations, ordinary exact root hit probability
is 0.00001089 (8 moves), 0.0009891 (16), 0.0063297 (32), and 0.0199190 (64).
Cap9 increases the root degree from 24 to 96. In 32 random trials at H=32,
ordinary hit 1 and cap9 hit 0; they visited 836 and 957 labeled states,
respectively. The cap9 pilot evaluated 27,018 active choices compared to
12,851 at cap8. This is too small to infer a performance difference; it
suggests that extra graph exposure can also dilute reward probability.
The full cap9 graph is not enumerated.

`matrix_train.py` implements the three-arm learned search panel, tracking
actual scored candidate counts, active decisions and maximum allocated
slot allowances. These are **not identical compute costs**; a rank slack
arm can score more candidates. A credible positive finding would need an
additional candidate-compute-matched or wall-clock-matched follow-up.
This simple term energy is not a neural SOTA solver. It tests whether extra
native rank moves supply useful reward experience, not whether a published
solver has already failed. It retains the ordinary target and terminal
verifier and supplies no certificate to training. Local end-to-end smoke
with two updates, one group of two, two ordinary evaluation episodes per arm
passed replay checks; zero successes (expected at this tiny budget). No full
learning panel has been run.

Commands from this directory:

```sh
OPENBLAS_NUM_THREADS=1 python3 matrix_audit.py --out matrix_geometry.json
OPENBLAS_NUM_THREADS=1 python3 matrix_train.py --updates 2 --groups 1 --group-size 2 --eval-count 2 --seeds 42 --out /tmp/matrix-exposure-smoke.json
# Registered prospective panel (not launched):
OPENBLAS_NUM_THREADS=1 python3 matrix_train.py --workers 12 --out matrix-results.json
```
