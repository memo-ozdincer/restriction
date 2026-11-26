# Lean delegation and mathematical discovery: joint evidence

Two frozen inference pilots, 117 Codex CLI sessions in total. Both use Lean
4.9.0-rc1, but the HELP pilot uses four authored core-Lean roots and the
speculation pilot uses eight MiniF2F roots with a selective Mathlib import
closure. Different tasks, prompts, and sampling counts preclude pooling
success rates as a single effect estimate. Low/Medium denote reasoning effort,
not different verified parameter sizes. Neither pilot trains a model.

## Evidence by direction of assistance

| Condition | HELP (4 roots, 3 draws) | Speculation (8 roots, 1 draw) |
|---|---:|---:|
| Luna Low direct | 0/12 | 0/8 |
| Luna Medium direct | 1/12 | 0/8 |
| Terra High direct | — | 4/8 |
| Low receives isolated verified HELP | 2/12 | — |
| Low receives bundled verified HELP | 6/12 | — |
| Low receives nonterminal verified object | 2/3 (reverse only, post-hoc) | 0/3 (three roots) |
| Terra receives Low's idea from full attempt | — | 4/8 |
| Terra receives Low's idea-only response | — | 4/8 |

All eight successful primary HELP continuations are direct use of the
entire original goal. Eleven of twelve proposed HELP objects were the goal
or a universally quantified counterpart; all three accepted primary objects
were the full goal. No root had multiple verified primary objects. The
reverse diagnostic is separate: a format-only correction to a previously
rejected Medium response exposed a valid general accumulator lemma, and Low
used its statement twice successfully. Both exact continuations fail when
the lemma is omitted. Baseline Low and Medium were each 0/3 on that root;
preexisting empty HELP cases were also 0/2. This establishes one conditional
proof path, not a randomized treatment effect or trained capability.

## Three separable failure modes

1. **Discovery:** the model may lack a useful mathematical relationship.
   `revAcc as bs = as.reverse ++ bs` supplies a general relationship from
   which the double-reversal theorem follows; the actor never sees its proof.
2. **Execution:** a model can express a correct mathematical plan but fail
   to encode it in Lean. On the even-factor problem Low derives
   `(n+1)^2 = 289` in its idea-only response; its standalone formal attempt
   fails nonlinear arithmetic. On the ratio problem Low identifies the
   cross-multiplication but cannot clear the denominator. Terra succeeds.
3. **Consumption:** even a verified fact sufficient to close the original
   theorem can be ignored. On the tree root all four Low continuations
   receiving the complete theorem fail, although `exact help0` verifies.
   In the speculation pilot all three fact-assisted Low attempts fail even
   when they attempt to use the supplied fact. Verified availability is not
   equivalent to usable knowledge.

These are overlapping diagnostic categories, not measured latent abilities.
The reverse lemma demonstrates successful discovery-to-consumption transfer;
not all failures can be attributed to missing discoveries. The generality
and form of a useful fact may matter, but two pilots cannot isolate whether
content, representation, task, or model capability causes the difference.

## What the two directions imply

* **Low→high (plan→execution):** Terra with Low ideas matches its standalone
  four accepted roots; this is not demonstrated causal use of the idea.
  Terra even recovers from an incorrect factorial bound. Idea-only routing
  reduces teacher output by 10.7%, combined output by 3.2%, but increases
  sequential generation time by 12.2%. Full-attempt routing is slower still.
  No speedup or accuracy gain established.
* **High→low (checked object→continuation):** one verified intermediate
  general lemma unlocks Low; three other fact exposures and four exact-root
  exposures fail. Primary bundles mainly repeat whole-theorem handoff, not
  composition. The HELP request-count comparison is not token-matched.
* **Joint hypothesis:** effective cooperation may depend on matching a
  discovered mathematical object to an actor that can consume it, rather
  than assuming a stronger model's insight is sufficient or a weaker model
  cannot discover useful mathematics. The two directions should be treated
  as distinct available actions rather than forced stages of every proof.

## Research propositions and discriminating next test

| Proposition | Joint evidence |
|---|---|
| Great mathematical team | Delegation works sometimes; no demonstrated gain over standalone stronger model at matched compute. |
| Expand actor's reachable reasoning | One positive, kernel-verified conditional existence example. |
| Compose independently discovered objects | Not demonstrated. |
| Mathematical speculative acceleration | Same solved set, no measured sequential speedup. |
| Distillation into the actor | Not tested. |
| Expand terminal RLVR gradients and unassisted ability | Not tested; neither pilot establishes effects on historical GRPO. |

A prospective test (not run): freeze new held-out roots and a native Lean
interface allowing the actor to continue independently, ask for a checked
object, or send a self-generated plan for execution. Keep direct proof legal,
whole-goal HELP legal, and all costs charged to the same total budget. The
only task reward is an accepted complete original theorem. Compare to direct
search with the same cost budget; if training, evaluate fresh roots with
assistance disabled as a separate endpoint. Record object production,
verification, actual consumption, exact omission dependence, whole-goal
handovers, and whether teacher execution follows an actor plan as diagnostics
only. Avoid a reward for lemma size, human-rated idea quality, help frequency,
or intermediate success. A direct proof reward alone can optimize outsourcing
rather than solo competence; test the separate unassisted endpoint instead
of assuming that cooperative performance implies parameter transfer.

This proposal is motivated by the observed consumption bottleneck and the
positive reverse lemma, not by a desire to repeat the same small panel for
statistical significance. No new experiment authorized or launched here.

## Provenance

- [Frozen HELP report](FROZEN_HELP_LUNA_2026-11-26.md), commit `5494eba`;
  [summary](experiments/frozen_help_luna_20261126/summary.json). All 75 saved
  Lean judgments independently reproduced.
- [Mathematical speculation report](MATHEMATICAL_SPECULATION_LEAN_2026-11-26.md),
  commit `0ae6a97`; [summary](experiments/mathematical_speculation_lean_20261126/summary.json).
  All 14 accepted model-generated proofs independently replayed.
- [Living proposal and verbatim idea dumps](INTRINSIC_HINDSIGHT_PROPOSAL_2026-11-25.md).
