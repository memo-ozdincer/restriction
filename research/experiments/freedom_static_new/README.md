# Non-sequential freedoms: fixed graph coloring

## Preregistered hypotheses, 2026-11-27 (before sampling)

A static candidate is an entire assignment of colors to 15 vertices, not a trajectory. A product-categorical stochastic policy produces all labels simultaneously and receives a binary terminal reward for satisfying every active edge constraint. All policy parameters start identically across paired arms; no planted solution, intermediate edge score, distance, or expert operation is supplied. Official evaluation always tests 3 colors and every original edge.

The graph is generated independently of policy training by assigning five vertices to each of three hidden classes then randomly connecting distinct classes (edge probability 0.65; seed 20261127); labels are shuffled. Exact backtracking counts 3-colorings and confirms non-2-colorability. The generator supplies a feasible witness but the learner never sees the class assignments. This is a fixed benign combinatorial optimization task, not a dataset or a general coloring solver.

Three distinct freedoms matter intrinsically:
- **Random constraint masking**: every candidate has an independently sampled set of enforced edges; keep probabilities .55/.75. No promising-edge selection. Binary training criterion becomes less strict. If the induced success landscape teaches broadly compatible assignments, then restoring all edges should enable additional exact solutions.
- **Fixed constraint masking**: randomly select a mask once, then apply equally throughout training. Same expected number of constraints as random mask; this tests whether state diversity rather than simply easier acceptance matters. Exact full reward remains evaluation target.
- **Color capacity**: temporarily allow four or five colors, then restore 3. This changes the candidate space, not graph dynamics. Full graph still checked; a successful 4/5-coloring may not compress and the transfer must be measured. All models have a five-column policy; active color count masks logits, no added parameterization.
- **Combined**: four colors plus .75 random edge mask, then restore both; tests whether freedoms can jointly unlock terminal signals.

Compare ordinary, assisted-only, assisted→ordinary, and a mask annealing variant. Total updates 500, batch 256 candidates, switch after step 150, 8 paired seeds (42..49), evaluate 1024 exact unassisted candidates at steps 0,50,...,500. Identical optimizer, lr .03, product policy and evaluation RNG. Same number of complete candidate proposals, but assisted edge masks and color capacity differ in actual constraint checks/entropy and are accounted for; evaluating fewer edges per proposal can reduce cost. Training queries use exact terminal predicates for the selected task, no dense progress reward. Non-sequential: no artificial 'start state' inserted. Compare phase-1 terminal accessibility and phase-2 ordinary performance; success during assistance is not success on the original task. These exploratory arms discriminate actual transfer from merely solving easier versions. A policy that solves this one fixed graph is not evidence of generalization to new graphs. The seed panel is intended to distinguish brittle breakthroughs from reproducible transfer, not publication-level significance.

Expected: random masks may teach compatible color coordination better than fixed subsets; capacity assistance may generate more successes yet transfer poorly. Ordinary may fail to discover any positive reward if target coloring basin is narrow. No outcome-conditioned schedule or hyperparameter selection will be performed.

## Follow-up registered after the initial results

Random 55% constraint masks produced six reliable exact-3-color policies, while switching at 150 gave only one. All root evaluations at step 150 were zero, and five of the six successful assisted-only policies first achieved substantial unassisted success after steps 250–450. Test two competing explanations: (1) switch too early; (2) relaxation magnitude insufficient in early phase. Fix same graph, seeds, total compute, optimizer. Compare switching at 300 and 400 with the original .55 keep probability; compare random .35 and .45 masks in continuous and 150-switch regimes. Include .35→1 linear anneal over first 300 updates. Compare unassisted results every 50 steps. This is a targeted response to the late-transfer observation, not extra replication for significance. No early stopping or selection within a run.

## Important audit and targeted control (registered before control sampling)

For a candidate violating m original edges and independent keep probability q, the expected binary relaxed reward is exactly (1-q)^m. Thus per-candidate random masking is mathematically equivalent in expected policy gradient to a dense monotone conflict-count reward, conditional on a particular candidate (the minibatch sample-mean baseline applies the same finite-batch scaling). It is genuinely random environment constraint selection and binary termination per episode, but it is **not equivalent to an unchanged verifier or an absence of implicit reward shaping**. This is a significant boundary relative to the research premise. The mask is never supplied as input; the same candidate can receive different reward draws. The expected reward intervention explicitly computes m and is a nonbinary comparator, not a claimed magic-preserving protocol. Test random-mask-per-batch (one shared random subset per group of 256) and deterministic expected reward, keeping the primary formulation and all budgets fixed. Compare .45 continuous and .35-switch at step 150, selected because those arms exhibited the strongest continuous and switched outcomes in the prior predeclared panel. Hypothesis: deterministic expected shaping may explain the random-mask result, while shared randomness changes gradient covariance and may alter transfer reliability despite the same marginal acceptance probability. Report this separately, with no cherry-picked seed comparison.

## Results

All runs trained with 128,000 whole-candidate proposals each; the full study contains 25 modes × 8 paired seeds. Every evaluation draws only 3 colors and tests all 49 edges. The graph has exactly six legal assignments (all global color permutations of a unique partition), no 2-coloring, and uniform exact-success probability 6/3^15 = 4.1815e-7. Empirical percentages below average over all eight policies and 1024 draws per final policy. 'Reliable' means ≥10% exact success at final checkpoint; this threshold is descriptive, not a statistical claim.

| Mode | Reliable / 8 | Mean final exact success |
|---|---:|---:|
| Ordinary | 1 | 12.3% |
| Fresh per-candidate mask, keep .75 | 2 | 24.8% |
| Fresh .75→full at 150 | 1 | 12.3% |
| Fresh .55 | 6 | 74.4% |
| Fresh .55→full at 150 | 1 | 12.5% |
| Fresh .55→full at 300 | 2 | 24.9% |
| Fresh .55→full at 400 | 5 | 62.1% |
| Fixed .55 mask | 1 | 5.3% |
| Fixed .55→full at 150 | 1 | 12.3% |
| Fresh .45 | 8 | 99.4% |
| Fresh .45→full at 150 | 3 | 37.3% |
| Fresh .35 | 7 | 86.7% |
| Fresh .35→full at 150 | 5 | 62.2% |
| .55→1 anneal over 150 | 1 | 12.3% |
| .35→1 anneal over 300 | 0 | 0.0% |
| Four colors (unassisted evaluation uses 3) | 2 | 7.4% |
| Four colors→3 at 150 | 0 | 0% |
| Five colors | 3 | 26.8% |
| Five colors→3 at 150 | 2 | 24.8% |
| Four colors + fresh .75 mask | 4 | 44.0% |
| Four colors + fresh .75→full at 150 | 2 | 24.9% |
| Deterministic expected reward .45 | 8 | 99.5% |
| Shared batch mask .45 | 8 | 99.2% |
| Deterministic expected reward .35→full at 150 | 8 | 99.6% |
| Shared batch mask .35→full at 150 | 8 | 99.4% |

Initial uniform candidate hit probabilities from exhaustive enumeration of all 14,348,907 assignments: full 4.1815e-7, .75 1.334e-6, .55 3.947e-5, .45 2.957e-4, .35 .0020974. The eight fixed .55 masks correspond to probabilities 2.51e-6 to 3.18e-5. They are generally harder than the marginal fresh-mask distribution, which also includes rare masks with few constraints. Thus fixed versus fresh does not cleanly isolate diversity at equal success probability.

The strongest gain was continuous fresh masking compared with ordinary; tested switch schedules generally degraded transfer relative to continued assistance, including the more favorable .35-switch result. This is a counterexample to assuming removal itself provides a gain. Early exact success remains zero on most masks but late breakthroughs can become nearly deterministic.

The deterministic expected-reward and shared-mask controls both solved all eight policies under the stronger selected conditions. This supports interpreting random constraint masking as implicit conflict-count shaping; binary reward per sample does not eliminate the dense objective in expectation. Shared masking can also change gradient covariance by correlating episode environments within a group. These results are not evidence that stochastic masking has capabilities beyond explicit shaping. No mask selection uses policy outcomes. Extra-color capacity is another actual degree of freedom but changes feasible outputs and may produce incompatible solutions; it was less useful here.

## Audit / reproduction

- Run python3 graph_coloring.py --out coloring_results.json, then --followup --out coloring_followup.json, then --controls --out coloring_controls.json from this directory.
- python3 -m unittest discover -s . validates calibration, scalar terminal predicate and switch boundaries (3 tests).
- python3 audit.py independently enumerates all 3^15 assignments, verifies every retained success certificate with a scalar checker, reproduces seed 42's complete successful .35-switch training record exactly, and evaluates 2048 fresh draws for every saved final policy with the scalar verifier. Fresh results preserve all major counts, including 8/8 shared batch and expected-reward switch, 5/8 independent-mask switch, 1/8 ordinary. Exact percentages and certificates in audit.json.
- Fixed policy parameter count 75, identical initial logits and Adam parameters, 500 updates, 256 full candidate proposals per update, same independent evaluation seed. Color mask changes active score coordinates (3,4,5); there is no model-parameter budget change. Training computes the full conflict vector before masking and independently computes full-check diagnostics; the constraint_checks counter in records measures logically enforced edges, not CPU operations. Every mode performs full vectorized graph comparisons and full-check diagnostics per proposal; execution costs differ slightly with masking RNG and active colors. No LLM, human guidance, privileged solver state, or expert labels in training.
- No new graph generalization was measured. The underlying task has a set of six equivalent exact accepted assignments, so a high final pass rate can be a concentrated distribution over a single assignment. This is a bounded fixed-instance search-and-learning result, not evidence of broad capabilities. No claim of algorithmic novelty.
