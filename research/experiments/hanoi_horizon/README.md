# Hanoi: horizon and objective conflict

Registered before training. Independent audits found that the original exact
31/63-move horizon makes nonoptimal moves fatal at the entrance but not
at random starts. Saved-policy extended-horizon evaluations reveal that
six-disk tabular uniform practice has substantial delayed success, while
linear policies remain near zero even with much longer time. A strict-margin
LP for the unique distance-decreasing move at every nonterminal state is
infeasible for the linear architecture, although the root-only LP is feasible.
The global shortest-policy LP does not prove inability to solve with slack.

Hypothesis: random-start practice learns robust reachability but not exact
optimality in the tabular case; in the linear case it may learn conflicting
local behaviors. Compare exact original horizon and twice that horizon with
same terminal reward, legal actions, feature representation, Adam, episode
count and paired seeds 42 and 43. Modes root, uniform, uniform-switch;
five and six disks, linear and tabular. Each horizon has its own matched
ordinary control. Cross-horizon comparisons do not match padded move slots
(report both); they diagnose the action cap, not compute efficiency. Record
root success at H, 2H, 4H, 16H, uniform success and actual root log-probability
change through training; exact expected gradient and Adam step alignment at
checkpoints are diagnostic only. No solution labels, distances or oracle
policy enter any training update. The original H arms are instrumentation
controls, not additional seeds for statistical significance.
