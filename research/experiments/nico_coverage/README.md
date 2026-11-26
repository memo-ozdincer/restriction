# Published NICO checkpoint coverage audit

Registered hypothesis (before running): the published learned 2-opt policy
covers a small, strongly biased subset of its legal one-move neighborhoods,
even when repeated search trajectories explore the same problem. Diagnose
which part of the accessible state space remains unseen as search progresses,
using the actual released weights and actions, before choosing an intervention.

Four fixed synthetic Euclidean instances per size (20 and 50 cities), eight
independent chains per instance, 5n steps, seed 42. Same random initial tour
per set of eight chains; native action mask, history and progress retained.
Record canonical undirected tour identities; exact legal action counts and
probability mass on worsening moves; at steps 0,n,2n,5n assess whether each
admissible one-step neighbor was ever visited by any of eight chains.
Uniform comparison is only an offline one-move coverage diagnostic, no
training or change to original reward. One-step neighborhoods are local
coverage denominators, not global state-space coverage. Report checkpoint
config and provenance; released repo has newer config options than paper.

Sources: https://arxiv.org/html/2604.06940v1 and
https://github.com/TheLeprechaun25/nico-tsp. No claim of reproducing original
paper training; this audits the publicly released checkpoint.

Follow-up hypothesis registered after the coverage result: a uniformly
sampled admissible neighbor absent from the original eight recorded chains
may provide a different improvement signal under the actual checkpoint.
Test two checkpoints (2n, 5n-1) on chain zero of each of the four n=20
instances. Replay the full original state including history. Compare one
native 32-step G=20 group from the actual state against one from a random
unvisited neighbor. Reference cost is the same recorded best-so-far.
The extra reset move is charged separately; no reward-based reset selection.
Use the released group_advantages implementation and report whether
nonzero advantage actually appears. This is a diagnostic of local exposure,
not an equal-compute trained comparison.

## Result

Released checkpoint loaded strictly on Apple Silicon CPU, Python 3.11,
PyTorch 2.15.0. Source revision and full checkpoint hash/config in audit.json.
Checkpoint is RL epoch 119, with 20 RL epochs in current repo default and
50% later starts; this differs from the original paper's 200 RL epochs.
Do not conflate repository revision with paper experiment. PUZZLES source
also cloned at 9116c7b19b492993449e0c55b579c71e0c818d23; no checkpoint
execution from that repo yet (Linux-oriented setup).
NICO source local ../experimental-baselines/nico-tsp,
venv ../experimental-baselines/nico-venv. Reproduce audit and probe:
python audit.py --repo <nico source> --out audit.json
python probe.py --repo <nico source> --audit audit.json --out probe.json

| Size | Step | Admissible one-step neighbors seen anywhere in eight chains | Policy mass on those neighbors | Worsening-action probability |
|---|---:|---:|---:|---:|
| 20 | 0 | 1.03% | 96.67% | ~0% |
| 20 | 20 | 2.22% | 86.69% | 34.43% |
| 20 | 40 | 3.18% | 93.96% | 26.54% |
| 20 | 99 | 2.28% | 89.53% | 44.17% |
| 50 | 0 | 0.38% | 67.13% | ~0% |
| 50 | 50 | 0.23% | 74.61% | 34.51% |
| 50 | 100 | 0.35% | 80.39% | 46.64% |
| 50 | 249 | 0.31% | 76.91% | 39.25% |

Mean across all sampled chain states, after canonicalizing rotations and
reversal of tours. Native action-history distinguishes states even for
same tour; these statistics measure tour configurations, not full MDP
state coverage. Eight chains cover 201–357 unique tours at n20 and
977–1449 at n50. 11,200 native actions total. The policy learns to take
worsening moves after early descent; avoidance of most neighbors is
strong selectivity, not automatically a defect.

Follow-up group probe: ordinary 1/8 nonzero groups, 1/160 improving
rollouts; uniform unvisited neighbor 0/8, 0/160. All alternate resets
8.7–34.9% worse than the previously achieved best reference.
One unvisited move often moves away from reward; simply increasing
coverage does not guarantee signal. This is a measured negative result.
The checkpoint's objective is reference improvement, not global optimum.
Next question is whether a broader *native trajectory archive* can expose
productive high-quality states without selecting actions by quality or
providing a solution. Avoid assuming every underexplored state is helpful.
No model training or claims of global state-space coverage.
