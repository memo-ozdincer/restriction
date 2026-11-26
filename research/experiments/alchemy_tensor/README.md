# Exact tensor compression beyond reward bootstrapping

## Registered hypothesis (before running)

Already-correct 2x2x2 binary tensor decompositions let every rollout receive
terminal rank-efficiency reward. Does unguided native exposure at **equal
or greater decomposition cost** teach reusable transformation behavior that
competent ordinary RL does not acquire? A positive result must improve
held-out, unassisted rank after common ordinary training; mere faster
first correctness or easy-state access is ruled out by construction.
A structural signature (counts of voluntary expansion and subsequent net
rank reduction, conditioned on quality) is descriptive only, not a reward.

Use all 70 rank-four coordinate expansions (4 of 8 basis terms), split
by seed 20261127 into 48 training, 8 validation, 14 independent test
targets. No selection by intervention or optimum. All legal flips and
plus operations from the existing finite tensor graph remain available,
cap five in every arm. Include explicit stop-equivalent identity action.
No early termination; every endpoint is scored (1 - rank/6, positive
for all rank <=5). Exact target is preserved by every native edge.
Features are raw decomposition term indicators, shared state-to-action
MLP across all targets. No distance/rank-optimum labels. Group-relative
REINFORCE, Adam, seed-paired ordinary pretraining, then fork weights and
optimizer. Validation must show >0.5 mean savings from rank4 for common
competence; if not, pilot does not test alchemy. Stop gate evaluated only
at fixed checkpoint, not by exposure results.

Exposure uses two randomly chosen native moves per start, constrained
to not reduce rank below root (rank >=4). No oracle, no supplied good
decomposition. These moves consume the first two of eight available
primitive slots, leaving six learned decisions. Compare root-only eight
learned decisions, and an unrestricted uniform-native two-move prefix
followed by six learned decisions (random action exploration control).
The latter may supply cheaper states; track prefix end rank. Same
terminal reward, actor, cap, train roots, group size, optimizer and
total primitive slot budgets. Exposure and prefix control have fewer
policy calls than ordinary; count actual candidate scores and all
prefix candidate enumeration. No claim of equal wall clock. No extra
final specialization. Evaluate fixed held-out original roots, all
eight learned decisions, exact verification, independent RNG. Report
matched-seed differences and all nulls. Tiny environment and pilot
budget, no claim about large tensors or absolute impossibility.

A local implementation smoke inadvertently ran the full 400+400 updates
for seed 42 because macOS multiprocessing spawn reimported the module
defaults, while the output header advertised two updates. This is not
counted as a valid smoke or the cluster panel; the bug was corrected
by passing explicit iteration counts in each worker job. The corrected
two-update smoke completed with scalar verification and no competence
(expected). The accidentally observed seed42 point had strong common
competence and near-equal held-out arms; registration otherwise unchanged.

Cluster provenance: source tree HEAD c4135f851d8b746daa36c7824007924f81721a9d;
new experiment directory untracked at staging (all scripts hashed).
Staging location /scratch/memoozd/rrl/alchemy-tensor-20261127.
Debug submissions rejected twice due to another same-user debug job;
submitted once successfully via `sbatch --partition=compute` (same
preferred def-zhijing account, original script otherwise unchanged).
Job 2939371, one whole CPU node. Resolved config: 4 independent
one-thread workers, seeds 42–45, common400+fork400 updates,
4 groups x16 episodes, H8, Adam 0.003, test64 draws per held-out target.

## Results (job completed; no follow-up scale)

Trillium compute/def-zhijing job 2939371 completed on tri0147 in ten
seconds (exit 0:0). Source hashes and hardware/python details are in
the small job log; output hashes matched retrieval. All four common
policies qualified (validation mean rank savings 1.709–1.783).
All arms evaluated on 14 unseen target tensors x64 rollouts x4 seeds,
all from rank4 coordinate root, no reset or assistance. Every trajectory
replayed with an independent coordinate-scalar verifier. Exact
minimum ranks were enumerated *after* training (audit.py), solely
for interpretation. Mean optimal held-out rank: 2.142857.

| Condition | Held-out mean terminal rank (lower better) | Expansion then terminal rank <4 | Expansion among rank2 outcomes | Expansion among rank3 outcomes |
|---|---:|---:|---:|---:|
| common checkpoint | 2.26814 | — | — | — |
| continued ordinary | 2.20703 | 9.29% | 10.24% | 9.48% |
| nonshortening exposure | 2.19587 | 11.33% | 12.29% | 12.05% |
| unrestricted random prefix | 2.19894 | 11.24% | 12.38% | 11.52% |

Nonshortening exposure improved over continued ordinary by 0.01116 terms
(3/4 seeds), unrestricted random prefix by 0.00809 terms. This is a tiny
difference near the finite problem's ceiling, and unrestricted prefix
exploration reproduces almost the whole signature. No demonstrated
new strategy. Exposure did practice genuinely worse states: prefix
mean rank 4.608 versus 4.215 unrestricted, 2.433 learned ordinary.
The two exploration arms both exhibit slightly more expansion, including
when conditioned on quality, but this is not specific to nonshortening
exposure and could just reflect higher stochastic exploration.

Exact paired primitive budget per post-intervention arm: 819,200
slots (four seeds), ordinary all learned, exposure and unrestricted
614,400 policy +204,800 prefix actions. Candidate enumeration/scoring
costs were 7,696,376 ordinary, 9,178,375 nonshortening, 8,953,568
unrestricted; candidate compute is not matched, no wall-time or
sample-efficiency claim. Total post-training reward checks 102,400
per arm; correctness preserved by every transition. Small reproducibility
artifact includes complete optimization summaries, final weights and
verified expansion witnesses. Cross-platform replay of all 12 final
policies exactly matched terminal-rank means; rechecked every stored
expansion witness against scalar semantics and native transitions.
No checkpoints trained on held-out targets.

Interpretation: this tensor family is not rich enough to establish
alchemy; continued ordinary was already close to exact optimum, and
randomization's tiny quality/motif differences are also present with
unrestricted prefixes. A qualitatively harder tensor family would be
needed; do not merely increase seeds or iterations in this one.
