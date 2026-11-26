# Broad environmental-freedom experiments

User steering, verbatim:

> try as many combinations and as many formulations as possible. generally, you want them to also be audited against our requirements at every step. Explore. Experiments. Probably non-LLM trials for now.
>
> If the environment is non-sequential for example, we change the random-start method with something that actually changes the degrees of freedom accordingly for that problem in a way that actually matters
>
> get subagents to run experiments

Three independent agents ran reversible, sorting and graph-coloring panels.
Main agent ran a static subset-sum panel. In total 824 training runs
(296+280+200+48) across 103 formulations using eight paired seeds per
formulation, plus independent reproduction and replay audits. The panels
are exploratory: follow-up arms were motivated by observed discrepancies,
reusing the seed panel, so the best configurations are selected results.
All use small non-LLM stochastic policies, a single fixed task per family,
no supplied solution paths or human-labeled process supervision, and final
evaluation on the original full objective.

## Most important findings

### Sorting: near the original start is better than near an easy finish

One fixed six-wire sorting network with an irregular eight-link
interconnect, exact optimum 12. All 64 binary input rows checked.
Uniformly sample a length from 1..r, execute random legal comparators,
and expose only the resulting row-set state to the policy. No path.
Switches at 30% of training. Each cell 4,096 fresh root evaluations.

| Maximum reset walk | Continued exposure | Switched to ordinary |
|---:|---:|---:|
| 2 | 0% | 0% |
| 4 | 35.08% | 10.16% |
| 6 | 38.45% | 63.70% |
| 8 | 8.35% | 22.34% |
| 12 | 2.61% | 10.77% |
| 24 | 0% | 0% |
| 36 | 0% | 0% |
| Uniform reachable state | 0% | 0% |

Ordinary training 0/4096. Radius6 switch 6/8 seeds crossed 10%,
90 distinct optimal circuits verified. Long/wide resets generate far
more initial reward but no root competence. Mixing short and very long
resets weakens results. Horizon 24/48, generic macro actions and cross
combinations have weak or zero results. The radius-six result uses
+8.7% simulation transitions for resets compared with ordinary; primitive
policy slots and optimizer updates match, total transitions do not.
Root-near resets still improve initial random success probability, so
this is not an equal-difficulty demonstration.

### Reversible circuits: goal exposure then specialization

Fixed exact-eight-gate three-wire task. Same 12 primitive gates,
300 updates and 1,024 policy action slots per update. All legal reset
walks independent of solution paths. Already terminal resets excluded.

| Reset distribution | Continued | Switch at 30% | Switch at 60% | Switch at 90% |
|---|---:|---:|---:|---:|
| Goal walk 1..4 | 0.61% | 0.52% | 67.08% | 4.51% |
| Balanced exact-distance shells | 1.59% | 12.58% | 63.71% | 35.06% |

Exact finite-horizon root probabilities, mean across eight seeds.
Ordinary approximately 0.001%; equal-distance, root walks and uniform
no meaningful root improvement. Balanced shells require shortest-distance
oracle for reset selection, unlike native random goal walks.
50/50 root/goal walk mixture switched at 30%: 25.27%. A 5%-goal,
95%-uniform mixture switched: 13.84%; 20%-goal mixture much weaker.
Horizon slack yields occasional wins, not strong consistent transfer.

A distance ladder emerges without an adaptive reset schedule: continued
near-goal training achieves 35.82%,14.54%,4.59%,0.76% on distance shells
5,6,7,8 even though resets are at most four moves from the goal.
Training rollouts may visit these states, so only their reset status
is unseen. After switching, root probability rises as broad-shell
competence declines. Exposure and specialization are distinct effects.
48 exact training record/weight replays; 32 high-success final
policies independently sampled and 10,149 optimal wins verified.

### Graph coloring: nonsequential constraint freedom, with a crucial audit

One fixed 15-vertex graph, whole coloring proposed in one sample.
Exact six valid three-color assignments. Ordinary 1/8 policies cross
10% exact success (mean 12.3%). Random enforcement of 45% of edges
throughout training: 8/8 (99.4%); 35% then restore all edges at 30%:
5/8 (62.2%). Continuing 55% masks: 6/8 (74.4%); switch at 80% 5/8
(62.1%), switch at 30% 1/8. Extra colors and combined masks less
effective. Annealing weak.

Important: if m constraints are violated and each is retained with
probability q, acceptance probability is (1-q)^m. Thus random masks
produce implicit dense conflict-count shaping in expectation despite
binary realized rewards. A deterministic expected-reward control
and shared-mask-per-batch control each produced 8/8 successes after
restoring at 30%, at ~99.6% and ~99.4% mean exact success.
This is an example of a freedom that genuinely matters for one-shot
tasks, but not evidence for unchanged-verifier magic or superiority
over explicit reward shaping. Random vs fixed masks also differ in
initial reward availability. All certificates and fresh eval samples
independently checked.

### Subset sum: one-shot numerical tolerance

One fixed 20-item instance, exactly one accepted subset certified by
meet-in-middle. Whole bit vector generated simultaneously. Exact-only,
constant tolerance, switched tolerance, annealed tolerance, random
bit checks, expanded bit checks, each with eight seeds.
47/48 final policies zero exact hits in 2,048 samples.
One annealed-tolerance run (seed 49) reached 398/2048 exact successes,
after only two relaxed rewards and first exact hit at step 480,
far after full restoration at step 180. Exact final probability 19.92%;
fresh independent replay 408/2048. Rare, not reliable. Exact reward
for the original task was not unchanged in early training.
Random-bit checks likewise implement expected Hamming-distance shaping;
neither is a clean neutral state-exposure intervention.

## Requirement audit

| Intervention | Native state or output freedom | Unchanged target verifier during training | No reference solution | Strongest evidence |
|---|---|---|---|---|
| Random start walks | Yes | Yes, same action cap | Yes | Sorting 63.7%, reversible 67.1% |
| Exact-distance shell | Yes | Yes | No action labels, but oracle selection | Pure equal-distance null; balanced shells strong |
| Fixed mixture of reset sources | Yes | Yes | Yes for legal walks/uniform | Reversible mixed gain, sorting mixed weaker |
| Longer horizon | Resource relaxation | Goal equality unchanged, budget altered | Yes | Weak/sometimes useful |
| Generic macro granularity | Primitive composition | Yes if cost charged | Yes | Weak in sorting; fewer policy calls |
| Extra colors | Candidate-space expansion | Original 3-color constraint altered | Yes | Modest and incompatible solutions possible |
| Random constraint masking | Terminal constraint subset | No; implicit shaping | Yes | Strong static results, shaping control matches |
| Numerical tolerance/bit mask | Terminal constraint relaxation | No; implicit shaping | Yes | Rare numerical breakthrough |

Each implementation records explicit budget, state/goal semantics,
reset sampling, evaluation conditions and audit boundaries. A fixed
single-task policy may memorize a solution; no generalization to new
targets demonstrated. Exact distance controls are not scalable
proof of unsupervised sampling. No LLM learning claim. Discovery
panel results cannot establish a statistically robust best schedule.

## Reproduction and artifacts

- [Reversible full panel](experiments/freedom_reversible_new/README.md)
- [Sorting full panel](experiments/freedom_sorting_new/README.md)
- [Graph-coloring full panel](experiments/freedom_static_new/README.md)
- [Subset-sum full panel](experiments/freedom_subset_new/README.md)
- [Reset comparison figure](experiments/freedom_summary/reset_comparison.png)

The strongest next research question is why start-centered intermediate
perturbations preserve useful experience in sorting whereas reversible
synthesis needs near-goal positive reward. Compare matched reward-access
distributions and independent fixed targets with the selected schedules,
rather than merely increasing replication on the chosen examples.
