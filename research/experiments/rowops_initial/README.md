# Minimal elementary matrix operation synthesis

Hypothesis registered before model sampling: a fixed hardest invertible
three-by-three matrix transformation over GF(3) is substantially harder
from identity than from randomized near-goal matrices, and uniform random
invertible starts may provide intermediate reward access. Every action
modifies the current matrix, so the current state cannot be ignored.
A second hypothesis is that familiar row arithmetic may be more accessible
to language models than bit-level generalized Toffoli synthesis.

The state is the current 3×3 invertible matrix over integers modulo 3.
Allowed actions are row addition/subtraction and row negation, each costing
one action. There are 15 actions: 12 add/subtract operations for ordered
distinct rows and 3 row negations. No swap primitive (it can be synthesized).
The terminal success reward is 1 for exact target equality within 7 actions;
otherwise 0. No intermediate reward or human reasoning feedback.

The source task is the identity-to-fixed-matrix transform. All 11,232
states of GL(3,3) are reached by exact BFS and the diameter is 7. The
target is the lexicographically first distance-7 matrix:
[[0,0,1],[1,0,0],[0,2,0]]. Its optimality is independently established by
BFS, and a legal witness is reconstructed and verified.

The matched frozen diagnostic compares 4 attempts each of root,
uniform-random valid matrix, and near-goal random walk (1..4 steps,
with accidental goal resets excluded) in both gpt-6-luna and
gpt-6.1-terra, low effort. Exact distance is recorded for analysis only.
All use the unchanged action budget 7, and every uniform/near state is
feasible within that budget by group transitivity and the exact diameter.
Random seed 20261127; same starts for both models. No solution, distance,
tools, intermediate checker feedback, or references shown to models.

This is a small local variant of linear reversible circuit synthesis,
which maps binary CNOT synthesis to elementary matrix decomposition
and admits extension to larger finite fields. See Patel, Markov and Hayes,
[Efficient Synthesis of Linear Reversible Circuits](https://arxiv.org/abs/quant-ph/0302002).
The GF(3) 3×3 panel is newly generated, not a published benchmark split.

## Frozen results

All 24 responses resolved and independently replayed with a separate
row-list evaluator. Every response contains nonempty legal actions.

| Model | Root (distance 7) | Uniform (distances 5,5,4,4) | Near (distances 1,2,3,4) |
|---|---:|---:|---:|
| Luna | 1/4 | 0/4 | 2/4 |
| Terra | 4/4 | 4/4 | 4/4 |

Luna's root success takes 7 actions (optimal); near successes have length
1 and 3, optimal. Terra root solves all at optimum 7. Uniform success
lengths 5,7,7,4 and near success lengths 1,2,3,6. Terra is too capable
for this particular 3×3 target, but it is a plausible Luna task and
all conditions receive substantive action sequences (unlike decimal
opaque truth-table failures). Uniform starts were harder than root
for Luna despite lower exact distance, plausibly because the root
matrix has a simple signed-permutation target, while uniform starts
require more general intermediate arithmetic. This single four-attempt
panel is exploratory, not a stable pass-rate estimate.

Raw prompts and model responses, exact starts/distances, usage, hashes
and independently reverified outcomes are in frozen_results.json.
Operational JSONL and stderr logs are retained locally in
/tmp/rowops-{luna,terra}-{root,uniform,near}-20261127.
No training performed.
