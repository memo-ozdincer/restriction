# Creative RLVR: open discovery and strict experimental selection

## User steering (verbatim)

> Okay put it to some note doc, and also just reference where everything we tried, everything that seems to already be really good at rlvr, everything that seems to be able to learn from rlvr, etc. etc. etc.
>
> Another very important requirement is: in discovery phase, these requirements don't matter. Because we want to be open minded. add that. in discovery, just an environment that would allow for creative solutions, or perhaps an environment that has been studied, and has very interesting solutoins established using very expressive rl models, or more advanced/analytical models that we can try to emulate using our smaller or rl models, or problems without solutions, etc. etc.
> P=NP is an interesting space, circuit design is, math is, coding is very interesting, kernel optimization has a lot of work around it, assembly, games are good, but yeah like papers of that kind aren't bad sources either. So add those points as well, and then send em off exploratorily

## Two phases — do not conflate them

**Phase A: discovery.** No strict gates apply. Look broadly for environments
with creative potential, surprising existing solutions, analytical or
strong-model discoveries that might be reproduced by small RL learners,
unsolved problems, positive and negative RL results, unusual trajectories,
scaling behavior, or new questions. An environment need not have an existing
RL baseline, proven headroom, known missing skill, open training data or
cheap experiment to be interesting enough to record. Papers, benchmarks,
algorithms, formal specifications, and games are equally legitimate leads.
Do not rank solely by NP-hardness, and do not claim progress on P vs NP
from empirical instance-solving improvements. Investigate benign abstract
combinatorial problems (SAT, TSP, graph optimization, etc.), circuits,
formal math, executable algorithm synthesis, numerical kernels, arithmetic/
sorting assembly, and games. Do not force leads into the taxonomy; add
new phenomena when warranted. Do not propose interventions yet.

**Phase B: selection before committing substantial training compute.**
Use the rigorous screening rubric below. Missing evidence is unknown,
not proof of disqualification; cheap diagnostic work can resolve it.
Baseline reproduction is necessary before making a comparative claim,
not a prerequisite to recording an interesting lead.

## Research questions and taxonomy (open, not dogma)

See [earlier taxonomy and verbatim discussion](RLVR_BOTTLENECK_TAXONOMY_2026-11-27.md).
Three strands, not necessarily exhaustive:

1. Resource-limited discovery: ordinary RL makes progress but capability
   is prohibitively costly at current model capacity, rollout width/depth,
   optimization budget, or combinations thereof.
2. Valuable behaviors ordinary RL practically never discovers: local minima,
   long valleys of failure, extremely distant solution regions, absence of
   a generic useful exploration heuristic, narrow coordinated successes,
   dominant habits, no reason to learn yet, novel objects/representations,
   unexpected composition, abandoning an established approach. These can
   coexist (ultra-shortcut analogy) and are hypotheses, not general
   impossibility theorems. Astronomical search times should not be conflated
   with routine scaling.
3. Unexploited experience: valuable computations occur in successful or
   failed trajectories but are not acquired, retained, or generalized.

The goal is to observe what ordinary RLVR does and does not discover,
not define good mathematical taste or prescribe a preferred solution.

## Strict selection rubric (from three agent critiques, refined)

Universal requirements for a decisive experimental comparison:

- Objective native verification of success and, where applicable, quality.
- Creative freedom: materially different solutions, not merely permutations
  or renamed versions of the same solution.
- Minimal prescription of the desired reasoning/computational strategy.
- Meaningful witnessed headroom (a checked better solution or bound);
  exact optimum is unnecessary. A genuinely unsolved task can remain a
  discovery lead without meeting this gate.
- Observable learning: trajectories, checkpoints, meaningful diagnostics.
- Reproducible ordinary baseline, ideally established published work.
- Pilot tractability and honest accounting of primitive compute, verifier
  queries, sampling/reset overhead, and evaluation budget.
- Native, unassisted evaluation; independent held-out tasks when claiming
  transferable capability.

Creative potential: new objects and representations, unexpectedly useful
compositions, counterintuitive decisions, qualitatively distinct solutions,
reusable discoveries, large improvements over conventional solutions,
and possibility of surprising the experimenter.

Signals to investigate (not mandatory all together): scaling cliffs;
large gaps to feasible solutions; failure valleys; seed divergence; rare
successful trajectories; transient skills subsequently lost; systematic
held-out failures; oracle or additional-freedom performance gaps; radically
different human/algorithmic solutions; unexplained plateaus.

| Criterion | Resource-limited | Practically undiscovered | Unexploited experience |
|---|---|---|---|
| Ordinary success required | No | No | Observable relevant behavior, not necessarily full success |
| Known missing strategy required | No | No | Some relevant behavior observable, not preselected |
| Trajectory access | Valuable | Very important | Essential |
| Scaling diagnostics | Important | Valuable | Secondary |
| Held-out probes | Valuable | Very valuable | Essential for transfer claims |

Disqualify a *proposed comparison*, not its entire domain, if baseline is
effectively optimal; nominal search size is the sole interest; diversity
is cosmetic; desired behavior is impossible under the interface; human
labels prescribe the intended strategy; improvement cannot be measured;
only aggregate scores are accessible for a mechanistic claim; or evaluation
leaks assistance or extra inference budget. Do not interpret zero ordinary
success as automatically disqualifying. Do not infer intrinsic impossibility
from finite zero counts or a low coverage estimate.

For each lead report what is known, why it is creative, established
approaches and interesting solutions, evidence of learning/failure or
headroom, data/code availability when known, tractable open questions,
and uncertainty. In phase A, none of those fields is required to be
resolved. Separate published evidence from inference.

## Research-history map

This is an index, not a claim that all referenced experiments are LLM RLVR
or have established generalization. Many are small REINFORCE policies,
evolutionary experiments, frozen LLM inference, or verifier-based search.

| Thread | Evidence and links |
|---|---|
| Original mathematical intervention | [Results](RESULTS.md), [proof characteristics](C2_C3_PROOF_CHARACTERISTICS.md), [capability retention](CAPABILITY_RETENTION.md), [near misses](NEAR_MISS_TRACKING_2026-11-25.md), [selective sharpening](RRL_SELECTIVE_SHARPENING_2026-11-26.md). |
| Mathematical invariants, interfaces and witness bottlenecks | [Interface discovery](INTERFACE_DISCOVERY_RESULT_2026-11-19.md), [deduction/witness construction](DEDUCTION_WITNESS_CONSTRUCTION_2026-11-25.md), [repaired library](REPAIRED_LIBRARY_RESULT_2026-11-19.md), [failed proof knowledge](FAILED_PROOF_KNOWLEDGE_2026-11-25.md). Checked facts can unlock execution, but irrelevant/bare controls and failed consumption caution against generic assistance. |
| Hindsight, HELP, collaboration and feedback | [Intrinsic hindsight proposal](INTRINSIC_HINDSIGHT_PROPOSAL_2026-11-25.md), [Lean delegation](LEAN_DELEGATION_AND_DISCOVERY_SYNTHESIS_2026-11-26.md), [simple Lean pilots](SIMPLE_LEAN_RLVR_PILOTS_2026-11-26.md), [iterative critiques](ITERATIVE_RLVR_EXPERIMENT_CRITIQUES_2026-11-26.md). Frozen-model assistance is not learning evidence. |
| Pinball and physical crutches | [State exposure notes, physical results, verbatim idea-dumps](STATE_EXPOSURE_RLVR_2026-11-26.md), [coding charter](CODING_STATE_EXPOSURE_2026-11-26.md). User-reported evolutionary pinball 82.3% random-first then regular vs 49.4% ordinary vs 10.1% random-only. Earlier exposure 92/2048 vs 42/2048 root wins; physical project separate. |
| AIG Boolean circuits | [Initial benchmark and frozen Luna/Terra screen](experiments/aig_initial/README.md). Distinguish observed language competence from trainability. |
| Reversible synthesis | [Frozen and initial learning](experiments/reversible_initial/README.md), [small learning](experiments/reversible_learning/README.md), [hard bottleneck](experiments/hard_reversible_bottleneck/README.md). Five-wire target: ordinary 0/1.536M training, switch 2044/2048 root tests; rare generalized targets failed despite abundant auxiliary successes. |
| TSP | [Adjudication](experiments/TSP_INITIAL_ADJUDICATION_2026-11-27.md), [plateau](experiments/tsp_plateau/README.md), [commitment](experiments/tsp_commitment/README.md), [frozen signal](experiments/tsp_signal/README.md). Low neighborhood coverage alone did not establish valuable missed strategies. |
| Sokoban, Flip, matrix/tensor, reversible, TSP CPU panel | [Completed 220-run panel](experiments/exposure_cpu_launch/README.md), [tensor and Sokoban implementation](experiments/exposure_tensor_sokoban/README.md). Hard Sokoban solvable resets 994/1024 vs ordinary 0 and switch 91/1024; unrestricted legal resets failed. Ordinary medium Sokoban and Flip near ceiling; TSP no clear mean gain; larger matrix pilot inconclusive; reversible panel unsolved. |
| Post-competence exposure and generalization | [Alchemy synthesis](ALCHEMY_DISCOVERY_2026-11-27.md), [compression](experiments/alchemy_compression/README.md), [XOR](experiments/alchemy_xor/README.md), [tensor](experiments/alchemy_tensor/README.md), [racetrack](experiments/alchemy_racetrack/README.md). Ordinary RL discovered neutral circuit restructuring independently; small XOR and tensor close to optimum; racetrack held-out 93.75% vs ordinary 75%, one ordinary seed transiently learned then lost maneuver. |
| Broader combinatorial work | [Combinatorial exposure](COMBINATORIAL_EXPOSURE_2026-11-27.md), [reset geometry](RESET_GEOMETRY_AND_FREEDOMS_2026-11-27.md), [environment freedoms](ENVIRONMENT_FREEDOM_EXPERIMENTS_2026-11-27.md), [reward bootstrap](REWARD_BOOTSTRAP_BOTTLENECKS_2026-11-27.md), [task-family audit](TASK_FAMILY_AUDIT_2026-11-27.md). |
| Prior art and general direction | [Environment-wide RLVR prior art](ENVIRONMENT_WIDE_RLVR_PRIOR_ART_2026-11-26.md), [state-exposure prior-art checks](STATE_EXPOSURE_RLVR_2026-11-26.md), [frontier RL sources](FRONTIER_RL_SOURCES_2026-10-26.md), [Supervision Through a Straw](SUPERVISION_THROUGH_A_STRAW_APRIL_2026-11-25.md). PrefixRL, reverse curricula, failed-trace resets and other approaches overlap substantially; no novelty claims based on absence from search. |
| Complete project history | [Project state](../PROJECT_STATE.md), [handoff](../CONTINUE_ELSEWHERE.md), [decision ledger](DECISIONS.md), [experiment directory](experiments/). |

## Positive evidence to learn from, not automatic restrictions

Ordinary RL already learns neutral circuit transformations, small XOR
synthesis and tensor compression near optimum, medium Sokoban, Flip,
some racetrack maneuvers, and many Lean proof modes. These are examples
of capabilities already accessible without our interventions. Positive
learning under modified starts includes hard Sokoban and five-wire CNOT;
pinball provides user-reported delayed specialization; held-out racetrack
provides evidence of transferable maneuver acquisition. Negative results
are equally valuable: abundant auxiliary reward can worsen root success,
and broader exposure need not beat ordinary RL after competence.

External starting points already indexed in the coding charter:
AlphaTensor, AlphaDev, ABC/EPFL, CompilerGym, KernelBench, VerilogEval/
RTLLM, PrefixRL and Go-style/game learning. These are leads, not a
statement that their strongest methods are ordinary RLVR or that all
are equally suitable for small-model experiments.

## Discovery assignments

Three independent exploratory searches: mathematics and abstract
combinatorial optimization; computational algorithms/circuits/numerical
kernels/benign assembly; creative games and puzzles. No strict screening
in this phase, no training or mechanism selection. Seek primary sources,
positive results as well as failures, and underrated or unexpected
capabilities rather than simply harder tasks.

## Initial exploratory literature sweep (three agents)

These are discovery leads from primary-source searches, not screened
recommendations, novelty claims, or independently reproduced experiments.
Reported numbers are authors' results; conditions differ considerably.

### Mathematics and combinatorial optimization

- [Andrews–Curtis: What makes math problems hard for RL](https://arxiv.org/html/2408.15332v2):
  exact primitive string/group rewriting; very similar inputs with
  drastically different difficulty; PPO solved two hard presentations
  that initial classical search did not. Learned supermoves can help or
  harm depending on selection. [Solver](https://github.com/shehper/AC-Solver).
  [The Two-Hump Problem, ICML 2026](https://proceedings.mlr.press/v306/fagan26a.html)
  explicitly studies a gap between trivial and effectively unreachable
  instances; [ACSolverX data/code](https://github.com/Math-AI-Caltech/ACSolverX)
  offers large certified datasets and a stronger curriculum baseline.
  Related [SAIR benchmark](https://github.com/SAIRcompetition/Andrews-Curtis).
- [Graph conjectures and deep cross-entropy](https://arxiv.org/abs/2104.14516):
  small learned graph constructors refuted published conjectures.
  [Follow-up study](https://arxiv.org/abs/2403.18429) reports 25 of 68
  spectral-bound conjectures refuted by RL, five additional via exhaustive
  search suggested by structures found by RL, 38 unresolved (not
  necessarily false). [Open graph environments](https://github.com/CuriosAI/graph_conjectures).
- [New Ramsey Multiplicity Bounds and Search Heuristics](https://link.springer.com/article/10.1007/s10208-024-09675-6):
  reports classical tabu/annealing dramatically faster than the tested
  neural cross-entropy approach, including a target CE never reached in
  reasonable time. Authors describe timing comparison as anecdotal;
  Cayley representations dramatically reduce search variables.
  [Related AlphaZero/tabu graph generation](https://www.ijcai.org/proceedings/2024/772).
- [Hard unknot diagrams](https://arxiv.org/abs/2409.09032):
  substantial class provably requires increasing crossings before
  simplification. [Later RL solver](https://arxiv.org/html/2603.07955v1)
  reports >95% on very-hard data using shaping, macros and heuristics;
  validate train/test split and compare primitive-only methods.
- [AlphaEvolve mathematical exploration](https://arxiv.org/abs/2511.02864):
  survey of 67 math problems, including finite-field Kakeya, Turan,
  polynomial constructions, autocorrelation and difference bases;
  successful and unresolved cases provide sources of creative tasks.
- [FunSearch](https://www.nature.com/articles/s41586-023-06924-6):
  cap-set construction and transferable online bin-packing strategies,
  using LLM-driven evolutionary program search rather than ordinary RLVR.

### Computational and mathematical algorithm discovery

- [AlphaTensor](https://www.nature.com/articles/s41586-022-05172-4):
  >14,000 inequivalent 4x4 standard-arithmetic factorizations reported;
  strong positive example of creative solution diversity. Synthetic
  games and symmetries already used for training.
- [Flip graph](https://arxiv.org/abs/2212.01175),
  [symmetry-aware variant](https://arxiv.org/abs/2502.04514),
  [later matrix schemes](https://arxiv.org/abs/2505.05896): random-walk/
  analytical search methods report rank-93 5x5 and rank-153 6x6 schemes;
  check fields and task constraints before comparison.
- [AlphaEvolve](https://arxiv.org/html/2506.13131v1): search-algorithm
  evolution improves published matrix multiplication bounds, including
  4x4 complex rank 49 to 48; compare only like arithmetic settings.
- [ShortCircuit](https://arxiv.org/abs/2408.09858): SFT and RL, authors
  report 98% held-out eight-input truth tables synthesized and
  18.62% gate-count reduction versus ABC. Revisit given our small AIG pilots.
- [AlphaDev](https://www.nature.com/articles/s41586-023-06004-9)
  and [code](https://github.com/google-deepmind/alphadev): assembly sorting
  instruction sequences outperforming prior implementations.
- [Strong Generalization and Efficiency in Neural Programs](https://arxiv.org/abs/2007.03629):
  imitation then RL, sorting generalization beyond training lengths,
  binary search and knapsack; benchmark-specific efficiency claims.
- [Symbolic Equation Solving via RL](https://arxiv.org/abs/2401.13447):
  exact symbolic stack calculus, interpretable equation transformations.
- [Ansor](https://www.usenix.org/conference/osdi20/presentation/zheng):
  identifies restricted templates and incomplete-program pruning as
  excluding valuable numerical kernel optimizations. Hierarchical search,
  not an ordinary RL baseline.
- [Mirage](https://www.usenix.org/conference/osdi25/presentation/wu-mengdi):
  multilevel algebraic and scheduling representations for numerical
  kernel synthesis; probabilistic equivalence verification.
- [Sorting-network optimal-depth bounds](https://arxiv.org/abs/1507.01428):
  objective universal correctness and size/depth tradeoffs. Verify current
  open frontiers before deciding on any task.

### Games, puzzles and emergent algorithms

- [PushWorld](https://arxiv.org/abs/2301.10289),
  [code and reference solutions](https://github.com/google-deepmind/pushworld):
  simple grid physics, movable obstacles and tool use. Table 2 reports
  PPO training/held-out base 88.5/40.4%, more walls 77.9/23.3%,
  more obstacles 64.7/21.4%; harder level 1 only 6% after 350M steps,
  DQN <1%. Interesting creativity, scaling and generalization lead.
- [PuzzleJAX](https://arxiv.org/abs/2508.16821): accelerated PuzzleScript
  engine for many games; compare search, RL and LLMs.
- [PUZZLES](https://proceedings.neurips.cc/paper_files/paper/2024/hash/e5d1eaadeed651ba1021c09149db4b92-Abstract-Datasets_and_Benchmarks_Track.html)
  and [code](https://github.com/ETH-DISCO/rlp): forty scalable logic puzzles;
  Netslide 2x3 PPO/DreamerV3 100%, 3x3 9.2/22.4%; Same Game 2x3
  100%, 5x5 ~30%. Direct scaling-cliff leads.
- [DeepMind Alchemy](https://arxiv.org/abs/2102.02926):
  procedural hidden causal chemistry. Symbolic VMPO 155.4 vs ideal
  observer 284.4 and random heuristic 145.7 after 20B steps; paper
  diagnoses that actions reveal latent chemistry, but learned agent
  fails to exploit information. Episode logs and explicit belief-state
  interventions permit analysis; assistance is not an autonomous solve.
- [Baba Is AI](https://arxiv.org/abs/2407.13729): rules themselves are
  movable objects, frozen LLMs struggle to compose individually
  demonstrated rules.
- [Interpreting Emergent Planning in Model-Free RL](https://arxiv.org/abs/2504.01871),
  [checkpoints](https://huggingface.co/AlignmentResearch/learned-planner):
  generic Sokoban DRC exhibits planning resembling parallel bidirectional
  search; causal analyses support use. Positive ordinary-RL anchor.
- [DeepCubeA](https://www.nature.com/articles/s42256-019-0070-z):
  all tested cube instances solved, 60.3% shortest; goal-reverse training,
  value iteration and search, also applied to sliding puzzles/Sokoban.
  Close precedent for solvable-state approach, not ordinary RLVR.

No experiments launched. Strong early leads for deeper discovery reading
(not selection decisions): Andrews–Curtis, graph conjectures/Ramsey,
PushWorld, Alchemy, AlphaTensor/flip graph, and symbolic equation solving.
