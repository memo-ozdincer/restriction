# TSP reference-quality and group-signal diagnostic

Hypothesis registered before any numerical run: steepest-descent 2-opt warmup
trajectories enter states where a fixed stochastic 2-opt policy rarely discovers
additional improvements. Earlier checkpoints from the same trajectory should
produce more nonzero centered reward groups under NICO-TSP's nonnegative
reference-improvement rule. However, that gain may vanish under a fixed global
optimality objective. If so, easier warmup references create relative reward
variation without demonstrating additional access to the original terminal goal.

Motivation: NICO-TSP (https://arxiv.org/html/2604.06940v1), section 3.3 and
Appendix E, report zero-signal groups especially after strong warmups. Their
method already varies warmup length. They propose reference-difficulty
control. This experiment is an audit inspired by that mechanism, not a
reproduction of their pretrained neural policy or a novel warmup curriculum.

Design fixed in advance:
- One 10-city Euclidean TSP (Python random.Random(20261127), integer points
  in [0,100]^2, no instance selection). Distances round Euclidean distance
  times 100, nearest integer. Held-Karp dynamic programming finds exact
  minimum closed-tour cost. No witness tour is supplied to models.
- Sixteen seeded uniform random initial tours, each followed by deterministic
  steepest-descent 2-opt to a local minimum. Every warmup trajectory retained.
  Compare terminal checkpoint versus halfway checkpoint, for each warmup.
  Cost/steps of creating starts are recorded; both use the same warmup trace.
- Continuation action is ordinary 2-opt, reversing positions i+1..j with
  nonadjacent cut edges; no action-mask relaxation and same budget in both
  arms. Horizon 3, groups of 8. 128 groups per start for a fixed stochastic
  move policy with softmax over cost differences (temperature 3% current
  tour cost, no learning). Same RNG seeds across paired starts.
- Exhaustively enumerate all legal continuations of length <=3 as an offline
  diagnostic, never as a policy input. Measure exact best reachable cost and
  whether the global minimum is reachable. Report NICO-like centered signal
  (winner-time cutoff and nonnegative relative reference improvement),
  fixed binary terminal success, and absolute best cost.
- Frozen Luna/Terra screen will use the first *suboptimal* warmup trajectory
  (or first trajectory if all optimal), same two starts, four independent
  no-tool proposals per group, 3 moves maximum. The optimum value and witness
  are hidden. Exact verifier checks all proposed actions and costs. Main
  frozen group results are exploratory and there is no training. Record
  raw prompts, answers, and independent verifier replay summaries.

No claim about retained transfer can follow from this screen. A proper learning
comparison would require matched training compute and root-only evaluation after
withdrawing changed exposure. The fixed policy diagnostic isolates arithmetic
of the reward-access mechanism; it is not evidence about the NICO model itself.

## Local result

Exact optimum 27099; independently verified by enumerating all 9! tours
in addition to Held-Karp. Sixteen warmup runs give 11 globally optimal
terminations and five genuinely suboptimal plateaus costing 27139. Cost
difference is small (0.148%); strict optimum is nevertheless a hard
terminal event for the limited-horizon fixed policy.

Primary comparison conditional on the five suboptimal plateaus:

| Metric | Midpoint starts | Plateau starts |
|---|---:|---:|
| Groups, 8 rollouts each | 640 | 640 |
| Groups with nonzero centered NICO-like reward | 640 | 380 |
| All-zero NICO-like groups | 0 | 260 |
| Terminal optimum hits (5,120 rollouts) | 157 | 53 |
| Mixed binary-optimum-reward groups | 118 | 51 |
| Starts with optimum reachable within 3 moves | 3/5 | 5/5 |

An exact probability calculation over all three-step policy paths yields
mean terminal-optimum probability 2.755% from midpoints vs 1.199% from
plateaus, expected mixed binary groups 17.11% vs 9.20%. This confirms
the direction without relying on Monte Carlo luck. It is an average
over five selected suboptimal trajectories of ONE instance, not an
independent-instance sample. Three midpoint starts can reach the optimum,
and for two of those the probability exceeds the paired plateau. Two
midpoints cannot reach the optimum in the allotted horizon. Do not
assume all earlier starts are useful.

All-16 diagnostic includes 11 already-solved plateau starting tours.
With NICO-like improvement reward these necessarily have zero groups,
so the aggregate comparison would exaggerate the practical mechanism.
Our primary analysis conditions on the suboptimal cases. The local fixed
policy takes exactly three moves even from solved starts; it cannot stop,
and its all-16 binary success metric should not be interpreted as solver
success with early stopping. The frozen screen permits up to three moves.

This is a demonstration of a reward-access bottleneck in a fixed
handwritten stochastic policy; it has not demonstrated learning or
specialization. Reference-clipped improvement reward genuinely changes its
reference across starts; the absolute optimum reward does not. No expensive
training or repeated seeds for significance have been performed.

Reproduction:
- python3 research/experiments/tsp_signal/experiment.py
- python3 research/experiments/tsp_signal/audit.py
- python3 research/experiments/tsp_signal/screen.py --out /tmp/new-tsp-signal

## Frozen result

One group of four independent proposals per model and reference start,
first suboptimal warmup trace (trial 1). All 16 outputs valid and all
replayed independently. Both reference states have a global optimum
reachable within three legal moves. The expensive model comparison
reverses the result of the weak stochastic policy:

| Model/start | Positive NICO-like rewards | Mixed NICO-like group | Exact optimum hits | Mixed binary group |
|---|---:|---:|---:|---:|
| Luna midpoint | 1/4 | 1 | 0/4 | 0 |
| Luna plateau | 0/4 | 0 | 0/4 | 0 |
| Terra midpoint | 4/4 | 0 | 0/4 | 0 |
| Terra plateau | 2/4 | 1 | 2/4 | 1 |

Terra midpoint outputs converge on the same local minimum (27139),
so positive improvement does not yield centered reward variation.
Terra plateau can instead solve the 40-point residual difference
with a 2/4 success rate. Thus midpoints are not universally better.
Useful exposure depends on current policy competency, and a scalar
reference-quality metric is insufficient to identify the best
training starts. This is the strongest result of the screen. It
motivates a state-difficulty diagnostic conditioned on model,
but does not establish that changing the training distribution
would improve later performance.

Raw public synthetic inputs/prompts and model JSON outputs are under
frozen/; compact verified metrics and hashes are frozen_results.json.
Full generation events/stderr are retained locally in
/tmp/tsp-signal-20261127 and should not be committed. No model was trained.
