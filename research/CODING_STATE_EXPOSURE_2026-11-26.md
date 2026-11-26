# Coding state exposure — research charter and handoff

November 26, 2026. New direction, branched from the fully preserved mathematical
speculation branch at a003784. No coding experiment has been run yet.

## User steering (verbatim)

> I think we just do 1. But now you need to find me the most "magical" coding environment. for example web design would have zero magic. Go (alphago zero) has near-maximum magic, lean has quite a bit of magic. Find me a classic standard set of coding RL tasks that have quite a bit of magic. so, very verifiable, and ideally very "models don't necessarily have to listen to humans" kind of thing. Idk if thats chip design or assembly or low latency coding or verilog, or idk. you definitely know better.

> but which one actually has that "would benefit from playing around within the established best solutions" or obvioulsy, established best solutions is a compromise since we can't do real random starts, so if you can think of a real random start that would be even better

> ugh we should have switched to coding long agooooo.... make a branch lets go. also make sure everything is documented because we had a massive amount of ideas

## Primary hypothesis: exposure before specialization

Broad experience of legal native computational states can train transferable
skills that are inaccessible or rare from a standard start, and those skills
can produce delayed performance improvements when subsequent ordinary RL
specializes on the unmodified task. This is a testable hypothesis, not a result
in coding. Prefer trajectory-independent random starts over replay of known
solutions. Neither known solutions nor human-approved intermediate steps
should be necessary ideally. The task should be ordinary benign algorithmic
computation, not a human-preference or subjective quality benchmark.

The motivating pinball experiment used evolutionary selection, not GRPO.
Fixed generation-60 random-start-to-entrance switching yielded 82.3% on fresh
entrance tests, compared to 49.4% entrance-only and 10.1% random-only. At
generation 150 the fixed-switch group still trailed regular-only; by generation
200 it reached 56.2%, versus 24.3% regular-only. Eight paired training seeds;
not proof of a specific learned mechanism. Earlier independent replication:
92/2048 versus 42/2048 entrance wins after random-start versus regular-only
training. Details, source paths, hashes, and caveats are in the state-exposure
notes.

## What we mean by magic

- A fixed objective, exact or clearly characterized machine verifier, no
  preference for familiar human solutions, no process reward.
- Broad freedom of action under the environment's own rules.
- A meaningful native state representation shared by practice and final tasks.
- Genuine opportunities for unconventional strategies, not merely choosing
  among human-approved solution templates.
- Ultimately measure independent performance from the original start, without
  any free scaffolding; account for all generation and verification costs.

Legal random starts need not be reachable by the current policy. A valid
computational state is not necessarily useful, reachable from the original
start, or equivalent to a universal solution. Keep those distinctions explicit.
Avoid conflating learning with search-time completion of supplied fragments.

## Candidate environments (not a final selection)

| Environment | Why promising | Crucial caveat |
|---|---|---|
| Digital combinational circuit synthesis (ABC, EPFL) | Random acyclic gate graphs have well-defined Boolean semantics; equivalence can be checked exactly; gate count/depth are objective | Starting gates alter resource budget; arbitrary circuits may be irrelevant; distinguish synthesis from optimizing an already correct circuit |
| AlphaTensor | Residual tensor and fixed zero terminal state; exact finite-ring or integer arithmetic; established discovery benchmark | Arbitrary residuals can be unrelated to target; a random residual need not have a feasible remaining decomposition under the same budget |
| AlphaDev-style arithmetic/sorting | Explicit symbolic register states and executable instruction semantics | Per-input success is not universal correctness; random concrete values alone cannot establish algorithm discovery |
| CompilerGym | Standard RL infrastructure and program states | Human-designed optimization actions narrow discovery; arbitrary transformed programs require equivalence guarantees |
| KernelBench | Open-ended numerical kernel optimization | Finite tests, tolerance and timing confounds; comparatively expensive |
| VerilogEval/RTLLM | Executable hardware specifications | Testbench success may not guarantee equivalence; many benchmark prompts are conventional code generation |

Working preference: investigate small combinational circuit synthesis first,
with AlphaTensor and AlphaDev-style bounded arithmetic/sorting as alternatives.
No particular benchmark version, action representation, sampler, training
algorithm or model has been selected. A small policy may be more informative
and cheaper than a language model initially. This is a possibility, not a
requirement.

Sources: [AlphaTensor](https://www.nature.com/articles/s41586-022-05172-4),
[AlphaDev](https://www.nature.com/articles/s41586-023-06004-9),
[CompilerGym](https://github.com/facebookresearch/CompilerGym),
[KernelBench](https://arxiv.org/abs/2502.10517),
[KernelBench-Verified](https://arxiv.org/abs/2607.16241).
The circuit benchmark and implementation remain to be verified before selection.

## Proposed experimental contrast — not registered or launched

At equal total environment/verification and learning budgets compare:
ordinary-start-only; random-start-only; random-start then ordinary-start-only.
Inspect original-start performance throughout, including after the switch.
If useful, add a mixed-reset comparator to separate exposure from scheduling.
Before implementation, identify a meaningful reset distribution, exact terminal
criterion, resource accounting and a concrete discriminating hypothesis.
The Lean baseline is untouched; its model and verifier commitments remain for
historical Lean comparisons, not prescriptions for a different environment.

## Full idea inventory (retained, not all active)

1. Trajectory-independent random starts followed by full-task specialization
   (selected direction).
2. Recursive expansion of the training-state distribution using native states.
3. Free/randomize degrees of freedom (position, momentum, resource tolerance).
4. Reuse states from failed trajectories and optionally move starts backwards
   following a terminal success.
5. Model-directed HELP, terminal-only collaborative outcome, separate team
   performance from eventual individual capability; multiple partner responses.
6. Intrinsic hindsight: speculate about a computational object and later earn
   it; time-axis deferral rather than supplied reasoning.
7. Near-miss survival and suppression; Supervision Through a Straw research.
8. Synthetic environment generation without relying on human traces; distinguish
   true state randomization from generated tasks, typed grammars, and learned
   proposing policies.
9. Related mathematical explorations: assumptions/wildcards, deferred
   obligations, invariant experiments, forced exploration, symbolic
   specialization, nearest-neighbor and concrete-instance transfer,
   Boltzmann/GFlowNet typed-space sampling, formal quotienting,
   empowerment-based symbolic sandbox. None silently discarded from the record.
10. Physical analogies: valley landing tolerance removal, timed-door relaxed
    planning, hidden-checkpoint pinball imagined endings and legal splices,
    random position at rest and the proposed random-velocity follow-up.

### Durable records and handoff

- [State exposure: all prior brainstorming, user verbatim dumps, physical evidence and prior art](STATE_EXPOSURE_RLVR_2026-11-26.md)
- [Intrinsic hindsight and HELP: all critique rounds and user notes](INTRINSIC_HINDSIGHT_PROPOSAL_2026-11-25.md)
- [Near-miss tracking](NEAR_MISS_TRACKING_2026-11-25.md)
- [Supervision Through a Straw / APRIL](SUPERVISION_THROUGH_A_STRAW_APRIL_2026-11-25.md)
- [Mathematical speculation](MATHEMATICAL_SPECULATION_2026-11-25.md)
- [Lean speculation follow-up](MATHEMATICAL_SPECULATION_LEAN_2026-11-26.md)
- [Lean delegation and discovery synthesis](LEAN_DELEGATION_AND_DISCOVERY_SYNTHESIS_2026-11-26.md)
- [Small Lean RLVR pilots](SIMPLE_LEAN_RLVR_PILOTS_2026-11-26.md)

All historical tracked files are inherited unchanged. The three-agent coding
prior-art audit is in the state exposure document's final section. General
restart curricula, prefix methods and synthetic task curricula predate this
work; exact coding random-start-to-root-only delayed transfer is not established
by the reviewed papers, but absence from the search is not proof of novelty.
No code, checkpoints, or raw results for new coding experiments exist yet.
