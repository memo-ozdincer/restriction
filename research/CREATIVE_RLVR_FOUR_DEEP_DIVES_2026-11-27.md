# Four deep literature investigations: creative learning beyond benchmarks

## User steering (verbatim)

> I LOVE these examples. Lets send agents to investigate these four, papers around them (the latest ones, and perhaps their followups, although I think papers and their proposed followsups are HARDLY ever good alpha), don't get TOO tethered by the number of RL improvements we've tried in the past, or even the categories we try to put "areas for improvement in". Although slightly more trivial too, I'm also okay with partially looking for "they needed an extremely expressive model or physics-informed/math-informed/analytical to find this, we can do it in a smaller one" or something like that too, but obviously our bigger task is what we talked about before

Discovery phase: no strict selection criteria, no predetermined intervention.
Three independent agents investigated AC, graph theory and Alchemy; root
investigated Sokoban/planning. Sources are primary papers/repos, reported
results not independently replicated. See [discovery rubric and history](CREATIVE_RLVR_DISCOVERY_2026-11-27.md).
No experiments launched.

## 1. Andrews–Curtis: creative mathematics as native symbolic moves

[Original study](https://arxiv.org/html/2408.15332v2),
[Two-Hump ICML 2026](https://arxiv.org/html/2606.21611v1),
[public data and solver](https://github.com/Math-AI-Caltech/ACSolverX).

Important corrections to the initial sweep: the newer PPO policy receives
+1000 terminal reward and otherwise max(-total relator length,-10), so it
is not binary terminal-only RLVR. Of 2,380 environments, 640 are fixed known
solvable Miller–Schupp benchmark presentations, with 1,740 sampled from
AC-19/AC-1M. No other 550 of the 1,190 benchmark presentations were solved.
Thus mean 607.2 solves is mostly training-task competence, not held-out
generalization. Older PPO solved 457, new architecture/substitutions
588.2, additional data 607.2; greedy with substitutions 640. The DRT is
already small (2 blocks, width 32, 4 heads), uses cyclic attention and
mathematical composite substitutions. Greedy with substitutions reportedly
finds the same 533 solves as primitive search in 614 versus 1M nodes;
compare search-node/action semantics carefully. This is evidence that
the representation of operations matters enormously.

**More interesting than the authors' future work:**
- [Theorem-guided RL, NeurIPS 2025 workshop](https://openreview.net/pdf?id=lt3Lpa4d2d)
  clusters successful traces, uses Gemini 2.5 Pro to propose theorem
  families, manually proves three, then marks matching states terminal.
  At horizon 1024: 741 vs 378; at 8192: 282 vs 21 (different horizon
  regimes, not directly comparable across rows). 753 unique solves pooled,
  only three incremental unique overall. Shorter paths count theorem
  applications as abstractions, not primitive moves. Stronger reasoning
  can compress search but independent primitive execution is unestablished.
  Direct abstract path-solving DeepSeek-Prover-V2-7B 0%, Claude Sonnet
  8.3%, Gemini Deep Think 75% on an easy small test; general group theory
  Lean success is not equivalent to AC-solving skill.
- [July 2026 equivalence certificates](https://arxiv.org/abs/2607.23611)
  report a minimum maximum-relator-length bottleneck of 19 between a
  length-14 MS branch and AK3, while other length-14 branches need at
  least 27 within the substitution graph. Independently certified
  nonmonotonicity, not a guessed reward valley. AK3 remains unresolved.
- [Analytically tractable thickenable class](https://arxiv.org/abs/2606.06122)
  may offer a mathematically resolved subclass for studying learning.

Questions: Which mathematical computations are reusable across distinct
presentations? Does a learner acquire a generalizable version of a
composite move, or need the supplied action? Are severe length increases
actually rare in successful trajectories? Do independent seeds discover
distinct simplification ideas? Could a small primitive-action learner
recover abstraction or evidence of generalization? Do not conflate
solving training presentations, proving equivalences, and resolving
the open conjecture.

Resources: AC-19 125,192 certified examples; AC-1M 1,136,154; reported
full training ~11 GPU-hours (MI210); generating data expensive but
released. Strong lead for both mathematical behavior and data analysis.

## 2. Graph conjectures and Ramsey constructions

[Wagner 2021](https://arxiv.org/abs/2104.14516) demonstrates small neural
cross-entropy agents refuting published conjectures.
[Ghebleh et al.](https://arxiv.org/html/2403.18429v2) tested 68 bounds:
25 RL refutations, 5 further by exhaustive search inspired by RL,
38 unresolved (not necessarily false). The five misses are bounds
2, 17, 32, 50, 61 (Table 1). One 12-vertex subquartic graph SQ*
refutes 23 conjectures. Exhaustive subquartic search through 14 vertices
was motivated by learned structures. This is a surprisingly reusable
object across nominally different tasks. [Published TensorBoard runs](https://doi.org/10.5281/zenodo.10779251)
are a concrete data source; not downloaded yet.

[2025 thesis](https://arxiv.org/html/2509.01607v1) rediscovers three of
the five misses (2,32,61) with parallel cross-entropy; other two not in
witness table. More random graphs degraded performance; elite-prefix
initialization boosts early results then stagnates. Possible RNG bug
noted, and one tested conjecture had no witness in comparison.
[RLGT 2026](https://arxiv.org/html/2602.17276v1) compares CE, REINFORCE,
PPO across nine graph environments. Linear construction with CE reliable;
nonlinear edits with PPO/REINFORCE rely on cycle initializations or
prove unstable. [Open graph environments](https://github.com/CuriosAI/graph_conjectures).
[Monte Carlo graph refutation (ECAI 2025)](https://www.lamsade.dauphine.fr/~cazenave/papers/ConjectureRefutationECAI2025.pdf)
refutes 12/13 previously refuted Graffiti conjectures in seconds vs
reported neural hours/days, benefits from evaluating partial graphs.
A proposed new refutation has ambiguous definitions: not settled.

**Unusually promising adjacent sources:**
- [RamseyGadgets, Aug 2026](https://arxiv.org/html/2608.14999),
  [code](https://github.com/deepakpandita57/RamseyGadgets): 70 graph
  construction problems with witnesses at <=10 vertices, exact SAT
  verifier, best of assessed open models 51.83% overall and 37.70%
  hardest tier despite tools. Small objects, genuine headroom.
- [PatternBoost](https://arxiv.org/html/2411.00566),
  [code](https://github.com/zawagner22/transformers_math_experiments):
  local search plus small transformer trained on elite objects (not RL).
  33-vertex no-4-cycle problem at 50M local-search calls: 5 graphs with
  >=89 edges for local search alone vs 2750 for improved PB. 6-layer
  width128 model eventually finds 96 edges at 116.5M calls. Width256
  model finds 91 edges under 1M calls vs 8.6M for 2-layer width16.
  Refuted older hypercube conjecture with 81-edge, diameter-6 spanning
  subgraph vs expected 82. Tokenization strongly affects validity.
- [Ramsey AlphaEvolve](https://arxiv.org/html/2603.09172v5):
  nine reported improvements to classical Ramsey lower bounds, e.g.
  R(4,19) from 213 to 219; released witnesses and search algorithms.
  Strong model evolving programs, not a learned graph policy.
- [Not Constructing Ramsey Graphs Using Deep RL](https://openreview.net/forum?id=ODY9UitugC):
  PPO/A2C poor compared with local search; full PDF not yet inspected.
- [Ramsey multiplicity heuristic comparisons](https://link.springer.com/article/10.1007/s10208-024-09675-6):
  CE much slower in anecdotal timings; Cayley representation makes
  search variables linear rather than quadratic in vertex count.

Questions: Are useful structural properties recurrent across conjectures,
and are they actually learned as transferable representations? Can an
ordinary small model invent a graph construction principle rather than
iterate edge choices? What does successful CE teach compared to local
search, search-plus-transformer, or strong-model-generated programs?
Distinguish single-object optimization from learning a reusable method.
Don't assume all unresolved conjectures have counterexamples.

## 3. DeepMind Alchemy: information is present but not used

[Original Alchemy](https://arxiv.org/abs/2102.02926): hidden causal
chemistry varies by episode; symbolic VMPO score 155.4, random
heuristic 145.7, Bayesian trial-optimal 284.4 after 20B steps.
Independent posterior analysis shows agent actions reveal information
that the policy fails to exploit.

[2022 modified representation study](https://arxiv.org/html/2112.08360):
single Tesla T4, score 272.85 with modified representation and shaping,
236.06 without shaping, same architecture canonical input/output/memory
158.91. Semantic output+memory canonical input 243.83, positional outputs
and canonical input 156.34. Removing memory from successful 272.85
system yields 168.88; canonical agent without memory 153.40.
These comparisons point toward representation/variable binding, not
simply opportunities to explore. The architecture and encoding changes
must not be collapsed into one factor.

[Model-based transformer plus search](https://arxiv.org/html/2208.11535):
79.3 score at 100 expansions vs 251.5 at 10k; closes much of gap but
substantial test-time compute. [AMAGO](https://github.com/UT-Austin-RPL/amago#6-meta-rl-symbolic-deepmind-alchemy)
authors' repo describes difficult local optimum and tuning cost, says
their Alchemy generally matches VMPO and hasn't appeared in published
results; links public learner/actor runs. This is valuable candid failure
evidence, not a peer-reviewed controlled comparison.

[2025 frozen LLM study](https://openreview.net/pdf?id=wOrkUTr0W5):
no-prior/no-summary strong models can exceed heuristic but no significant
within-episode improvement (N=10); prior invariants help, summaries often
help, altered rules not universally recovered. [RIME Nov 2026](https://cmu-aire.github.io/RIME/)
Qwen3-4B ACT+WRITE: oracle-normalized 0.301 prompted vs 0.490 trained;
first-to-last-half +0.086 vs +0.213. Exploration reward alone barely
helps without trained writer; trained writer without exploration worse
than untrained. Evidence that collecting and exploiting information
are co-dependent. Not terminal-only RL; verify exact task overlap.

[Public author-provided trajectory corpus](https://huggingface.co/datasets/Racktic/alchemy-eval-logs):
~80GB, selectively inspect/download if needed; five Qwen3-4B runs
(ACT-only, WRITE-only, co-train, free-form, no-memory), frontier zero-shot
and exact oracle on 1,000 chemistries, cross-model memory and failure logs.
Not peer-reviewed; provenance and metric comparability need checking.

Questions: Does the model know what happened, or does it lack a usable
representation connecting experience to later choices? Can the policy
acquire abstraction and variable binding from ordinary experience?
Which evidence is present but inaccessible to decision-making? How do
trained memory representations and exploratory behavior co-develop?
A score gain from supplying belief states does not establish independence.

## 4. Sokoban: a small learner invents a planning algorithm

[Guez et al. 2019](https://arxiv.org/abs/1901.03559) introduced deep
repeated ConvLSTM (DRC). [2024 planning behavior](https://arxiv.org/html/2407.15421v1)
shows it discovers extra thinking time by cycling through movements even
with per-step penalty. Planning-time performance increment emerges
during first ~70M transitions, then weakens on medium levels while
strengthening on hard ones. This is a useful observed developmental
trajectory; weakening increment does not by itself mean skill forgotten.

[ICLR 2025 causal planning](https://arxiv.org/html/2504.01871): 3 recurrent
layers, 3 ticks per action, 32 channels, 250M training transitions
on 900k Boxoban levels. Learned internal plans tested via interventions,
resembles forward/backward planning. Reward includes -0.01 per step,
+1/-1 box on/off target, +10 all goals; not terminal-only. Appendix F
single-layer nine-tick DRC trained 100M transitions solves 84.9% unseen
levels, +0.8 points on medium with five extra thinking steps; also
causal evidence of planning. ResNet appendix shows preliminary
planning-like computations even without recurrent state.
[Trained model archive](https://huggingface.co/AlignmentResearch/learned-planner/blob/main/README.md):
DRC(3,3) 1.285M parameters; DRC(1,1) 0.988M; ResNet 3.068M.
[Code](https://github.com/AlignmentResearch/learned-planner),
[training](https://github.com/AlignmentResearch/train-learned-planner),
[Boxoban levels](https://github.com/google-deepmind/boxoban-levels).

[ICLR 2026 Path Channels and Plan Extension Kernels](https://openreview.net/pdf?id=z025sIH4Nq),
[conference](https://proceedings.iclr.cc/paper_files/paper/2026/hash/d92595f484e8df5f190477fb3f245780-Abstract-Conference.html):
hidden channels encode directional paths, learned convolution kernels
extend paths in both directions, obstacles produce negative activations
that propagate backwards and prune plans. Causal test of obstacle
activations supports backtracking. [Earlier preprint](https://arxiv.org/abs/2506.10138)
also describes value-like activation magnitude, separately represented
boxes and different layer-specific plans. Not identical to classical
search. One revealing failure in Appendix L: zig-zag levels solved up
to n=15, fail above; 20x20 backtrack succeeds, 30/40 fails. Activations
decay as paths extend; multiplying selected recurrent weights by 1.2
allows zig-zag through n=25 and 40x40 backtrack; stronger modification
can lead to incorrect locked paths and chaotic activations. Demonstrated
failure of an *already acquired algorithm* to extrapolate in length,
with mechanistic evidence, not just a reward-starvation story.
Reward differs across paper versions/agents; do not conflate configs.

This is an excellent positive anchor: ordinary learning can invent
search and backtracking without human-provided algorithms. It also
creates a research question beyond solving puzzles: what makes an
algorithm that works locally fail to scale? Could different training
make it intrinsically extrapolate, instead of changing weights at
inference? Is box-by-box factorization sufficient for coordinated
multi-box detours? Inspect actual failures before drawing conclusion.

[ICML 2026 Learning to Search and Searching to Learn](https://arxiv.org/html/2605.25720v1)
has contrasting relational planning scheme with search-derived Q targets.
On 1,000 10x10 Sokoban tasks, greedy policy 681 vs lifted HER 309;
weighted A* with learned guidance 1000 (207 mean expansions), versus
classic weighted A* 3298 and DeepCubeA 1050 (reported comparisons).
On harder IPC scale, greedy 14% vs guided search 32%; distinct task
semantics. On 24-puzzle the learning method finds no training goal,
other search learners solve all test cases — explicit gradient access
contrast. On PushWorld Level 1, greedy 5/63, search 48/63, LAMA 60
reported (different evaluation exclusions/budgets). No need to treat
search-derived signals as ordinary RLVR or inference assistance as
policy competence. Paper supplies strong complexity and transfer probes.
[SokoBench 2026](https://arxiv.org/abs/2601.20856) reports deterioration
of LLM planning beyond ~25 moves despite simplified puzzle structure;
interesting separate comparison with recurrent neural planner.

## Preliminary cross-domain observations (not a mechanism prescription)

- In AC, a mathematically useful abstraction can shorten computational
  search by orders of magnitude; current policy uses human-supplied
  substitutions, and much apparent competence is on training tasks.
- Graph discovery has direct evidence of mathematical structures generated
  by RL becoming useful to independent search across multiple conjectures.
- Alchemy distinguishes seeing informative events from learning to
  represent and use their implications, with multiple strong comparisons.
- Sokoban shows an ordinary small network autonomously discovers a
  complex algorithm, yet fails in an identifiable way when scaled.

The common question is not whether a specific prior intervention works,
but what the learner has discovered, what it has not, and what the
stronger solutions reveal about the space. Initial promising data audits:
AC held-out vs fixed training instances, graph patterns across conjectures
and method trajectories, Alchemy selective logs, Sokoban released
checkpoints and scale-controlled failures. No download or training
authorized by this literature-only request.

## Late findings from completed deep reports

### Tree polynomials — striking new branch of graph discovery

[Tree unimodality via PatternBoost](https://arxiv.org/html/2510.18826),
[code and ~35,000 counterexample run](https://github.com/ericgramos/TreeUnimodalityPatternBoost).
PatternBoost is elite-trained transformer plus local search, not PPO/GRPO.
Without local swaps transformer alone found no violations and collapsed
to path permutations. On a 56-vertex task targeting a different
coefficient, epoch-five top 50k examples consisted of 42,608 path
relabelings and 7,392 single-leaf-modified paths despite a known Galvin
witness. Search and restrictions later found six counterexamples but not
the known Galvin tree. Emergent low independence number helps ordinary
discovery but obstructs other mathematically valid constructions;
explicit penalty did worse. At 60 vertices after five epochs, the
degree-based branching heuristic (helpful in small runs) produces 247
counterexamples, versus 26,766 lexicographic and 24,163 random ordering.
Study the actual compute and conditions before interpreting causal effect.

[Dominating-set polynomial followup](https://arxiv.org/html/2605.02193v1):
PatternBoost finds single log-concavity violations but no double
violations, while analytical rooted-gadget composition proves trees
with arbitrarily many violation indices. Related [consecutive
violations](https://arxiv.org/abs/2603.14204), [spherically symmetric
trees](https://arxiv.org/abs/2610.04172). Distinguish independence and
dominating-set polynomials. Prüfer encodings give valid arbitrary
labeled trees; exact integer dynamic programming available. Reported
training 5–15min/epoch to several hours/run on RTX Ada 5000.
This is perhaps the most compelling *new* lead: a creative learner
finds thousands of mathematically meaningful objects, but fails to
compose known constructions; independently witnessed headroom, with
human heuristic sometimes reducing discovery. Still not an ordinary
RLVR finding until tested as such.

Graph dataset size 475.9 MB [Zenodo](https://zenodo.org/records/10779251).
Ramsey AlphaEvolve explicitly reports evolved algorithms cell-specific
and not transferring across (r,s); algebraic seed families important
in some cells. See [teacher–student structural transfer followup](https://www.mdpi.com/2227-7390/14/8/1367)
for a prescribed-structure comparison. RamseyGadgets zero-shot Llama
3.1 8B 1.71%, DeepSeek-R1 10.29%, GPT-OSS 120B 21.14%, Gemma 4 31B
36.0%; Gemma with graph colorer 51.83%, ~56k tokens; structural hints
generally hurt other models.

### AC extra evidence

Original 2025 variable-horizon PPO independently solves two presentations
missed by primitive greedy search, simplified lengths 195 and 381 moves
with substantial temporary growth. Newer Appendix H example: 80 composite
substitutions vs 1080 elementary moves (871 conjugations).
[Machine-checkable artifacts](https://github.com/joe-carr-data/ac-certificates).
[July 2026 learned automata study](https://link.springer.com/article/10.1007/s10817-026-09759-8):
even AC-equivalent initial presentations yield distinguishable sampled
neighborhoods, test accuracy ~81–83%; misclassified examples more likely
to simplify with one automated reasoning encoding (36 vs 5% within
30 minutes), not replicated with alternative encoding. This suggests
search-dependent internal organization of equivalent mathematical objects.

### Alchemy extras

Original ideal observer optimizes within trial, not exact future-episode
planning; full chemistry oracle 288.5. Modified representation
[implementation](https://github.com/bkhmsi/alchemist); canonical potion
slot versus persistent semantic identity is a critical distinction.
Even 272.85 system retains some opposite-effect and blocked-transition
deficits. [Adjacent simplified-model work](https://arxiv.org/html/2302.04250)
reports ~90% optimum within 100 steps with explicit graph supervision;
not comparable directly. Author dataset hard-subset frontier comparison
~0.67 oracle-normalized Opus 4.8 vs ~0.27 Qwen3.5-4B, unaudited.
