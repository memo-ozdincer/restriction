# Targets where ordinary terminal RL cannot get rolling

User direction: "i think fundamentally then we really want to target
things where the model CAN'T get the ball rolling in regular rlvr"
and "you can send multiple subagents to try multiple things that ideally
get the 'regular rlvr can't do it' behaviour."

Following the long subset-sum result (ordinary RL eventually saturates),
the scientific criterion is a measurable reward-access barrier plus
successful assisted-to-unassisted learning at matched budgets. Absolute
impossibility is not claimed; an exact nonzero first-hit probability can
imply impractical compute. Before first terminal reward, a pure
REINFORCE learner with zero baseline reward and zero optimizer moments
receives zero gradient, so the initial-policy hitting probability
predicts its discovery waiting time.

## Positive fixed-task experiments

### Eight-wire nearest-neighbor sorting network

Exact optimal budget 28, 40,320 reachable native states, all 256 binary
input rows exhaustively verified. Same linear stochastic policy, exact
terminal reward and action budget, paired initialization, 2,000 updates,
128 episodes each. Ordinary 8/8 seeds zero reward, zero fresh success
and bit-identical parameters. Exact uniform-random root probability
1.0567e-10, initialized policies 5.8e-11..2.07e-10, expected first
ordinary reward 4.84–17.20 billion episodes. Even 60,000 updates
have <0.08% chance of first reward for each initialized policy; this
is a mathematical extrapolation of unchanged pre-reward policy,
not a literal 60,000-update run.

Native random comparator walks 1..18 followed by root-only at 30%
give 99.39% mean exact root probability, 4,073/4,096 fresh success,
8/8 seeds; walks 1..24 give 99.44%, 4,075/4,096. Radius18 continued
81.28%; switched policy had 55.03% mean root success at switch,
so root specialization improves an already acquired skill. All 21,331
fresh successes independently replayed; radius18 switch discovers 949
distinct optimal networks. Reset overhead +5.74% actual transition
simulation versus root while policy budgets match. Strongest current
neural (linear softmax) terminal-only result.

### Sliding puzzle

Fixed ordinary start at exact depth 29; complete 181,440-state graph.
Uniform legal random hit probability 1.9274e-12 within 29 moves,
expected 519 billion episodes before first positive. Tabular
finite-horizon Bellman learning, binary terminal value, no distance
or reference action targets. Ordinary 0/2048 final, root-centered
walks 0, goal-centered continued 0, goal-centered-to-root 2048/2048,
uniform continued 1541/2048, uniform-to-root 2048/2048, four paired
seeds. Identical maximum policy action slots, uniform-to-root uses
fewer actual actions. 5,637 fresh successes scalar replayed, all
optimal 29 moves. Distinguish tabular propagation from representation
transfer or GRPO.

### Tower of Hanoi

Trillium CPU two jobs 2938970 and 2938979, each completed on an
entire 192-core def-zhijing/debug node in 18 seconds. Five disks
optimal 31 moves, six disks optimal 63. Exact random-policy root
probabilities 2.43e-15 and 1.31e-30, respectively. Shared linear
policy failed for every reset distribution and obtained many
assisted wins without any meaningful root improvement. Capacity
ablation uses state-specific logits initialized to the identical
initial output policy, terminal REINFORCE otherwise retained.
Five-disk uniform continued 45.76%, uniform→root 99.25% across
eight seeds, ordinary ~2.44e-15 with zero rewards. All 16 positive
policies evaluated in 512 fresh episodes each: 1,837/4,096 continued,
4,080/4,096 switched, independently replayed all successes as exact
31-move solutions. Six-disk all arms fail at this budget. All 192
saved policy probabilities independently checked along the unique
shortest path. This is a capacity diagnostic and tabular success,
not evidence of neural feature transfer.

## Interpretive boundaries

- Use "effectively reward-starved at an explicit budget", not literal
  impossibility. First-hit theory holds for unchanged policy before
  first reward; entropy bonuses, MCTS, pretrained models or alternative
  learning algorithms may alter exploration.
- Single-task fixed-goal competence is not generalization to new tasks.
- Exact distance and optimal witnesses are offline certification only;
  policies get no expert trajectories or distance-shaped rewards.
- Pure resets preserve terminal equality and primitive action cap;
  reset construction is external simulation and must be charged.
- No claim of LLM RLVR; the sorting/reversible experiments use learned
  small stochastic policies, sliding uses tabular Bellman, Hanoi
  compares linear and tabular terminal policy gradient.

See individual reports for full methods and evidence:
[sorting](experiments/hard_sorting_bottleneck/README.md),
[sliding](experiments/hard_new_bottleneck/README.md),
[Hanoi](experiments/hanoi_bottleneck/README.md).
