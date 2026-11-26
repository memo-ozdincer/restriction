# TSP plateau exposure diagnostic

## Registered hypothesis (before frozen sampling)

Best-improvement 2-opt descent can stall at strict local minima although a short legal sequence that temporarily worsens the tour improves the final objective. Exposing a policy to target-independent, randomly perturbed states around that observed stall may produce more terminal successes or reward variation than repeatedly sampling at the stalled state. This is a frozen diagnostic, not training or a retained-capability result.

Motivation: [Learning 2-opt Heuristics for the TSP via Deep Reinforcement Learning](https://arxiv.org/abs/2004.01608) trains improvement policies with random starting tours and exhibits rapid early progress followed by refinement; random starts themselves are established. [NICO-TSP](https://arxiv.org/html/2604.06940v1) reports zero-variance groups when warmup states are too strong; the present test focuses on whether a single, unguided perturbation of an actually observed local optimum changes terminal reward access. This is closely related to classical iterated local search, not a claim of a novel solver.

## Design

Generate one fixed 11-city rounded Euclidean instance from seed 20261127. Take the first strict suboptimal 2-opt local minimum found by deterministic best-improvement descent with a two-step improvement. Independently compute exact optimum by Held-Karp DP; no reference tour or successful moves provided to models. Target length is at most plateau cost minus one. Anchor city zero, legal actions reverse positions i..j inclusive, i>=1 and j<n, excluding reversal of the entire nonzero suffix. All conditions give identical 3-action horizon, same terminal binary criterion and observation/action format. The alternative starts are two distinct uniform random one-step 2-opt kicks sampled with seed 42, without looking at length or access to success. Reset computation is tracked separately as one legal move; policy decision budgets are matched but physical move budgets differ by one. This isolates training-state access, not a fair solver-compute improvement claim. Each state gets four independent low-effort frozen completions per model (Luna and Terra), with no tool use and no feedback. Report separate per-state groups, not pooled state variance. Exact counts of sequences hitting threshold under <=3 moves are computed offline as feasibility audit, not provided to the model.

Expected positive evidence: a mixed-reward group at perturbed states despite all failures at the plateau; negative evidence: no improvement or only trivial easy-state wins. Comparison of start quality, exact sequence counts and validity prevents conflating mere easier starts with broader exploration. A later learning test would require ordinary, perturbation-only, switch, and standard iterated-local-search controls with total compute matched.

## Results (24 frozen calls, all legal, independently replayed)

The first qualifying geometric instance arose at source index 0. Best-improvement descent began at length 616 and reached the strict local minimum 341; the Held–Karp optimum is 334. Every one of the 44 legal 2-opt moves from the plateau increases length. The terminal threshold is 340. There are exactly 2 successful ordered two-action sequences and 19 successful ordered three-action sequences from the plateau. Both blind reset states require at least three continuation moves to pass.

| Same-state group | Initial length | Luna success | Terra success | Terra final lengths |
|---|---:|---:|---:|---|
| Plateau | 341 | 0/4 | 4/4 | 334, 334, 334, 334 |
| Kick 0 | 372 | 0/4 | 0/4 | 341, 343, 365, 343 |
| Kick 1 | 475 | 0/4 | 4/4 | 334, 334, 334, 334 |

All six same-state groups had uniform binary reward. All four Terra wins at kick 1 first undid the reset and then solved from the original plateau, using three actions. Terra solved from the plateau despite the monotone descent bottleneck, including the genuinely nonmonotonic trajectory 341→350→343→334. Luna never won, although several perturbation trials identified and undid the kick. The intervention produced no additional positive or mixed-group signal.

An exhaustive offline audit of all 44 one-step reset choices shows 13 successful exact-three-action sequences on average versus 19 at the original plateau. Only two resets (4.5%) exceed the ordinary count, with 112 and 120 successful sequences. These are actual escape moves, and intentionally selecting them would feed optimizer-derived information. The blind seed-42 resets produced counts of 10 and 6. This is a concrete reason random exposure can fail despite a genuine local-search bottleneck. A monotone heuristic's stall is not necessarily a frozen model's stall, and random perturbations may spend scarce continuation actions revisiting the previous state.

Next discriminating hypothesis: investigate the actual bottleneck of a policy that exhibits mixed success before selecting alternative start states; map reward-access variation around observed failed trajectories. Do not infer that merely practicing from an arbitrarily changed state is useful. The abrupt switch remains untested.

## Reproduction

Run `python3 -m unittest discover -s research/experiments/tsp_plateau`. All four tests passed. `screen.py` uses isolated read-only Codex CLI processes. `instance.json` records the frozen matrix, witness-free prompt inputs, descent path and exact access counts. `audit_neighborhood.py` regenerates the all-44-reset audit. `archive.py` assembles and independently replays compact `results.json`, including exact prompts, raw parsed actions, usage and prompt/answer hashes. Full operational event logs remain in the six /tmp/tsp-plateau-{model}-{state}-20261127 directories. No checkpoints or external data were used.
