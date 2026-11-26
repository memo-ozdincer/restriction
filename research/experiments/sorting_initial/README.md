# Sorting-network task family: state exposure

## Registered diagnostic (before model calls, November 27)

Hypothesis: a target-independent native comparator prefix can compress the
set of unsorted rows enough to unlock valid continuations under the same
terminal comparator-count budget, and a short known-prefix suffix acts
as a positive control. This is an inference diagnostic, not RL evidence.

One ordinary target for each of n=6 and n=9 wires. Their proven optimal
comparator budgets are 12 and 25 (see below). Compare empty universal
start (all binary rows), random native start after 2*budget uniformly
sampled legal comparators, and a proven solution state with three
comparators left. Random sampler depends only on n and seed, rejects
only terminal states. Exact same action alphabet (compare i<j, min on
wire i and max on j), fixed terminal goal and continuation budget for
each n; zero-one principle gives correctness on all ordered inputs.
All reset starts are reachable and can be solved by an ordinary full
sorting network. No prefix is supplied to models, only the native
possible-output set with already sorted rows omitted; sorted rows are
fixed under all legal comparators. One fresh no-tool low-effort rollout
per n/condition/model (Luna and Terra), 12 total. Report exact terminal
reward and number of unresolved rows for diagnosis, not shaping.

A compact bitset represents the set of all reachable row values, with
wire 0 as the most significant row bit. The state is sufficient for
terminal universal sorting; duplicates and row provenance do not matter.
Prefix costs are excluded from the continuation budget deliberately (as
in pinball reset); independent root evaluation with complete cost is
required for future learning claims. Because a full ordinary sorter can
always be applied from every start, frozen successes could be generic
sorting rather than state-specific. This pilot does not test transfer.

Sources: Codish et al., [25 comparisons for 9 inputs](https://arxiv.org/abs/1405.5754)
and [formal size optimality / zero-one principle](https://imada.sdu.dk/u/lcf/pubs/paper44.pdf).
Witnesses reproduced as functional comparator lists from the [SorterHunter
catalogue](https://bertdobbelaere.github.io/sorting_networks.html), independently
verified locally. [AlphaDev](https://www.nature.com/articles/s41586-023-06004-9)
is prior art for assembly sorting optimization, a distinct environment.

A follow-up random-policy calibration tests a specific alternative explanation
for any frozen continuation wins: the chosen reset may be trivially solvable
by random comparator actions. An informal n=6 pilot yielded zero root wins
and many wins after long random legal prefixes. Therefore, before interpreting
model responses, compare random policy completion on the same fixed root,
random and known starts, and a fresh population of independent random prefixes,
for both n values. Seed 42, 2,000 episodes per state source, same continuation
budget; no model calls. The purpose is to quantify intrinsic task difficulty
and distinguish a usable reset distribution from a sampler that yields only
near-trivial cases.

### Follow-up candidate: restricted interconnect

After Terra exactly reproduced the published n=9 root sorter, a credible
alternative explanation is memorized standard benchmarks. Real sorting
networks can be constrained by available comparator links. One natural
candidate is six wires with every adjacent pair and shortcuts (0,3),
(1,4), (2,5), limiting the comparator library to eight links. Determine
whether exact BFS can certify a nontrivial optimum and preserve
state-changing random resets. No model calls in this feasibility check;
if available, a new fixed interconnect target could test memorization
versus construction. Every adjacent link is necessary to repair the binary
row with a single adjacent inversion, so the line backbone guarantees a
solution via an ordinary adjacent sorting network.

Feasibility outcome: exact bitset BFS for the six-wire, eight-link graph
visited 8,583 states and found optimum 12 comparator actions. Its
shortest path is (0,1),(1,2),(0,1),(3,4),(4,5),(3,4),(0,3),(1,4),(2,5),
(2,3),(1,2),(3,4). This demonstrates that a nonstandard hardware
interconnect benchmark can be constructed and proved locally rather
than relying on a memorized public catalogue. It is a separate future
candidate, not part of the frozen sorting screen.

After Terra solved all observed continuation cases, exact shortest remaining
distances were registered as a follow-up diagnostic: compare action count
from frozen successful continuations with the optimum of their actual state,
rather than with the universal root budget. BFS is bounded to 250,000 visited
states. This determines whether the model is efficient at the native partial
state even when it can finish.

## Results

The frozen screen completed all 12 scheduled calls. Eleven returned legal
comparator arrays. One Luna six-wire known-prefix call timed out at the
predefined 180-second limit without an answer; it is counted as a failed
attempt, not an invalid sequence. All returned actions were independently
replayed with scalar tuple compare/exchange in addition to the native
bitset verifier. Recorded prompt/answer hashes match local artifacts.

| Model | n=6 root | n=6 random | n=6 known | n=9 root | n=9 random | n=9 known |
|---|---:|---:|---:|---:|---:|---:|
| Luna (success / returned comparators) | 0/9 | 0/1 | timeout | 0/25 | 0/21 | 0/4 |
| Terra (success / returned comparators) | 1/12 | 1/2 | 1/3 | 1/25 | 1/12 | 1/3 |

Luna's two random-start attempts each leave just one unsorted row; neither
gets terminal reward. Terra solves every case and exactly reproduces the
published 25-comparator nine-wire root witness. This suggests memorization of
a familiar public benchmark; standard sorting is not a sufficiently hard
frozen-Terra task. Native state-specific compression nevertheless lowers
Terra's solution cost substantially. Exact reset distances (see
exact_results.json) are n6 random 2, n6 known 3, n9 random 7, n9 known 3;
Terra uses 12 comparators for the state optimally solvable in 7.

Random-policy calibration results (2,000 rollouts per cell, terminal binary):

| n | Root | Fixed random reset | Independent fresh random resets | Known prefix |
|---|---:|---:|---:|---:|
| 6 | 0 | 655 | 475 | 250 |
| 9 | 0 | 10 | 17 | 298 |

Thus the environment demonstrably exposes terminal rewards to an untrained
uniform policy from legal random starts. n=6 random states are relatively
easy; n=9 remains sparse even from long random prefixes. The family is a
potentially strong controlled RL test for smaller policies; the standard
Terra frozen task is too familiar to justify a hard-task transfer claim.
A memory-resistant interconnect restriction is one follow-up candidate.

Compact evidence: frozen_results.json, random_policy_results.json,
exact_results.json, and executable scripts. Raw prompt, answer and event
logs remain at /tmp/sorting_initial_20261127, schema.json included;
frozen_results.json preserves output actions and hashes.
