# Exposure beyond bootstrapping: discovery of reusable computational strategies

## User idea-dump, verbatim

> the thing is, the ones that are kind of like explore then RL (like, make it possible for a good solution to sxist, then do regular RL), are too well established, i mean theere's the whole paradigm of sft then RL... you know?
>
> I'm just wondering if there's anything beyond that here. Perhaps something like exploratory RL allowing for learning of things the model would never have learned... its unlikely that that kind of behaviour can even be observerd in these environments though right?
>
> I mean, maybe if the path to the correct solution was SO difficult, that somehow teaching the model some wizardry and alchemy in the form of advanced subproblems (such as placing it down the line in a successful proof, or getting it to internalize some really difficult proof patterns in similar environments) gave it the tools to, that nothing else would. But just exploration for bootstrapping is just... exploration for bootstrapping i think

## Hypothesis and limits

Environmental exposure determines not only whether terminal-reward RL
succeeds, but which reusable computational strategies it discovers.
Operationally, a competent ordinary learner fails to develop a specific
transferable strategy within a matched budget despite already receiving
useful reward. Exposure causes a learner forked from that same checkpoint
to develop and reuse that strategy on fresh ordinary tasks.

No finite-budget experiment establishes that ordinary learning could
*never* discover a strategy. Nor does a better terminal score alone
distinguish reusable skill from bootstrapping a rarer high-quality
reward. This proposal requires stronger, independently tested evidence.

## Independent agent critiques (three reviews)

All three support the operational hypothesis, with the following
requirements, ordered by importance:

1. Native terminal objective and verifier unchanged throughout. No
   curated useful objects, expert operation rankings, process labels,
   reference solutions, oracle state selection, or motif reward. The
   learner chooses its operations. The reward may be a terminal
   efficiency score (e.g., actual gate count) if defined from the
   beginning for every arm, not a new auxiliary curriculum reward.
2. Fork a common ordinarily trained, demonstrably competent policy
   plus optimizer. Ordinary must already solve and improve on the
   task. If common competence is not attainable, the task tests
   bootstrapping instead; do not advertise it as alchemy.
3. Identical action language, state representation and legal
   transitions; intervention changes experience distribution only.
   Generate resets using target-independent native mechanisms, not
   an authored or discovered winning solution supplied as input.
   Account for reset ancestry, elapsed time, and all environment and
   policy costs. No free computational work. Include same- or
   greater-cost resets where feasible so exposure is not merely
   practice on easier examples.
4. Match compute, initialization, training objective, and final
   root-only phase (if any); compare continued ordinary, exposure,
   on-policy or entropy/diversity-matched exploration, and random
   search without learned exposure. Log success and reward histograms;
   equal compute is primary, matched-quality checkpoint comparisons
   are additional descriptive controls, not a replacement for it.
5. Freeze and test original starts on disjoint instances and
   relabelings, with no additional reward or tuning. Demonstrate
   independently measurable strategy behavior and its utility,
   conditioned on comparable circuit quality where appropriate.
   Analyse motif discovery on development traces, freeze tests before
   held-out evaluation. Offline ablation/recombination with matched
   random controls may assess causal usefulness; a motif ban changes
   action availability, so use identical bans for both arms and do
   not claim an intervention-induced ban is native training.
6. Report nulls: no root improvement; advantage explained by free
   reset work, reward density, quality threshold crossings, or a
   non-learning search; same strategy at equal quality; no held-out
   transfer; ordinary achieves same result within budget. Faster
   discovery alone supports a narrower result.

### Agent 1: multi-output XOR synthesis

Uniformly draw distinct full-rank 5x5 GF(2) target matrices, seed
committed before sampling. Use 256 training and 256 disjoint held-out
maps plus a separate validation split for deciding baseline competence.
No map selected for containing an alleged clever motif. Five input
wires are symbolic one-hot bitmasks. Append XOR of two existing wires,
excluding zero/duplicates (a declared fixed action-space quotient).
Target reached when every row mask exists; exact bitmask equality.
Horizon H=20, sufficient for constructing each output separately.
Terminal reward 0 if incorrect, otherwise 1+(20-L)/20, where L charges
every appended gate including unused reset gates. Immediate terminal
on correctness. Ordinary root is input wires only. Exposure: uniform
native legal XOR walks of depth 0..8 independent of target, reject
terminal resets; account rejected draws and all reset costs.
Compare ordinary, random-prefix exposure and same-depth on-policy
prefix exposure, fork only after ~80% ordinary validation correctness
and observed optimization progress. Hold out fresh maps and
permutations; evaluate from empty input start.

Possible strategy: shared intermediate combinations, including
cancellation-aware reuse (an intermediate may contain terms absent from
an output and later cancelled). This is a diagnostic candidate, not
a rewarded or enforced pattern. Evaluate reuse, terminal cost, and
motif causality on fresh maps; same-quality controls distinguish
structural effects from short-circuit reward discovery. Exact small-map
optimization may audit cost but cannot direct resets or training.

### Agent 2: physical maneuvers and puzzles

Top recommendation integer racetrack/pinball: native position,
velocity and remaining clock; terminal 0 on failure, otherwise
1+(H-t)/H. Establish >=90% ordinary finishing checkpoint. Randomize
reachable snapshots with original elapsed time and charge generating
moves. Procedures for boards fixed before outcomes. Compare final
ordinary and novel held-out boards and starts; inspect high-speed
maneuvers, braking, alternative routes versus mere speed improvement
on the same route. A reusable maneuver across new geometries is stronger
than a better single trajectory.

Sokoban: start with ordinary competency, native random exploration or
reverse-reachable resets (the latter encodes solvability and must be
audited). Terminal solved plus move/push efficiency fixed from outset.
Diagnostic possibilities: temporarily moving crates away from goals,
coordination and parking. Small permutation puzzles: reusable group
words, conjugations or commutators that affect one portion of the
configuration while leaving another unchanged. Assess motifs post hoc,
not as training curriculum.

### Agent 3: semantics-preserving reversible circuit compression

Strongest skeptic recommendation: start with correct but inefficient
four- to five-wire reversible circuits (20–50 gates). Every episode
already has correct semantics and nonzero reward; optimize final gate
count, rather than discover correctness. Primitive actions replace a
short contiguous word by an exactly equivalent short word, including
neutral or longer replacements. Enumerate equivalences mechanically
over all short words (e.g. length <=3) with exact truth-table equality;
no curated hand-selected rewrite bank, no direct optimum supplied.
Every state preserves root target semantics. Fixed native action budget
and terminal gate-count score; all cells/caps equal. Random reset
moves preserve or enlarge initial circuit length, independent of
whether it improves afterwards, with all generation accounted for.
Common checkpoint already learns obvious compressions; continue root
vs exposure vs exploration/search controls.

Possible emergent behavior: voluntary temporary expansion or neutral
restructuring which permits a larger nonlocal reduction. Test whether
frozen learner executes such transformations from original starts and
disjoint circuits (not just supplied reset states). Canonicalize wire
labels, record exact transformations, verify end-to-end functional
equivalence; use matched ablation and replay/recombination to measure
actual contribution. First pilot selection may depend on independently
observed ordinary plateau and feasibility, never intervention wins.

## Synthesis and recommendation

First choice: circuit compression over synthesis, because correctness
is guaranteed at the start, every episode yields a terminal quality
signal, and equal- or worse-cost resets remove the simple 'easier
starting position' explanation. This still can bootstrap access to
better quality, hence frozen transfer and mechanistic analysis are
essential. The environment includes encoded equivalence operations,
but mechanical enumeration and use of identical actions in all arms
minimize human strategy labels; also test primitive-only representations
if equivalence works as a too-powerful shortcut. A rewrite table is
not intrinsically free: generation/access and identical prior knowledge
must be accounted for. Proposed, not yet implemented.

Second: multi-output XOR synthesis — structural generalization is
particularly interpretable but correct construction must become routine
first. Third: physical route optimization — strong native-state
analogy and interpretable maneuvers; less directly computational.
Tensor flip/plus decomposition already has a nearby implementation:
[existing pilot](experiments/exposure_tensor_sokoban/README.md). It
preserves semantics at every step but the current pilot seeks a minimum
rank with binary reward, so it does not yet meet the beyond-bootstrapping
criterion. A future terminal rank-efficiency task with common
competence and disjoint tensor transfer could be stronger than the
tiny 2x2x2 pilot. No claim of novelty over existing optimization
or exploration literature has been established.

A genuinely decisive result is not merely a new superior circuit.
It is an acquired, reusable way to produce superior circuits on
instances that have never provided a successful high-quality training
trajectory. No experiments were launched by this critique round.
