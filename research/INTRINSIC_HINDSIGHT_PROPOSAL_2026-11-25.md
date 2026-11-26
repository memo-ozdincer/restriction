# Intrinsic hindsight: an assumption tool that is ultimately removed

Status: preliminary proposal for critical discussion, not a registered run or
validated result. Part of the **Supervision Through a Straw** research direction.

## Governing premise (user)

The working philosophical premise is that prescriptive interventions destroy
the distinctive advantage of RLVR: the model can discover representations
and reasoning far beyond a human's ability to supervise them. The desired
mechanism should elevate that advantage without ruining it. This is the
user's governing research premise, not a claim already established by data.
The environment is indifferent to the particular reasoning employed. No
author-provided proofs, lemmas, stepping stones, repair targets, or PRM.

## Initial proposal

Give the model a general, dynamically available operation: at any proof state
`Γ ⊢ G`, propose an arbitrary well-typed proposition `P` and temporarily use
it as a local assumption. The model chooses P, its location, the number of
nested assumptions and the order of obligations. This produces two obligations:

- `Γ, P ⊢ G` (try the consequence);
- `Γ ⊢ P` (pay for the assumption in the original context).

Only an assembled proof of the original target that closes all obligations
and passes the unchanged Lean verifier can earn success. This is deferred
proof construction, not a permission to assert an unproved proposition in the
final proof. The model can assume G itself; that leaves the original target
unpaid. No author chooses which P is useful. The operation gives the model
a way to discover useful intermediate propositions from experience with the
environment rather than a supplied plan.

Compare terminal-only forward RLVR and deferred-assumption RLVR using the
same initial model, tasks, proposal/compute accounting and correctness verifier.
A further search control establishes self-proposed P before using it, isolating
the hypothesis about trying consequences before paying prerequisites.

The model's own successful discharged construction can be rendered as an
ordinary Lean proof, with the proof of P preceding its use. This deterministic
compilation supplies no mathematical content. Evaluation must include fresh
goals with the assumption interface removed, measuring ordinary proof
generation rather than assisted completion alone.

## User's critique and revised direction

1. Give the model the most general possible tool, then slowly strip it away.
   The proposed tool is `assume`.
2. Risk: the model learns trivial assisted successes (e.g. assuming the target),
   or relies on the tool rather than developing full proofs independently.
3. Tentative possibility: a small cost for using the operation, sufficient
   to discourage unnecessary usage while leaving it available for hard problems.
   Such a cost and any removal schedule are themselves interventions, and
   therefore must be critically questioned against the premise of indifferent
   terminal supervision. No penalty strength or schedule is specified or
   authorized. The existing terminal-only proposal remains the starting point.

No training, new verification, or sampling was requested or performed.

## User idea-dump, verbatim (November 25, continuation)

> We do need some guarantee that the model uses the tool only when genuinely necessary. Wait actually, I guess no.
>
> Wait. Okay, the DESIGN of the experiment is obviously important, but the magic still comes from the end goal, which will be to let the model decide on everything. So, I guess yes, we don't want to make the tool such that the model NEEDS to use it a certain way, we need to make it so that it completes our goal, which, importantly (note this), is NOT: "complete the proof using the crutches", IT IS: "Complete the proof". Very importantly.
>
> And, I'm thinking of two things:
> 1 - "Complete the proof without crutches" - the best experiment, our goal is to get a generally very capable model through the magic of RL. Once again very important, anything that is done without the magic of RL will not generalize. COme up with a rubric for the magic of RL
> 2 - POSSIBLY. Although I'm not sure about what I think about this yet. We frame Assume(p) as "pass it off to another agent in your multi-agent simulation". I guess one way to implement that is to not force the model to find the Assume(P) step itself, but to actually have a different goal, which would be: "write Assume(P)'s at such perfect places SUCH THAT another agent can find them" and that's in my opinion still a good goal, because we're still maintaing the magic of RL, the Assume(P)'s need to be in the exact correct place for another agent to actually fill in the gaps. And, perhaps that other agent can be co-trained or not co-trained, these are all things to decide on.
>
> Issue that comes to mind:
> - how in the world is the model going to use assume(p), we don't know. Will it somehow allow for the model to discover similar kinds of invariants that we had found? Idk.
> - I am thinking, though, that if we require another agent to be able to solve that assume(p) one way or another before sayig its okay to use assume(p) there, that could guarantee the magic of RL a little better. But that's just a direction idea.
>
> Btw. keep taking notes, and save my verbatim idea-dumps in the notes too, such as this one.

## Rubric: preserving the "magic of RL"

The distinction is **designing an environment** versus **designing the
reasoning learned within it**. The experimenter defines the task, legal
actions, resources and final success. The learner is free to discover
which intermediate representations and decisions matter. The working
premise about RL generalization is a hypothesis to test, not a measured
guarantee that only RL can generalize.

Design audit (pass/ambiguous/fail each; do not sum a score that could hide a
failure of a core requirement):

| Criterion | Pass condition | Failure example |
|---|---|---|
| Terminal objective | Reward only closure of the unchanged original target. Zero reward for undischarged assumed facts. | Score useful-looking propositions, count discharged subgoals as terminal reward. |
| Indifferent environment | Generic mechanics fixed across tasks; same verification standard for unexpected solutions. | Supply task-specific invariants or repair algorithms. |
| Endogenous discovery | Every intermediate claim, placement, order and count chosen by the policy; no requirement to use the tool. | Prescribe decompositions, number of holes, or mandatory crutch usage. |
| No epistemic subsidy | Facts from original context, model exploration and unchanged verifier; any extra intelligence supplied by a solver is declared and controlled. | Insert a known answer or pretrained teacher hint into one condition only. |
| Outcome-driven improvement | Learn from final verified task success, not the author's preferred explanation or action sequence. | PRM, explanation targets, rewarded "good" assumptions. |
| Resource honesty | Charge every proposer/solver attempt, unclosed obligation, retry and generation token; same total budgets for comparisons. | Treat delegated computation or disproved assumptions as free. |

Separate empirical audit: **do not** equate passing design criteria with
better learning. Measure unassisted held-out success after tool removal
(primary), assisted held-out success at equal total compute (secondary),
and spontaneous tool use/placement, discovered invariants and proof
diversity (diagnostics, never rewards). Compare no-tool and with-tool
policies starting at the same checkpoint. A tool-dependent model that
does not improve unassisted performance fails the capacity-building
objective even if its assisted system works well.

## Two candidate directions, not yet selected

### 1. Individual deferred obligation

A single learner may propose an arbitrary assumption and choose to discharge
it later. Its actual objective is **complete the proof**, not complete a proof
using assumptions. A policy that never uses the operation is legitimate.
No usage penalty is necessary for the minimal proposal; necessity is not
observable under finite sampling. Removal/fading and usage costs are separate
interventions, not innocuous defaults.

### 2. Delegated obligation (tentative)

The proposer emits arbitrary typed intermediate goals in context. A second
proof policy receives precisely the obligation and pre-assumption context,
and attempts to discharge it independently. The proposer chooses whether,
where and how often to delegate. An accepted overall proof requires that
every delegated obligation has been discharged and the assembled root proof
passes unchanged Lean verification. Proposing G itself is permitted; the
delegate would then have to prove the original problem, and that computation
is counted. Do not accept delegation merely because it appears promising.

Two subtly different candidate objectives must not be conflated:

- **Complete the original proof with optional delegation.** Only closed root
  success earns reward; the solver's success is mechanically necessary
  rather than an auxiliary reward for good hole placement.
- **Produce solvable holes.** A reward for each solved hole, or success even
  when the original root is not closed, is a separate shaped objective; it
  could teach easy or trivial hole selection and violates the strict
  terminal-only rubric. Solvable placement can be an emergent behavior under
  the first version without assigning this reward.

A frozen same-checkpoint delegate is the least complicated first variant;
a co-trained delegate adds a changing environment/opponent and a distinct
credit assignment question. A stronger delegate could supply an epistemic
subsidy, so its identity, privileges and budget must be matched in control.
An ordinary forward proposer plus the same solver budget and same-model
prove-before-use delegation are candidate controls. No delegated proof,
hint, or claimed invariant is supplied by the author.

Preserve both directions for critique. The desired result is unassisted
capability, not tool usage. Whether useful invariants emerge, whether
delegation enables meaningful exploration, and whether either generalizes
after tool removal are unknown. No experiment or training launched.
