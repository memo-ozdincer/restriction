# Sliding tile random-start diagnostic

## Preregistered question

Can frozen small language models solve a conventional sequential 8-puzzle
from randomly sampled near-goal states when an independently selected hard
start is too difficult? The task is a single fixed goal, canonical sorted
3×3 board with blank at bottom right. Legal actions slide the blank one
square up/down/left/right. All conditions share goal, rules, terminal
correctness reward and 29-move limit. No solver path, verifier feedback,
distance, or intermediate hints in model prompts.

The complete legal-goal component is enumerated via reverse BFS solely
for experimental reset calibration and verification, not accessed by the
model. Choose one seeded uniform board from exact distance 29, and one
seeded uniform board from each exact distance 1, 3, 5 shell. These are
states independently sampled from a graph, not a prefix of a known
solution to the hard board. Freeze the board panel before querying
gpt-6-luna and gpt-6.1-terra at low effort (one attempt per board per model).
Hypothesis: near-goal success with no hard-board success indicates accessible
terminal feedback; this does not demonstrate training or transfer.

This is a conventional search domain; see the Korf sliding tile benchmark
context at https://www.ns-software.com/SAS/STP/ . The related general near-goal
curriculum principle is established by Florensa et al.,
https://proceedings.mlr.press/v78/florensa17a.html (2017). This pilot is a
locally exact 8-puzzle variant and does not claim to use Korf's 15-puzzle data.

## Results (eight independent frozen attempts)

| Exact start distance | Luna | Terra |
|---:|---|---|
| 29 | Failure, 29 legal moves | Failure, empty response |
| 1 | Success, 1 move | Success, 1 move |
| 3 | Success, 3 moves | Success, 3 moves |
| 5 | Failure, 27 legal moves | Success, 5 moves |

Luna 0/1 hard and 2/3 near; Terra 0/1 hard and 3/3 near.
All eight submissions were well-formed legal move sequences, although an empty
response is technically valid syntax. Both near-success sets contain exact
shortest solutions. The exact 29-move root had one legal but wrong Luna
trajectory and an empty Terra trajectory. The conditions compare genuinely
different initial states while using identical prompts except the current
board. Unlike AIG optional wires, neither agent can ignore the board state.

All cases and answers independently replayed using a grid-based checker, with
goal and budget verified. The BFS has all 181,440 reachable states, maximum
distance 31. All three unit tests passed. No training was conducted; these
are single draws per case. The result supports reward accessibility near
the fixed goal, not transfer or a guarantee that uniform random starts
provide positive rewards. This problem is also a known search domain, so
it should be treated as a clean diagnostic environment rather than new
algorithm discovery.

Tracked panel.json and frozen_results.json contain all board states, model
actions, timing, exact result and raw prompt/answer hashes. Original logs
remain at /tmp/sliding-{luna,terra}-20261127. Runner uses codex exec with
ephemeral session, read-only isolated cwd, no tool use, low effort, strict
JSON schema; model IDs gpt-6-luna and gpt-6.1-terra.
