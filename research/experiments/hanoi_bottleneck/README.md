# Tower of Hanoi: long-horizon terminal-only RL

Hypothesis registered before sampling. A fixed five- or six-disk puzzle
has a 31/63-action optimal root solution and a severe sparse terminal
reward barrier. Native random legal starts may supply transferable
skills without changing the actual puzzle, moves, goal or action cap.
Test uniform legal resets, short random root walks, goal walks, and
near/uniform-to-root specialization. Ordinary-only is the matched long
control. An exact finite-horizon random-policy diagnostic establishes
initial reward accessibility. No reference trajectories, distance
features or dense rewards used during training. Each disk's pole is
known; a legal move transfers the top disk onto an empty pole or a
larger disk. Illegal moves are masked identically in all arms, including
evaluation. Goals are all disks on pole 2; ordinary root all on pole 0.
All 3^n assignments are legal stacks, so uniform starts are truly
trajectory-independent. Exclude already-solved starts.

Same small linear stochastic policy, exact terminal reward, Adam and
full action horizon in all conditions. 128 candidates/batch, 3000
updates, eight paired seeds 42..49 for both disk sizes. Modes root,
uniform, uniform-switch, goalwalk, goalwalk-switch, rootwalk,
rootwalk-switch. Fixed switch at 60%. Goal/root walks of uniformly
random length 1..12 legal moves. No outcome-selected resets.
Exact official-root success probability computed at final checkpoint;
sampled root evaluations at intervals. Account for actual moves and
fixed padded policy slots; reset generation is reported separately.
One fixed task per size, no generic capability or reliable novelty
claim. Long horizon may challenge the policy architecture itself;
assisted success is necessary to distinguish that confound.

Cluster launch: Trillium job 2938970, def-zhijing/debug, one 192-core
node, 112 independent workers, 20-minute limit. Isolated directory
/scratch/memoozd/rrl/hanoi-bottleneck-20261127. Remote SHA-256:
run.py b89d452d1ea353c3dfefa9f3c2d0236e64aa3601d8d5336cb322289d4e31792f;
sweep.sbatch f7e2d1a69c1aaf4f0f610113ec1cbfd0cb400da529d8ab0bb8f194d166d6ce22.
Initial exact random-policy root hit probability: 2.428e-15 (5 disks),
1.311e-30 (6 disks). Thus even 384,000 proposals would give essentially
no initial reward to the uniform policy. This is a far stronger test
than subset sum, whose long baseline could reach a first success.

Initial cluster results: all 112 trajectories complete, 18 seconds node time.
No trained condition produced a material root-success improvement on either
size; root and rootwalk arms obtained zero rewards. Goalwalk and uniform
resets obtained hundreds of thousands of successes, yet reduced root
probability, in some cases by more than 20 orders of magnitude. This does
not establish a capacity gap in ordinary RL because assisted learning also
fails. Targeted follow-up registered before execution: replace shared
linear logits with a state-specific table, initialized to exactly the same
policy, retaining original terminal REINFORCE, optimizer, seed panel,
action slots and reset schedules. Test whether lack of expressivity/shared
representation is responsible for the observed collapse. No solver values
or action labels enter the training. This is a capacity ablation, not just
more seeds. Five arms x two sizes x eight seeds.

Follow-up job 2938979 submitted def-zhijing/debug, 192-core node,
80 workers. Remote source hashes tabular.py
e3cb88a018bba7776a297dfdd0db59573e556d73d353976e3cc6d93512e21008;
tabular.sbatch 3ad0f1b96a3ace92ec1e665d13cbd21c0e1e349173015b62e1c372bf35551e91.

Capacity follow-up complete (job 2938979, 18 seconds node time).
Five disks: ordinary mean exact root probability 2.4422e-15 (zero
training rewards), uniform continued 45.76%, uniform→root 99.2543%,
all eight seeds >10%. Goal-centered walks fail despite millions of
near-goal successes. Six disks: all arms fail at this budget, including
uniform continued (1.38e-7 mean) and uniform switched (2.93e-11).
The tabular capacity ablation therefore unlocks one task; no evidence
of transferable neural representations. The same underlying state
and action rules and exact terminal checker were retained. Using a
different representation/parameter count is explicitly an ablation,
not a pure reset contrast with linear baseline. Within the tabular
panel all conditions use identical architecture.

Independent audit computes probability along the unique optimal path
using a separate stack-based move evaluator, with float tolerance for
float32 versus float64 policy calculation. All 192 saved policies
match the exact DP probability. Every high-success five-disk policy
sampled 512 fresh root episodes; all successful trajectories checked
at exactly 31 moves, 5,917/8,192 across the 16 successful policies.
Results archive SHA-256 matches remote evidence for both jobs.
Run audit.py to reproduce.
