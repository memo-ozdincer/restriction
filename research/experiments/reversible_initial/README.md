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

## Frozen single-target diagnostic

Registered before sampling: 4b15g_1, fixed 15-action budget, both Luna
and Terra at low effort. Four independent root attempts, four uniform
permutation resets, four near-target resets (random walks of lengths 1..4
from the goal, reversed walks prove feasible completions). The latter
are a positive control only, with no exact distance claim. Starts shared
between models; no solver, feedback, or solution supplied. Hypothesis:
near-target starts enable positive reward where the published maximum
distance target is otherwise too difficult. Uniform starts test whether
indifferent exposure alone helps. The user's explicit concern is that
the 15-gate target may be too hard even for Terra. This diagnostic
determines whether we should begin RL with a less difficult target.

### First frozen results

All 24 responses resolved and independently replayed. Luna 0/4 ordinary,
0/4 uniform and 0/4 near. Terra 0/4 ordinary, 0/4 uniform, 3/4 near.
Terra's successful near continuations took 1, 3 and 3 gates respectively.
Terra produced empty actions for every ordinary and uniform start.
Thus 15-gate root synthesis is out of reach under this frozen sampling
budget for both models, but Terra can complete short suffixes without
a supplied trajectory. Uniform random starts did not unlock any wins.
This supports testing reset distributions around the goal rather than
expecting uniformly random permutations to produce near-target experiences.
A lower-cost diagnostic on an exactly eight-gate three-bit target can
separate task-size effects from the one-shot interface. No training yet.
Compact results, model actions and prompt/answer hashes in frozen_results.json;
raw prompts (containing copyrighted target specifications), answers and
operational logs retained locally at /tmp/reversible-{luna,terra}-{root,uniform,near}-20261127.
Screen source 853d0ac. User raised concern 15 gates may be too hard for both.

### Aurora local-GPU follow-up (prepared 2026-11-26)

Hypothesis: an exactly eight-gate three-wire target will expose a usable
positive-reward region for locally available instruction models, even if
four-wire root synthesis fails. A matched second model distinguishes broadly
poor reward availability from a checkpoint-specific limitation. This is a
frozen inference diagnostic, not RL training. The decision is whether to
begin RL on three-wire exact distance shells or first simplify the task.

`local_screen.py` deterministically selects one optimal-distance-eight target
(seed 20261127), repeats four root attempts, samples four uniform starts and
one start at each exact goal distance 1–4; every case has budget eight.
The same 12-case panel, sampling settings and strict independent gate verifier
are used for both Qwen3-4B-Instruct-2507 (cached pinned snapshot) and the local
Qwen2.5-7B-Instruct base instruction checkpoint. No solver trajectories or
feedback are provided to the models. `--preview` is CPU-only. Reused runtime:
`/mfs1/u/memo/rcc-research/envs/rcc-managed312` (torch 2.14.0+cu130, Transformers
5.3.0), with no changes to that environment. `local_screen.sbatch` prepares a
two-task array (one GPU per model), writing independently to
`/mfs1/u/memo/rrl-phc/runs/`. No weights are modified.

CPU verifier tests and panel checks passed. Original Lean preflight was run;
its Ray/Lean/Python 3.11 checks are not satisfied on Aurora and are not used by
this standalone diagnostic. The host exposes no NVIDIA devices and its
installed Slurm client cannot locate `/pkgs/slurm/etc/slurm.conf`. Initial
submission timed out without a job ID; no runs are claimed queued or started.

## Full matched GRPO experiment (2026-11-26)

The user asked to proceed directly to RL: practice from genuinely random
current circuits instead of always practicing from identity. Hypothesis:
training on a diverse distribution of current permutations provides learning
signal that transfers to solving the same difficult target from identity.
The decision is whether exploratory reset exposure can improve root synthesis
under the same physical rollout budget, not whether it merely improves
continuation success. This supersedes the diagnostic as a prerequisite; no
additional screen result is required to launch the training arms.

| Factor | Identity control | Exploratory arm |
|---|---|---|
| Target | Fixed optimal-distance-eight three-wire permutation `[1,5,4,3,0,2,7,6]` | Same |
| Current state | Identity each time | Independent uniform nonterminal permutation with replacement |
| Budget | 8 gates | 8 gates |
| Reward | Binary exact replay success | Same |
| Initial model | Cached Qwen3-4B-Instruct-2507, revision `cdbee75f17c01a7cc42f958dc650907174af0554` | Same |
| Optimizer | TRL 0.29 GRPO, LoRA r16, lr 5e-6, BF16, DR-GRPO, KL beta .01, one iteration | Same |
| Rollouts | 512 groups × 8 completions = 4,096 | Same |
| Root evaluation | 128 before and 128 after, matched seed and sampling | Same |

The exploratory arm samples the full distribution, not near-goal-only walks;
excluding the solved state avoids free rewards. No path witnesses or exact
distances appear in the prompt. The fixed exploratory sample spans exact
distances 2:3, 3:11, 4:37, 5:117, 6:211, 7:130, 8:3 (groups). This is
intentionally not a curriculum or specially selected collection of easy
starts. The target and gate library are unchanged from the three-wire screen.
The baseline is an existing pristine instruction checkpoint, not a medical
or persona adapter, to avoid injecting unrelated learned behavior.

Reuse the RCC-managed Python environment and its installed TRL GRPO/PEFT
backend; no new environment or unrelated training code changes. The trainer
records every answer and exact verifier verdict, per-group reward and
truncation counts, identity evaluation before/after, adapter fingerprint
changes, resolved training configuration and model/run provenance; policy
updates are tracked separately from mixed-reward groups. All-zero reward
training is a possible result, not a reason to change the verifier or
oversample only one arm. Both arms use identical temperature .7, top-p .95,
384-token completion budget, one allocated BF16 GPU and a new LoRA adapter.

`train_grpo.py --arm identity --preview` and `--arm exploratory --preview`
validate and print the deterministic plans without GPU allocation. Submit both
arms via `sbatch research/experiments/reversible_initial/train_grpo.sbatch`.
The job array runs one independent arm per allocated GPU. The final comparison
is `python3 research/experiments/reversible_initial/compare_grpo.py IDENTITY_RUN EXPLORATORY_RUN`,
which rejects mismatched configurations or proposal counts and reports the
absolute and baseline-adjusted difference in identity-start success. These
are same-target transfer metrics, not held-out-target generalization.

Training data and outcomes remain within `/mfs1/u/memo/rrl-phc/runs/`.
No training results are claimed until GPU execution completes. Eight circuit
unit tests passed, and a tiny CPU-only TRL integration run verified actual
rollout grouping/reward metadata and confirmed an adapter update under
synthetic mixed rewards. This smoke uses random tiny weights and is not an
experimental result. Aurora still has no NVIDIA devices visible and
the installed Slurm client has no configuration file; attempts to submit
have not returned a job ID.
