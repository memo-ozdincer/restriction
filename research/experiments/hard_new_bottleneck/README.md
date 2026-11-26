# Sliding-puzzle sparse reward bottleneck

Registered hypothesis before sampling: ordinary terminal-only RL on the fixed
published-in-project depth-29 8-puzzle start fails to discover enough terminal
successes even over a long budget. Legal starts sampled near the goal or via
uniform/random walks can provide the learner with native terminal experiences
that bootstrap useful paths. An assisted learner may then solve the original
start even after assistance is removed. A completely different hypothesis is
that ordinary simply catches up once it discovers a solution.

Use the same fixed 29-action budget and exact solved board throughout. No
distance rewards, answer paths, expert action labels, or solver calls inside
training. Goal walk uses native uniform legal moves up to 29 steps, excluding
already solved initial boards. Uniform and root walk controls; each assisted
condition is compared continued vs removal after 60% of training. Four paired
seeds 42..45, 1000 batches of 256 episodes, 29 action slots each (7,424,000
slots per run). This is a fixed mechanistic long-budget pilot, not a scale
replication. Evaluate root with greedy learned policy and epsilon=0; train
with epsilon=.2. All episode budgets identical; record actual active moves
and reset generation overhead.

Learner is a tabular deterministic finite-horizon Bellman learner: a sampled
terminal success establishes value=1 at zero remaining actions. Every sampled
transition can inherit a positive value if the successor has a previously
learned path within the horizon. Encode each binary finite-horizon Q function
by the shortest known feasible number of steps; all longer horizons have
value 1. Backups apply in reverse sampled order, using minimum known distance
via sampled successor (not exact distance oracle). This represents the
finite-horizon sparse return, and introduces no intermediate reward signal.
All arms have identical bootstrapping. The full state space is indexed only
to vectorize legal transition evaluation; exact BFS distances are diagnostic
only and never observations, action selectors or backup targets. Track the
learned root feasible cost and exact bounded native replay. Distinct from
the previous policy-gradient experiments and not a claim about vanilla GRPO.

## Results

All 28 runs completed. The exact optimal root distance is 29 and the
native action horizon remains 29. Root policy evaluation is 512 fresh
greedy-with-random-ties episodes per seed, 2,048 per arm.

| Initial distribution | Final independent root wins | First nonzero root evaluation (steps) | Total training wins |
|---|---:|---|---:|
| Ordinary root | 0/2048 | none | 0 |
| Goal random walk, continued | 0/2048 | none | 1,005,604 |
| Goal random walk → root | 2048/2048 | 700,700,700,700 | 609,771 |
| Uniform reachable state, continued | 1541/2048 | 800,700,400,700 | 167,647 |
| Uniform reachable state → root | 2048/2048 | 700,700,400,700 | 49,207 |
| Root random walk, continued | 0/2048 | none | 0 |
| Root random walk → root | 0/2048 | none | 0 |

Goal-walk radius is sampled uniformly from 1..29; if the walk returns
to terminal, one further legal move is executed and counted. Root walk
radius is uniform 1..4. Uniform state draws are from all reachable states
excluding the goal, with no goal/solution selection. BFS enumerates legal
states but its numeric state index is only a table key, not a learned
numeric feature. No target trajectory or oracle labels enter learning.

All runs use 7,424,000 padded action slots (29,696,000 across four seeds).
Aggregate active moves, including free reset generation for walk arms:
ordinary 29,696,000; goal-only 7,411,687 + 15,409,772; goal-to-root
16,382,992 + 9,244,056; uniform-only 28,953,359; uniform-to-root
29,510,266; rootwalk-only 29,696,000 + 2,557,922; rootwalk-to-root
29,696,000 + 1,534,258. Uniform sampling uses a shared precomputed
reachable-state index, no native transition cost at reset; preprocessing
is not counted as policy action compute. This is an experimental simulator
privilege, not a claim about physical reset cost.

The initial uniform-random-legal policy's root success probability is
1.927432882224497e-12, approximately 518.8 billion attempts for one reward.
Ordinary training remains exactly that policy until its first success, since
all initially learned values outside terminal are zero and every sampled
nonterminal transition inherits only zero. At the 256k-episode budget, the
expected root hits under that frozen policy are 4.9342e-7. The probability
of any first hit within the entire ordinary training budget is at most
that expectation (union bound). Uniform reachable nonterminal resets give
6.250684174768939e-5 initial success probability, about 32.4 million times
the root probability. These are numerically evaluated exact finite-state
recurrences, no Monte Carlo approximation.

The tabular Bellman learner uses terminal positive values and sampled
transitions to stitch paths with known successors, choosing the shortest
currently known success path when feasible within the budget. This is
deterministic finite-horizon value compression, not policy-gradient GRPO.
The algorithm can exploit successes elsewhere even before an entire
root trajectory succeeds. It demonstrates a genuine state-distribution
reward-access bottleneck under a fixed learning algorithm, but does not
establish neural representation transfer or superiority to known search
algorithms. Goal-walk-only succeeds almost everywhere it resets yet misses
the hard root, while late root specialization connects the regions. Uniform
exposure can learn the whole relevant state graph, with specialization
finishing the remaining root coverage. Root-neighborhood variation alone
still never obtains reward.

## Independent replay

Run `python3 research/experiments/hard_new_bottleneck/audit.py`.
All 12 policies with positive final root evaluations were exactly reproduced
(checkpoint records, exact-first-hit timestamps, counts and final outputs).
Every independent root success (5,637 total) was replayed via the original
scalar 8-puzzle checker; each is an optimal 29-move solution. Across every
training run, all non-infinite learned path costs were audited against
independent BFS distances and none underestimated the true distance.
The source and original panel are in `../sliding_initial/`.
No cluster work, LLM calls, or Git changes outside this experiment.
