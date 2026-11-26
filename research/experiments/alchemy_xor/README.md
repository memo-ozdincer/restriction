# Alchemy pilot: multi-output XOR synthesis

Registered before running. Hypothesis: native, target-independent random
circuit prefixes expose useful intermediate computations and produce a
better *frozen transferable* gate-efficiency policy than further ordinary
RL, even after ordinary competence. If all learning merely discovers
success faster, or frozen held-out cost is not improved, the stronger
hypothesis fails here.

## Environment and controls

- Independent full-rank five-input/five-output GF(2) maps uniformly sampled
  via rejection of uniformly drawn unordered output sets. No selection by
  cost, motif or intervention success. Fixed generator seed 20261127,
  256 training maps, 128 validation, 256 held-out; disjoint unordered maps.
- All nonzero 5-bit masks are legal symbolic wires. Start with five basis
  masks. Each action chooses a new nonzero XOR of two already available
  masks. Duplicate wires are quotiented out. Policy chooses result mask
  (state transition), legal operand pair selected uniformly; full DAG
  retained. Pair choice is not a learned strategy; structural diagnostics
  refer only to learned choices of new mask. Exact checker validates every
  gate and target set. Complete immediately on correctness with terminal
  reward 1+(20-L)/20, otherwise zero. L counts every gate, including
  prefix and unused gates. All arms have same 20-action total cap.
- Shared small stochastic linear actor with 17 generic per-action features:
  legality from native XOR operation, result membership in target set,
  candidate Hamming weight, number of valid parent pairs, available
  and missing-mask counts bucketed by XOR Hamming distance to candidate;
  plus count of missing-output masks made reachable using candidate and
  existing masks (native one-step action geometry, no solver). Same
  features in all arms, no process reward. Adam, batch-mean terminal
  REINFORCE, no oracle trajectory or output labels.
- Four paired seeds, 42..45. 64 proposals/update. 1200 common ordinary
  updates then competence gate: >=80% validation root success and
  mean reward greater than initialization. Fork shared weights/Adam
  state, same train map sequence, 1800 further updates. Ord root-only,
  uniform native random prefix, and same-depth on-policy prefix (frozen
  sampling during prefix, learning only from suffix). Prefix length
  uniform 0..8, charged against horizon; if accidentally completes
  target, record and exclude from update (no repeated prefix draw).
  Equal episode/padded primitive action slots; record actual native
  moves/policy calls/reset moves as well. Exposure is not a fair
  computational advantage if actual policy/transition budgets differ.
- Frozen held-out from empty root (8 rollouts per map), before and
  after continuation; no extra learning to test. Compare correctness,
  mean terminal reward, mean gate cost conditional on correctness, and
  motif statistics (shared intermediate gate used by >=2 distinct target
  output DAGs; cancellation ancestor whose support is not a subset of
  a downstream target output). Independently replay every evaluation
  gate. Compare motifs within identical gate-count bins; a motif rate
  alone cannot prove causality. Gate optimum not given to policy.
  No special target or selected successful cases. This is a pilot, not
  a novelty claim. No training if common competence fails.

Implementation smoke (three updates/arm, not scientific result) passed
concrete truth-vector replay; found and fixed a moved-from vector in
one-step reachability feature (preserve a fixed legal-result snapshot
before moving action records). No pilot outputs consulted for task
selection/tuning.

## Post-run ceiling diagnostic (registered before audit)

All arms solved every held-out instance but ordinary gates were slightly
shorter. Determine whether the small task itself is nearly saturated:
independently compute exact minimum gate count per held-out target by
iterative-depth DFS over *sets* of available masks, using only a lower
bound of one gate per missing target and duplicate state elimination.
Report optimality gap and exact optimal output rate. This is an offline
diagnostic solely to decide whether a bigger domain is needed; no
training, task selection, or learner inputs will use these optima.

## Results

Job 2939367, def-zhijing/debug, tri0273, 192 CPU allocation/four
single-process seeds, 12 seconds elapsed, completed 0:0. Source
and run configuration frozen in the remote directory
/scratch/memoozd/rrl/alchemy-xor-20261127. Job output and checksums
preserved, all downloaded output hashes verified. Initial repo HEAD
was 4ead95f; experiment files were untracked. The source snapshot hashes
are also recorded in 2939367.log. No external model or dataset.

Every seed passed the competence gate: initial validation 133–169/512,
common checkpoint 512/512. Both common and all later policies succeeded
on every 2,048 frozen held-out rollouts per seed. Independent Python
replay (audit.py) checked 32,768 traces and every primitive gate, target
rank, exact truth vectors, terminal stop, gate count, motif counts, and
summary statistics. All passed.

| Arm | Gate count (mean, correct) | Exact optimum rate | Shared intermediates | Cancellation ancestors |
|---|---:|---:|---:|---:|
| Common | 5.73669 | 6,233/8,192 (76.1%) | .73486 | .67993 |
| Ordinary continuation | 5.56433 | 7,400/8,192 (90.3%) | .71765 | .61035 |
| Uniform native prefix | 5.60376 | 7,114/8,192 (86.8%) | .70007 | .59363 |
| On-policy prefix | 5.57556 | 7,316/8,192 (89.3%) | .72180 | .61340 |

Ordinary beats random exposure on each paired seed (gate cost difference
0.025–0.054). Both exposed controls still improve relative to the shared
checkpoint. Random exposure does not discover a beneficial additional
structural motif: within 5/6/7-gate bins its mean sharing and cancellation
counts are lower than ordinary. These diagnostic counts alone do not
prove causal use of a strategy, and pair choice is uniformly random;
the trained model chooses the mask, not the exact operand decomposition.
No ablation needed without a gain.

Exact offline DFS audit (optimum.cpp, optimum.csv) finds mean optimum
5.46484375 and maximum 7 gates across all 256 held-out maps. Thus ordinary
already reaches about .10 gate absolute optimality gap; random prefix
is further away (.139 gates), on-policy prefix .111. The environment
has a strong ceiling, so not an informative test of much more advanced
mathematical skill. This is a negative result, not evidence that broader
environment exposure can never improve strategy discovery. No more
seeds or task retuning launched.

Compute caveat: both continuation arms have 115,200 proposals and
2,304,000 padded primitive slots per seed. Representative seed 42:
ordinary 630,101 actual gates/policy calls, random 919,883 actual gates
of which 460,766 are random reset actions and 459,117 policy calls;
on-policy 631,996 gates/calls including 396,822 reset actions.
Already-terminal prefix episodes (189 random and 44,977 on-policy in
seed 42) were scored and counted against proposal budget but did not
train, as predeclared. In the on-policy control this is a substantial
loss of learning samples; it is not a clean equal-trained-count control.
Random exposure's lower policy-call vs higher actual gate count likewise
precludes claiming exact matched realized compute (padded slots are
matched). Prefix sampler is target independent except rejection of
terminal prefixes. No gradient or solution labels from rejected draws.

Reproduction:
```sh
g++ -O3 -std=c++17 run.cpp -o run
mkdir new-results
./run 42 new-results
python3 audit.py results > audit.json
g++ -O3 -std=c++17 optimum.cpp -o optimum
./optimum results/maps-42.txt > optimum.csv
```
Audit expects all four seed outputs. Full 4-seed launch via sweep.sbatch.
