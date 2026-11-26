# Reversible circuit state exposure

User selected a genuinely changing start state and one very hard target.
Classical combinational reversible synthesis, positive-control generalized
Toffoli library, no extra wires. Each gate toggles one target bit if all
its controls equal one. Four wires give 32 allowed gates (4 NOT, 12 CNOT,
12 Toffoli and 4 three-control Toffoli).

The observation is the complete permutation of 16 inputs, with a fixed
target permutation and remaining action budget. Each action composes the
current permutation with one gate. Unlike append-only AIG wire pools,
there is no option to ignore the current mapping. The verifier checks
all input assignments. The ordinary start is identity. A true random
reset is a uniformly sampled permutation, independent of any solution.
All permutations are reachable because the full library includes
three-control Toffoli gates; the root target remains the same.

## Published benchmarks

Golubitsky and Maslov, A Study of Optimal 4-bit Reversible Toffoli Circuits
and Their Synthesis (https://arxiv.org/abs/1103.2686).
The five 4b15g benchmark specifications and published 15-gate witnesses
are downloaded from https://reversiblebenchmarks.github.io/. Every witness
was independently replayed successfully. Optimality is published in the
source, not independently recomputed for the four-bit cases.
The copyright notices prohibit redistribution without permission. Raw
specifications and circuits stay local in ../circuit-tools/reversible-benchmarks;
inventory.json records hashes and verification evidence. Recreate with
python3 research/experiments/reversible_initial/setup.py.

Three-wire sanity check: exhaustive BFS reaches all 40,320 permutations,
with distance histogram [1,12,102,625,2780,8921,17049,10253,577] for distances
0..8, matching the published three-bit NCT distribution (Shende et al.,
https://web.eecs.umich.edu/~imarkov/pubs/conf/c026.pdf).
Run python3 -m unittest discover -s research/experiments/reversible_initial.

## Design question before training

A reset is the current transformation itself, not free gates appended to
a program. Training continuation cost counts new actions; root evaluation
counts every action from identity. Fixed terminal success and action budget
are kept identical across conditions. Uniform random resets may still be
too far from the target to produce reward. Measure exact distance shells
on three bits and test a fixed published four-bit target before choosing
reset distributions or training architecture. No training run started.
