# TSP commitment-release frozen diagnostic

## Preregistered hypothesis (before instance construction or model runs)

Constructive neural TSP methods serially choose cities, leaving prior decisions fixed. A deterministic nearest-neighbor rollout serves here as a transparent, reproducible accepted *heuristic* trajectory, not a claim to reproduce learned SOTA. We will locate the regret bottleneck with an offline exact Held–Karp oracle: how much worse is the best completion after each committed prefix? The experiment tests whether exposing a model to the same greedy prefix with its most recent commitment released can increase terminal success and mixed-reward group frequency. This is a diagnostic of reward access, not evidence of learned transfer.

References: [Attention, Learn to Solve Routing Problems!](https://arxiv.org/abs/1803.08475) learns a constructive policy with REINFORCE and greedy rollout baseline; [Take a Step and Reconsider](https://arxiv.org/html/2407.17206v1) explores diverse suffix alternatives after committing partial solutions. Neither source demonstrates our particular frozen commitment-release comparison.

One 12-city integer-coordinate symmetric Euclidean TSP instance (distance rounded to nearest integer). Seed selection rule: from independent seeds 0..199, take the first where a deterministic nearest-neighbor prefix of length five (starting at city zero) has a feasible optimal completion within 3% of the global optimum but strictly greater minimum cost than the four-city prefix (last decision released). This ensures locked completion is mathematically possible and isolates a commitment with measurable regret. Freeze both the city set and threshold before querying any model. If no instance meets the rule, report construction failure. Oracle paths never shown to the model.

Arms: root (city zero locked), locked (first five cities fixed), released (same five-city prefix displayed, first four fixed, fifth can be reconsidered). All outputs full tours, same exact objective, same threshold, no tools, same low reasoning effort, one-shot frozen calls. Four rollouts from the same prompt per model per arm constitute one group, allowing us to measure all-success, all-failure or mixed rewards. The released arm expands reachable tours; it does not hold the set of allowable trajectories fixed. All conditions share the same terminal TSP constraint (a complete permutation, returning to zero) and length objective; a separate check enforces the permitted prefix during the auxiliary rollout. Root is unassisted evaluation. A model success after release is not by itself evidence of learned capability, and selecting a useful release using exact oracle information may be too expensive for large tasks. Candidate follow-up: sample releases independently of their regret and test subsequent ordinary learning.

## Result

Frozen instance selected by the registered rule: seed 12, exact optimum 330, threshold 339. The nearest-neighbor route costs 430. The minimum reachable completion costs after its first 1..12 cities are `[330,330,330,330,339,346,353,404,404,404,430,430]`. The fifth city is the first strictly regretful commitment. Strict five-city prefix has precisely 1 acceptable completion among 5,040; releasing only the fifth expands the count to 2 among 40,320. Thus the additional freedom doubles absolute acceptable completions but quarters their probability under uniform suffix sampling. This is an exact distinction between access and density.

24 independent frozen responses (4 per model/arm), all valid permutations honoring the applicable prefix constraints; no tools/CLI errors. gpt-6-luna and gpt-6.1-terra, low effort. All groups were replayed against the exact checker, including prompt hash matching. Results:

| Model | Root | Five committed | Fifth released |
|---|---|---|---|
| Luna threshold successes | 1/4 | 1/4 | 0/4 |
| Luna lengths | 346,397,397,330 | 397,404,339,367 | 404,405,351,402 |
| Terra threshold successes | 4/4 | 4/4 | 4/4 |
| Terra lengths | 330,330,330,339 | 339,339,339,339 | 330,339,339,330 |

- Binary reward group variation: Luna root and locked are mixed, released unanimous failure. Terra all three unanimous success. The proposed release therefore did **not** increase access to informative binary groups.
- Continuous terminal length reward: Terra's locked prefix yields identical exact constrained-optimum tours; release restores cost variance and 2/4 globally optimal tours. Root also already has cost variance, and its mean length is better (332.25 vs released 334.5). This recovers diversity lost under commitment but does not establish greater access than the ordinary root distribution.
- The released Terra completions that improve length both explicitly reorder the fifth greedy decision. Luna's best release revises it as well but does not meet threshold.
- All four unit tests pass; test command `python3 -m unittest discover -s research/experiments/tsp_commitment`. Regeneration `python3 research/experiments/tsp_commitment/environment.py`; run `python3 research/experiments/tsp_commitment/screen.py --out /tmp/new-tsp-commitment`. Compact evidence `results.json`, full prompts/answers/events local at `/tmp/tsp-commitment-20261127`. The verified model outputs are in the compact artifact, and prompt text can be reconstructed from the checked-in case and code.
- Reasoning-token totals vary across arms despite equal call count and configured effort (Luna root 2340, locked 606, released 1645; Terra root 3025, locked 518, released 1160). No equal realized token-budget claim. No learning or transfer measured.

Interpretation: this particular degree of freedom is a negative binary-reward experiment. A more constrained start can increase reward concentration, while a released commitment can enlarge the branching problem enough to decrease success density. The actual training question would need a harder instance, root groups with low but nonzero success or an auxiliary group with usable signal, and a compute-matched learning/removal comparison. No reason to scale this same instance solely for significance. A trajectory-based improvement would use a constructive neural policy's observed commitments instead of nearest-neighbor proxy, and test releases chosen independently of oracle-optimality.
