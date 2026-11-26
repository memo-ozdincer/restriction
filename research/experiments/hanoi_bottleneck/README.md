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
