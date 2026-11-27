# What is ordinary RLVR not learning?

## User idea-dump (verbatim)

> Cuz my original idea was to teach a model to become good at executing PARTS of elegant mathematics by giving it slices of accepted proofs.
>
> But slices of accepted proofs has been done to death. Maybe if you can find an easily-put-ontoppable-of-existing-datasets-and-math-by-hand, that could be cool. Like essentially teaching the model a much LARGER rules of the game than just starting points of formulas, could teach it very interesting new ways to solve the starting point.
>
> This was my thought for Restriction of dominant (find alternatives), and it was my thought for all the pseudo hill climbing stuff. But we still haven't really narrowed down on a mechanism that can do this.
>
> I think instead of continuing to brainstorm, we just NARROW our sights to that:
> - what insane skills can be taught, that RL can't teach.
>
> Wait, that's not good either... cuz if an insane skill COULD get you to the endgoal, RL will get you to it... obviously with the exception of like the mario kart shortcut... so I guess one research strand could be, how would we discover shortcuts, but I had already went down that rabbit hole an insane amount with pseudo hill climbing. don't wanna do that again.
>
> I just need a kind of "set of problems that are creative" and then kind of see "what is RL NOT doing". yeah, like what is RLVR NOT doing. it could be as simple as scaling (like this rl system isn't BIG enough to learn this the normal way, so we're making it more efficient) (so, expressivity of models, rollout size, rollout depth, etc.) OR it can be something it intrinsically can't find, shortcuts, etc. I can't really think of anything else from those two categories? zero gradients to learn goes into category 1 - not enough rollouts/depth.

## Three independent critiques, synthesized

Keep finite-resource discovery versus structural limitations as an axis,
not a complete taxonomy. A rare legal shortcut is generally a discovery
problem, not intrinsic impossibility. Structural barriers may arise from
the policy's expressivity, observation or action support, or from the
training objective not distinguishing equally rewarded strategies.
Even a reachable trajectory may be sampled but not learned, or learned
and later discarded. For conditional first-discovery probabilities
p_t, the probability of no discovery through T is the product of
(1-p_t), conditional on no previous discovery; a nonzero lower bound
supports eventual discovery, whereas collapsing probabilities need not.

| Stage | Diagnostic question | Existing evidence |
|---|---|---|
| Headroom | Is materially better behavior available? | Small XOR/tensor near optimum; do not mistake saturation for failure. |
| Feasibility | Can policy/interface express the desired behavior? | Not established as a barrier in present experiments. |
| Opportunity | Does the training distribution reward the skill relative to substitutes? | Racetrack straight-line behavior suffices on training layouts. |
| Discovery | Is valuable behavior actually sampled? | Hard Sokoban and long CNOT finite-budget zero-success cases. |
| Acquisition | Do sampled successful behaviors become more likely? | Near-miss and mode research motivate, but do not establish, failures of credit. |
| Retention | Is an acquired behavior later lost? | One ordinary racetrack seed temporarily discovered then lost lateral steering. |
| Transfer | Does the learned behavior work on unseen tasks? | Racetrack positive; single-board Sokoban insufficient for cross-board transfer. |

The negative circuit-compression result rules against needing
special exposure for neutral transformations: ordinary RL discovers them.
TSP low coverage alone does not imply valuable unexplored strategies.
An invariant supplied to Lean may reveal a useful executable capability,
but does not show whether ordinary RL can discover, acquire or retain it.

## Next research questions, not proposed interventions

1. On creative, exactly verifiable tasks, where is there demonstrable
   headroom between ordinary competence and better solutions?
2. What does ordinary RL fail to sample at the tested budget? How does
   first-discovery frequency depend on ordinary width, depth and capacity?
3. Among trajectories it does sample, which valuable behaviors are not
   reinforced or retained? Track fixed independent probes across checkpoints.
4. What does train reward leave underdetermined? Do comparably competent
   policies differ in held-out capability across structural task families?
5. Is a capability expressible and identifiable from the existing interface?
   Treat an actual impossibility separately from finite-budget failures.

Start with baseline trajectory/checkpoint audits, preferably on existing
datasets and runs. Do not select an intervention before locating a
bottleneck. Creativity is an environment-selection heuristic, not a
reward. No new experiments run in this discussion.

Previous candidate mechanisms retained as options only: dominant strategy
exclusion, solvability-conditioned resets, failed-trajectory branching,
temporary action/resource expansion, constraint removal, independent
lineages and coverage-based scheduling. A change in start distribution
preserves the terminal predicate but generally changes the expected
training objective. Future comparisons must distinguish these.
