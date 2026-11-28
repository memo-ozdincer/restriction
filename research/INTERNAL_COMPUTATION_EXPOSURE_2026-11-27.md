# Alchemy and Sokoban: from environmental exposure to computational freedom

## User idea-dump (verbatim)

> 3 and 4 could tell us a LOT about how to design our interventions. Send subagents to figure out exactly what these could look like. How changing our interventions could be affected based on knowing A - Alchemy is just IMO being smarter with the environment design not a huge breakthrough; B - The Sokoban could tell us a lot about what intervention beyond just randomized starting positions we could create...

Literature evidence and caveats: [four deep dives](CREATIVE_RLVR_FOUR_DEEP_DIVES_2026-11-27.md).
Three independent critiques; no experiments launched. These are candidate
mechanisms, not claims of novelty or known efficacy.

## Alchemy: make the environment intelligible, don't supply the inference

The interface can obscure relations already observable in the environment.
Stable public entity identity is not an oracle for hidden chemistry. Prefer
information-preserving, semantically faithful interfaces as a design
principle. Distinguish representation changes from a learning intervention.

- Use persistent anonymous handles (renamed independently per episode)
  versus positional references; preserve original slot mapping where possible
  for information-equivalent controls. In mathematics, stable bound-variable
  identity, scope and object references—not hand-selected invariants.
- Two equivalent serializations of the same experience, selected randomly
  during training (native versus immutable action/entity/outcome events).
  No hidden facts or posterior; evaluate with original interface. Compare
  against same serialization always, matched context/compute. Improvement
  only with redesigned interface is still useful engineering, not evidence
  of learned abstraction.
- History-conditioned continuation: branch from a policy-generated prefix
  preserving the same hidden environment and actual action/outcome history.
  Compare intact history, no history and matched irrelevant history; charge
  prefix cost. Partial observability means physical state alone is not the
  complete information available to a learner.
- Fork several legal futures from a shared informative experience without
  selecting on outcome; compare independent prefixes at matched interaction
  cost. Tests whether applying the same experience in multiple contexts
  teaches its significance. Avoid silently changing goal.
- Optional model-owned scratch/workspace; no prescribed note contents or
  process reward. Evaluate with and without workspace, and distinguish
  learning transfer from online tool utility.

## Sokoban: expose the learner to different conditions of computation

A learned internal planner extends paths in both directions and revises
them via negative activations. Long-range activation decay limits
extrapolation; increasing recurrent gain rescues some longer tasks but
can prevent revision. This is a persistence-versus-revisability problem.
The 1.2x weight modification is an inference diagnostic, not a training win.
Do not prescribe particular channels, kernels or the known search algorithm.

### Candidate interventions, increasingly ambitious

1. **Variable thinking time.** Identical recurrent policy, ordinary starts,
   independently sample latent ticks per action (e.g. 1–8); no physical
   transitions or reward during ticks. Fixed ordinary and fixed mean-tick
   arms; match primitive recurrent compute and environment interactions,
   evaluate at fixed original ticks and across frozen compute sweep.
   Could train an algorithm stable across computation lengths. Model-owned
   stop/continue is a distinct experiment with charged compute.
2. **Structural dilation.** Randomly stretch ordinary puzzle geometry or
   primitive computational chains while preserving rules and objective
   (task distribution changes). Match lengths against other diversified
   geometries; hold out larger scales. Cross with variable ticks to
   distinguish spatial-scale experience from computation-time variability.
3. **Internal exploration noise.** Small isotropic hidden-state
   perturbations during thinking, removed at evaluation. No change to
   observed environment, rules or goal. Compare logit/action noise,
   ordinary dropout, additional ordinary compute, inference-only noise.
   Test whether perturbation training produces better unperturbed
   algorithms and whether it merely causes generic regularization.
4. **Random interruption and recovery.** Erase random subset of scratch
   activations or reset deliberation at random tick; no reconstruction
   supervision. Learn terminal behavior after interrupted computation.
   Compare no interruption, standard dropout and full reset; long-task
   tests distinguish recovery from a memoryless fallback.
5. **Random computation scheduling.** Generic masks/order of spatial
   or layer updates while retaining weights and same observation. Match
   expected update counts; fixed mask versus fresh random mask; evaluate
   synchronous normal model. Tests independence from fixed clock/dataflow,
   but may be architecture-dependent.
6. **Internal-state exposure.** Archive hidden states from prior
   deliberations on the same observed board, including failed and
   successful computations; restart internal deliberation from those
   states, keep physical root identical. Compare fresh hidden state
   and random noise, charge prefix compute, check checkpoint/version
   compatibility and avoid train/test leakage. Unlike arbitrary hidden
   vectors, real recorded snapshots have provenance. In language models,
   the analogue is self-generated scratchpad continuation (prior art).
7. **Counterfactual replanning.** Think about one valid board, replace it
   before first action with another valid same-goal board, retain scratch
   state. Only final solve of second board rewarded. Compare same board
   distribution with reset state/no prior thinking. Tests revision and
   discarding stale internal plans, not physical recovery. Training
   distribution changes; mild edits versus independent draws useful.
8. **Model-owned internal branching.** Generic bounded latent scratch
   copies with optional fork, reset, retain, continue. No supplied path
   or additional simulator calls. Same terminal reward, charge every
   recurrent update including discarded branches. Compare serial compute,
   random allocation, and unassisted native interface. This is an
   architecture change, not a single-factor continuation of existing DRC.
9. **Equivalent re-encoding.** Rotate/reflect board and remap actions
   exactly; vary observation encoding without varying semantics. Test
   geometry-independent computation; distinct from random physical states.

## Common experimental principles

Fork identical checkpoints or start identical base policies. Match
environment interactions and actual recurrent computation; these are
different resources. Assess fixed native inference budget first, then
compute sweeps. Evaluate independent held-out levels with long propagation,
unexpected obstacles, multi-box coordination, without intervention.
Use learned path-channel probes only for post hoc diagnosis, never reward.
An improvement at extra inference compute alone is not an acquired skill.
No requirement to discover classical bidirectional search specifically.

Most attractive first directions: variable computation duration (clean
and inexpensive), internal-state exposure/noise (strong analogue of
random-start exposure at a different level), and model-owned branching
(more expressive, more confounded). Replanning/interruption can probe
persistence versus revisability. Keep representation hygiene distinct
from the scientific claim; do not label every helpful design as a
breakthrough. Novelty review needed before any paper claim.
