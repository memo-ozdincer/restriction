# Reset geometry and other environmental freedoms

User idea-dump, verbatim:

> step 1 - look at what other degrees of freedom can be supplied other than starting points step 2 - look at how scooped the varied start is. I think varied start is specifically extremely good for stuff that actually has sequential solving. HOWEVER, the issue is, for math and stuff, its not exactly like pinball. It seems we need to go near the solution, which is fine, but in pinball starting from only near the solution was generally much worse than true pertrubations that are somewhat similar distances from the solution as the goal start (also, this requires you to have a "goal start" like a starting point that you're ACTUALLY optimizing towards, such as a 0,0). Now, obviously this i s just one formulation, if we use a different one, we should be aware that it is different, probably because true random also increases the chance of you getting to the solution. Also, I'm sure some kind of distance ladder emerges, where you have a distribution of earlier balls converging and that radius slowly increasing, becaus its random though its more indifferent therefore more magical.
>
> Lets consider this and alternative formulations that could work well for ours and for the other environments

## Separate variables

Let s0 be the official initial state, g the fixed goal, H the action budget,
and K unchanged legal dynamics. For reversible finite tasks d(s,g) is
shortest legal action distance. Distinguish proximity to the official
start, proximity to the goal, reward accessibility under the current
policy, and overlap with states occupied by useful root trajectories.
None implies the others. For pinball, physical Euclidean distance is not
minimum control cost: velocity and obstacle geometry matter.

| Reset distribution | Defining choice | Scientific question |
|---|---|---|
| Start-centered | Random legal walk from s0, fixed random length | Does nearby experience teach skills relevant to the launch? |
| Goal-centered | Random legal walk from g, fixed random length | Does easy terminal reward bootstrap reusable suffix skills? |
| Uniform | Any legal state, independent of trajectory | Does coverage alone suffice? |
| Iso-distance | Random states with d(s,g)=d(s0,g) | Does variation help without shortening the minimum task? |
| Broad radius mixture | Sample lengths across both centers, with fixed weights | Can easy experiences seed discovery at harder radii without a success-based teacher? |
| Adaptive reverse | Expand from starts of intermediate observed success | Strong prior art, explicit selection using outcomes |
| Replay | Previously visited states | Useful exploration but trajectory-dependent |

Iso-distance is a diagnostic oracle control, not a necessary implementation
of a scalable sampler. Exact distance is unavailable on many harder tasks.
Even exact distance does not equal difficulty: number of good paths, action
geometry, representation and policy priors all matter. A fixed broad mixture
can allow an emerging capability frontier without explicitly choosing it,
but the existence or outward motion of that frontier is empirical.
Measure conditional root and shell success over time with distance used
only for diagnostics. Equal training episodes and policy calls, account
for actual actions, and evaluate only the official start. A phase switch
must be compared with continued exposure and ordinary-only training.

## Exact diagnostic on our existing reversible task

The 40,320-state three-wire graph permits exact dynamic programming for
uniform-random-action hitting probabilities. Same eight-action horizon,
same fixed target at exact distance 8. Exclude already-terminal resets.
Random walks have length uniformly sampled from 1..4. See
[results and executable calculation](experiments/reset_geometry/README.md).

| Distribution | Mean shortest distance | Exact random-policy finish probability |
|---|---:|---:|
| Ordinary root | 8.000 | 0.0000014466 |
| Root-centered walk | 6.775 | 0.00001222 |
| Uniform legal states | 5.866 | 0.00018249 |
| Goal-centered walk | 2.153 | 0.03651645 |
| Equal-distance shell (577 states) | 8.000 | 0.00000088 |
| Balanced shells 1..8 | 4.500 | 0.01445371 |

Goal-centered walks supply ~25,000x the untrained root reward
probability; root-centered walks supply ~8.4x. Equal-distance random
states actually have smaller initial success probability despite 577
different states. These are exact probabilities for a uniform-action
policy, not learned performance. The result explains why even nonterminal
near-goal resets can be useful in combinatorial spaces, and why global
random resets are a much weaker source of positive rewards than the
physical analogy might suggest. It does not establish what the acquired
skills are or whether same-distance practice transfers better given
matched access to reward.

## Other degrees of freedom, ranked for our philosophy

1. **Action budget / temporal slack.** Keep root, target, observation and
   primitive dynamics fixed. Temporarily allow more steps, then restore
   the original budget. Success remains exact target equality, but the
   resource constraint is relaxed. In reversible root, untrained success
   rises from 0.000145% at 8 actions to 0.0206% at 24 and 0.1084% at 64.
   A useful whole-task control; count primitive actions and compute,
   compare against reset exposure. Longer horizon can create slow
   solutions that fail to compress; this is an empirical test.
2. **Action granularity / macros.** Offer generic compositions of legal
   primitives (e.g., all pairs), or permit variable-length action chunks.
   Charge their full primitive cost so the task remains equivalent.
   Removing the macro vocabulary can test whether practice teaches
   compositional skill. If macros cost one instead, the horizon/resource
   objective changes. No curated useful macro bank; sample uniformly
   or use all small compositions. Extra output heads and representation
   changes must be accounted for.
3. **Workspace / resource slack.** Temporarily add scratch registers,
   circuit wires or memory to a benign computational environment.
   Require full output correctness and restore the original workspace
   at evaluation. A real change of computational capacity: avoid
   pretending exact same feasible solution set. Useful in register
   synthesis and circuit construction, less clean in three-bit
   reversible benchmark without extra wires.
4. **Goal tolerance.** Accept broader terminal goal class during training
   (e.g., fewer incorrectly placed puzzle tiles, range of landing
   speeds), restore exact original terminal checker. Binary outcome
   remains but reward definition changes. Strong prior art and a
   potential source of shortcuts. Better as a control than core method.
5. **Dynamics relaxation.** Temporary generic move freedom such as
   allowing any two tiles to swap before restoring adjacent moves.
   This resembles open timed doors in physical experiments. It
   changes native transitions; agent can learn skills that do not
   transfer. Test with the original rules at evaluation.
6. **Observation/context freedom.** Provide exact environment facts
   already derivable (full board state, wire values for all inputs,
   formal local context), then remove redundant visibility. This
   changes information but not objective or transitions. A human
   selected lemma or reference path is materially different from
   native state rendering. Could be tested with truth-table display
   before interpreting model failures as mathematical limitations.
7. **Symmetry / representation randomization.** Random relabeling of
   equivalent wires, rows or variables, applying the same symmetry
   to state, goal and actions. Preserves distance and exact cost if
   it is a true automorphism. It varies task representation rather
   than fixed-target state; useful for separating memorization and
   general skills. Do not claim this is identical to fixed-root RL.

## Transfer to other environments

- Sliding puzzle: start walks, exact goal-distance shells and slack
  29->larger move budgets are clean. Macro moves can be arbitrary
  legal sequential moves; unrestricted swaps change dynamics.
- Reversible circuit and elementary matrix operations: both centers
  and exact shells are computable in small cases. Extra primitive
  action budget is especially clean. Generic algebraic operations
  composed of allowed steps can be exposed without naming a solution.
- Sorting network: random comparators compress the set of possible
  binary rows. Starts near fully sorted state cannot generally be
  generated by reverse moves because comparators discard information.
  Random prefix length is a native clock/radius parameter. Match
  remaining unsorted-row count or exact shortest suffix in small
  controls; neither is a universal distance metric. Total root cost
  and continuation cost must be distinguished.
- Lean: proof states are obligations in a justified local context,
  usually not invertible native configurations. There is no generic
  solved state from which random legal proof actions generate arbitrary
  unsolved target obligations. Root-centered exploration from failed
  attempts and problem specialization are distinct. Horizon, wider
  scratch reasoning, or generic additional deferral/HELP permissions
  are closer analogues of other freedoms, but require final unassisted
  Lean verification. No general random-start mapping established.

## Prior-art assessment (primary sources)

The broad reset method is established. [Reverse Curriculum Generation,
2017](https://proceedings.mlr.press/v78/florensa17a.html) uses goal-centered
random walks, moves starting distributions outward according to performance,
and sparse goal reward. Our distance-ladder intuition is directly related.
[Exploring Restart Distributions, 2020](https://arxiv.org/html/1811.11298v3)
mixes the original start distribution and past visited-state replay.
[Schenke and Wallscheid 2021](https://arxiv.org/abs/2105.08990) explicitly
study random exploring starts and density-based state coverage.
[Learning to Locomote, 2020](https://www.cs.ubc.ca/~van/papers/2020-MIG-envdesign/2020-MIG-envdesign.pdf)
widens initial joint angle distributions, finding a trade-off between
training efficiency and robustness. Thus starting near an intended launch
rather than near the goal is not a new broad idea either.
[Putting the Spotlight on the Initial State Distribution, 2025](https://openreview.net/pdf?id=RuJCcUWedX)
formalizes effects on the same policy's objective and bottleneck geometry.
[SCOUT 2026](https://arxiv.org/html/2607.26417v1) compares per-context
reset curricula and global schedules including scaffold removal.
[Satori](https://openreview.net/attachment?id=j4FXxMiDjL&name=pdf) applies
restarts to correct and failed reasoning prefixes; additional format
supervision, reflection bonuses and reward model distinguish that design
from our terminal-only native-state sampling.
[Privileged Action 2025](https://arxiv.org/html/2502.15442v1) relaxes
robotic constraints and adds virtual forces, followed by a curriculum
that reduces the privileges. Broad temporary action freedom is prior art.
[Horizon Length 2026](https://arxiv.org/abs/2605.02572) studies short-horizon
training for LLM tasks; different from simply allowing a longer action budget.
See also the existing state-exposure and coding prior-art audits for PrefixRL,
Go-Exploit, AlphaProof, GASP and other close neighbors.

No algorithmic novelty claim for random starts, reverse ladders, or crutch
removal alone. More specific research question remains: within a fixed
task and terminal verifier, compare start-centered, goal-centered and
distance-matched exposure followed by ordinary-only specialization.
A delayed gain despite training at similar minimum distance and without
outcome-based state selection would be particularly informative. A
reward-accessibility-matched comparison could further distinguish state
coverage from merely obtaining more terminal successes, but matching
uses diagnostic estimates and is not the core neutral sampler. No
comprehensive literature search can prove novelty.

## Proposed next experiment

Use the current exact three-bit task as a testbed. Freeze six reset
distributions above (exclude solved starts), use same learner and
terminal reward, compare continued and switched training. Include
ordinary-with-temporal-slack then restore budget as a separate
mechanism comparison with matched primitive action budget. Measure
initial random reward rate, distance-shell learning curves, action cost
and root completion throughout. The exact diagnostic already shows
that these arms differ dramatically in initial reward availability.
Do not conflate an emerging distance ladder with explicitly scheduling
one. No new RL training was launched as part of this design audit.
