# Three independent TSP diagnostics

User asked for independent proposed and implemented experiments using Luna
or Terra. Each agent registered its hypothesis before sampling. 64 frozen
calls total, all resolved and verified by the individual agents. No training.

| Experiment | Luna | Terra | Conclusion |
|---|---|---|---|
| Plateau and blind kicks | 0/4 each | 4/4 plateau, 0/4 kick A, 4/4 kick B | Classical 2-opt stall is not necessarily a model stall; random kicks reduce access on this instance. |
| Commitment release | 1/4 root, 1/4 locked, 0/4 released | 4/4 every arm | Extra freedom doubled acceptable completions but expanded suffix space eightfold; reward density fell. |
| Reference quality | relative improvement 1/4 midpoint, 0/4 plateau; absolute optimum 0/4 both | midpoint 4/4 improvements of identical cost, 0/4 optimum; plateau 2/4 optimum | Useful reward variation depends on current policy competency. |

Details: [plateau](tsp_plateau/README.md), [commitment](tsp_commitment/README.md),
[signal](tsp_signal/README.md). All original source files and compact evidence
are tracked. Operational logs remain local as documented by each agent.

The reference-quality study also evaluates a cheap fixed stochastic policy
over 640 same-state groups per arm, 8 rollouts each. Midpoint vs plateau:
640 vs 380 nonzero centered relative-improvement groups; 118 vs 51 mixed
absolute-optimum groups; 157 vs 53 exact-optimum hits. Exact probability
propagation confirms mean success probabilities 2.755% vs 1.199%.
The frozen Terra comparison reverses the useful-state ranking. Earlier
states are not automatically better.

Adjudication: prioritize reference-quality diagnostic because it demonstrates
a concrete model-dependent reward-access bottleneck under unchanged final
objective. The other two provide valuable negative controls against claiming
that more state variation or freedom necessarily increases signal. No claim
of learned transfer or competitive TSP solver performance. The observed
differences are exploratory, one group per model/start in the frozen
signal study. Further training should be motivated by a concrete
mechanism and not by significance-only repetition.
