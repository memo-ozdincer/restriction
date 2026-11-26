# Registered exploratory panel: reversible computation freedom

Target: the lexicographically first diameter-eight three-wire permutation
from the existing reversible learning environment, with twelve positive-control
Toffoli/NOT/CNOT gates as unit actions. Root is identity. Official goal and
eight-action cap are fixed. No reference gate sequence, distance reward,
or process labels. The only reward is binary exact permutation equality
within the episode's budget. Exclude already-successful starts throughout.
Distances are used only in reset controls explicitly labeled as oracle
controls and in diagnostics, never as observations or rewards.

Questions registered before running:
1. Can starting-state variation itself enable root learning, even if the
   random policy has no increased access to reward? Compare root, root-walk
   1..4, goal-walk 1..4, uniform legal nonterminal state, equal-goal-distance
   shell, balanced 1..8 shells, longer goal/root walks, and fixed mixtures.
   Equal-distance shell uses BFS to preserve remaining optimum eight,
   deliberately a diagnostic oracle rather than a proposed scalable sampler.
2. Are broad modes' benefits conditional on removing the freedom? Compare
   continuing reset versus switching to root at 30% of the 300 updates.
   For the preselected goal-walk and balanced-shell modes also test switch
   at 10%, 60%, and 90%, to separate early exposure from extended exposure.
   These variants test schedule sensitivity rather than simply replicating
   a previously observed benefit.
3. Does temporarily allowing longer legal action sequences unlock learning
   at the unchanged root without resetting toward the goal? Compare 8, 16,
   32, 64 training horizons, continued or 30%-switch to original horizon.
   At horizon 32 also pair root-walk and uniform sampling with the same
   horizon rule. Training success still requires the exact goal but relaxed
   horizon is a changed resource constraint; compare freely trained policies
   only at original root/horizon at evaluation. The action slot budget is
   1,024 per update in all arms; batch is 1,024/horizon, so episode count,
   likelihood-ratio variance, and first-hit truncation differ. Record all.
4. Trace each distribution's initial random-policy reward access and
   evaluation success on exact distance shells. A distance ladder emerges
   only if capability on more distant shells actually increases after
   training, not simply because starts were forced near the goal.

Procedure: eight paired seeds 42..49, 300 optimizer updates, Adam .01,
linear 64x12 stochastic policy, same initialization per seed. Separate
random streams for reset, sampled training actions and evaluation; unlike
historical pilot, this avoids proposal-method-dependent random draws.
The existing gradient estimator (within-batch mean terminal reward
baseline) is unchanged. At each training step all policies process exactly
1,024 action slots, including masked slots after first success. Count true
actions, episode starts, verified success, actual reset distribution,
and CPU times. Use a separately seeded root evaluation of 512 episodes
every 25 updates plus an exact finite-horizon policy hitting probability
at the final checkpoint. Exact evaluation also audits each shell and root,
not fed back into training. Compare whether final root rate exceeds 10%,
alongside average and per-seed results. No post-hoc hyperparameter tuning.
All arms are prespecified and use matching seed panels for discriminating
alternate mechanisms rather than publication significance.

Pure legal reset distributions change the training initial-state objective
but retain primitive moves, fixed goal, and horizon. They are intrinsic
in the sense of no supplied task-specific path. Goal-biased reset selects
states near the solution and thus favors easier episodes. Shell controls
use an exact shortest-path oracle and are unsuitable as a general sampler.
Uniform and walk sampling is implemented from exact precomputed distributions
for the finite experiment only; preprocessing is shared and reported.

Post-panel follow-up registered before replay: strong 60%-switch outcomes
raise the question whether near-goal ability actually propagates outward
or only memorizes the root during the subsequent ordinary phase. Reproduce
the exact fixed seed trajectories for root-only, near-walk continued and
60% switch, balanced-shell continued and 60% switch, both-walks 30%
switch. Add exact shell success measurements at each preexisting checkpoint
without changing training, verify weights and all original records exactly.
For each arm with a successful seed, independently verify 512 sampled
final root action sequences on the native evaluator. This is replay and
audit, not additional selection or a new seed test.
