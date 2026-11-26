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

## Follow-up: remove Monte Carlo noise (registered before execution)

The twice-horizon control rescued tabular reachability, not linear
reachability. The root-feasible linear certificate also beats the achieved
uniform-start reward of the original learned linear policies. Thus we
cannot blame a necessary tradeoff alone. Replace sampled REINFORCE with
the exact finite-horizon expected terminal gradient, multiplied by
(BATCH-1)/BATCH to match the expectation of batch-mean-centered REINFORCE.
Keep original five-disk horizon, same initial policies, Adam and 3000
updates, uniform starts, seeds 42/43, linear and tabular. Track root and
reset success and compare to sampled uniform controls. Hypothesis: if
exact-gradient linear learning also destroys root support, sampled
gradient variance is not necessary for the failure. This is a privileged
offline mechanism probe with access to the complete transition graph,
not an admissible native-RL performance comparison or matched compute.

## Results

Job 2939159 completed on Trillium (def-zhijing/debug, tri0003, one
192-core node, 25 seconds elapsed). Source/config commit a0324ca.
All 48 rows retrieved with matched SHA-256 checksums; 24 original-horizon
rows reproduce the old saved weights bit-for-bit and exact training
win/action counts. All 48 independent final-policy evaluation checks
passed (relative tolerance 1e-4 for float32/float64). See
scheduler_evidence.txt and results.json.

Two-seed means, evaluation from original entrance at each training horizon:

| Disks | Architecture | Training horizon | Root-only | Uniform | Uniform then root |
|---|---|---:|---:|---:|---:|
| 5 | Linear | 31 | 2.37e-15 | 1.00e-36 | 1.18e-27 |
| 5 | Linear | 62 | 7.00e-8 | 1.19e-15 | 2.92e-14 |
| 5 | Tabular | 31 | 2.37e-15 | 60.03% | 99.28% |
| 5 | Tabular | 62 | 7.00e-8 | 99.91% | ~100% |
| 6 | Linear | 63 | 1.55e-30 | 1.23e-74 | 1.61e-59 |
| 6 | Linear | 126 | 8.01e-15 | 5.81e-18 | 2.13e-18 |
| 6 | Tabular | 63 | 1.55e-30 | 3.23e-7 | 3.04e-11 |
| 6 | Tabular | 126 | 8.01e-15 | 99.34% | 99.99% |

All root-only arms saw zero rewarded training episodes. Six-disk
126-move switched tabular learned near-certain reachability but retained
only 1.35e-5 mean success at 63 moves. The original objective was not
wrong, but conflated difficult optimality with reachability.
Doubling horizon does not rescue shared linear policies; they remain
worse than untrained control even at 16H. Original five-disk linear
uniform root log probability first improves (-33.68 to -29.69 at
step 100) then deteriorates (-45.98 at 500, -93.14 at 3000), whereas
tabular improves (-33.68, -27.70, -14.12, -0.51).
At the uniform-to-root switch the unsuccessful linear learners retain
Adam momentum and drift a little before stagnating.

Independent offline audit (audit.py, offline_audit.json):
all-state optimal-action margin LP infeasible at n=3..6, feasible n=2.
Root-only feasibility certificate nevertheless beats actual uniform
training reward: five disks 41.32% vs ~20.15%; six disks 33.79% vs
~8.59% (original eight-seed means). Root and good reset performance
are therefore not necessarily mutually exclusive; exact shortest
actions from all states are a stronger requirement than needed.
The previously learned six-disk uniform tabular policies reach 10.04%,
40.05%, 72.06% by 2H, 4H, 16H, respectively (eight seeds), despite
1.38e-7 at H. This is a frozen-policy evaluation, not a new training
comparison.

Exact-gradient probe (local, exact_probe.py and exact_probe.json):
uniform expected success rises from ~3% to 38.27% for both linear
seeds, but their root log-success collapses from -33.65/-33.70 to
-290.72/-180.44. Tabular uniform rises to 99.925% with root success
99.603%/99.604%. The gradient is exact DP, with float64 parameters
for numerical robustness (original sampled optimizer uses float32).
No sampling noise is needed for destructive transfer. The root
certificate still beats the exact-gradient linear endpoint on both
uniform reward and root success, so this is an inferior optimization
outcome, not proof of an unavoidable task tradeoff. It does not
establish which architectural or optimization change will solve it.
