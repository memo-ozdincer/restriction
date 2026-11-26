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

## User idea-dump, verbatim (independent critique request)

> Alright. Now send subagents to critique our proposal, how it may or may not hold up to the magic of rl criteria, and perhaps what specifically assume(p) implementation can be, and what more criteria is must hold (they should propose ways in which certain implementations of the overall trainer, or assume(p) can break the magic of RL and propose requirements to robustly not allow for that,
>
> Right now the proposal is more or less.
> - Some general object assume(p) that can be implemented in a way such that it can be anything, including the invariant-type things we had seen.
> - The way we preserve generality is that we don't restrict the model's ability to use P, but we somehow reward it in a way that prevents using P in a way that breaks the magic of RL:
> 1 - the magic of rl can be broken if P is spammed in ways that don't pan out to real mathematics
> 2 - the magic of rl can be broken if P in any way gets in the way of the magic of RL, so, perhaps it is too restrictire, perhaps it is not "intrinsic", or "natural" enough, etc. we need to make it as natural to the environment as possible, which the subagents will suggest criteria for. The idea is, it should have JUST as much magic as a vanilla lean environment.
> Note: this is starting to look like a prover that is alloewd to defer certain parts of a proof. Not sure how I feel about it. Time becomes the axis of freedom we give it kind of.

## Independent critique (three subagents, November 25)

Independent reviewers were tasked with RL incentives/trainer behavior, Lean
semantics, and experimental falsification. Their critiques converge on a
potentially decisive objection: the proposed operation is **already part of
ordinary Lean reasoning**. No proof rule or new mathematical capability is
introduced by an assumption that must later be proved. The useful freedom, if
any, is the timing and persistence of experiment-derived feedback.

### Reviewer A: RL incentives and credit assignment

- There is no necessity test compatible with indifferent terminal RLVR.
  A redundant P in a valid closed proof is legitimate. The only hard reward
  guarantee is that no undischarged assumption can contribute to positive
  reward. Finite shared resources supply opportunity cost for pointless
  speculation; they cannot guarantee zero spam.
- Per-hole costs, count caps based on desired usage, solved-hole bonuses,
  proof-length penalties, stepwise discounting, and accepting only
  helper-approved P impose preferences or change the effective objective.
  Generic finite resource ceilings apply to all actions equally.
- Root-level rollout groups must include all attempts, including failures,
  rolled-back explorations, and unclosed obligations. Do not resample them
  for free, filter on tool use or solver progress, or reinterpret failed
  attempts as successful partial trajectories.
- On-policy training uses the actual chronological action tokens with their
  actual sampling-context log probabilities. Tool observations are context,
  not actor actions. Do not silently reorder or compile the proof and
  pretend the resulting text was sampled by the policy. Replay or SFT on
  assembled proofs would be a distinct intervention.
- Delegation makes P=G offloading legitimate team success if the helper
  solves G, not evidence of actor competence. Share compute and privileges;
  compare direct solver calls and require individual unassisted evaluation.

### Reviewer B: Lean semantics and naturalness

Lean already has `suffices`, `have`, term holes, multiple open goals and
goal selection. See official [tactic reference](https://lean-lang.org/doc/reference/latest/Tactic-Proofs/Tactic-Reference/),
[goal selection](https://lean-lang.org/doc/reference/latest/Tactic-Proofs/The-Tactic-Language/)
and [metavariable semantics](https://lean-lang.org/doc/api/Lean/MetavarContext.html).
These are current documentation; any execution must be tested on the project's
pinned Lean, not assumed to work based on current syntax.

A conceptual native representation of the operation is
`refine (fun h : P => ?consumer) ?producer`. The consumer can use h:P;
the producer must establish P in the context before h. The model can schedule
each live goal. This is not new logical expressivity. `suffices h : P by ...`
already puts the consequence first in a normal proof script.

If a persistent interactive wrapper is justified, use actual Lean
metavariable identity and scoped context, including dependent locals, local
instances and native elaboration constraints. Do not reconstruct proof
obligations from pretty-printed goals, merge states by text equality,
invent local axioms, or allow a later hypothesis to discharge its own source.
Native goal switching, resumption, and branch rollback must retain exact state.
No `sorry`, generated global axioms, or bypass of the final kernel/allowed-axiom
check. All obligations in the selected final proof must close; discarded
speculative branches may be abandoned with their costs charged.

A custom `P : Prop` cut would still limit the generality of native typed
holes, which may have non-propositional types and dependent witness goals.
An interface allowing suspension/focus of any legitimate Lean metavariable
is potentially more natural than a special proposition tool. Keep native
tactics legal; no automatic simplification, lemma search, goal ranking,
semantic pruning or task-specific context synthesis unique to the intervention.

A major control dilemma: enforcing prove-before-use while retaining
unrestricted vanilla Lean cannot prevent a policy from using `suffices`.
A restricted chronology comparison is a separate explicitly labelled
diagnostic, not vanilla RLVR. Do not artificially cripple the baseline.

### Reviewer C: falsifiability and experimental controls

If the whole-proof baseline lacks live proof-state feedback but the
intervention has it, any gain conflates temporal deferral with interactivity.
Use the same interactive observation, tactic granularity, parser, context
budget and Lean rules; compare unrestricted native Lean to optional explicit
defer/resume interface. A same-proposed-obligation prerequisite-first versus
consequence-first comparison is a separate mechanistic diagnostic. A shared
frozen policy-generated P bank can isolate chronology in that diagnostic,
but should not constrain the main learning policies.

For delegation compare to giving the same frozen solver the original goal
at the same total resource budget. Co-training is a different contrast;
the solver may change policy and the proposer's effective environment.
Do not conflate a team solve with the actor's unassisted proof ability.

Falsification:
- No gain over unrestricted native Lean: no evidence of useful new affordance.
- No gain over prerequisite-first in chronology diagnostic: no evidence that
  consequence-first discovery is the advantage.
- Assisted gain but no unassisted gain: inference scaffolding, not demonstrated
  general capability improvement.
- Direct solver matches delegated system: no demonstrated gain from decomposition
  beyond additional inference.
- Gains only on handcrafted related families: no demonstrated broad transfer.

## Reconciled design: freedom in time rather than additional mathematical facts

A stronger candidate is a thin native goal scheduler. At the mathematical
level the model already has the right to choose any proposition, local
variable or well-typed hole using ordinary Lean. At the operational level
it can choose to work on an obligation now, later, or on another open
obligation, with access only to authentic verifier state. A custom
`assume(P)` could be surface syntax for creating a local cut plus linked
native obligations; direct native goal operations should be the default
candidate, not a new proof rule. If the underlying native environment
already permits arbitrary interleaving and observations, a wrapper gives
only accessibility/syntax convenience, not necessarily more freedom.
Do not claim novelty before measuring this difference.

Important distinction: seeing that a continuation works under h:P does
not establish P. It provides a conditional mathematical observation.
The policy can choose to invest further effort in P; the environment
does not rank its promise. If P is false/unprovable in its context the
conditional achievement still earns no positive reward. An unused P or
abandoned branch is not separately rewarded, and abandonment cannot
erase a required proof hole. An independently valid proof with unnecessary
extra steps is still valid; terminal RLVR is indifferent to elegance.

### Expanded non-compensatory rubric and test requirements

| Gate | Requirement | Breaking implementation / required check |
|---|---|---|
| Conservative extension | Same target, logic, libraries, axioms and legal native tactics; every terminal success independently replays as ordinary Lean. | Temporary axioms/sorry or changed goal; reject incomplete/cyclic/corrupted root. |
| Native generality | No human-selected form of P, and native arbitrary typed holes remain possible. | Whitelist invariants, force single P, ban existing tactics; verify nested, quantified, branch-local and dependent witness obligations. |
| Temporal agency | Policy chooses placement, number, focus, suspension, resumption and rollback. | Auto-prioritize P or force solve order; check both orders, multiple open goals and exact rollback. |
| Context fidelity | Native scoped obligation identity, exact pre-assumption producer context, authentic Lean observations. | Goal-string equivalence, leaked future hypothesis, mismatched branch scope; test same printed goal/different context, stale handles, cyclic dependency. |
| Epistemic neutrality | No extra knowledge, ranking, repair, or solver proof supplied uniquely to an arm. | Hand-authored crutch schedule, useful-lemma filter, hidden stronger oracle; audit state/prompt payloads and compare equal privileges. |
| Terminal reward purity | Reward is one only for verified original-root closure; no hole-level bonuses/penalties. | Reward P=G assisted finish, easy hole counts, token-level discounts. Test legal P=G, false P, unused P, redundant P, and honest root closure. |
| Resource symmetry | Fixed task-independent compute budget; charge all generation, Lean calls, failed and abandoned branches, solver work; no free retries. | Hidden speculative extra sampling, ignored parallel work; reconcile physical attempts and tokens to root budgets. |
| Credit symmetry | Same terminal rollout accounting and loss, actual actor action/logprob pairs, tool observations masked. | Train assembled proof text as if sampled, drop failed branches/groups, select only successful snippets; test disabled-tool identity and synthetic trajectory accounting. |
| Baseline fidelity | Unrestricted native Lean and identical observation/feedback, initialization, action granularity, context, budgets. | Whole-proof baseline versus interactive intervention; artificially ban suffices, change verifier, or restrict ordinary tactics. Verify same no-tool behavior. |
| Unassisted transfer | Evaluate learned policy on fresh theorem families with wrapper/delegate disabled, native Lean unchanged. | Treat tool-assisted pass rate or attractive discovered invariants as evidence of learning; separate metrics and never reward diagnostic proxies. |

The first nine are design/implementation gates (pass, ambiguous or fail;
not a compensatory score); the final gate is the empirical test of the
capacity-building claim. No implementation can guarantee emergence or
absence of useful suppression given finite compute and changed action
representation. The premise is a hypothesis, not an unfalsifiable conclusion.

### Minimal candidate experiment sequence (design only)

1. Authenticate the pinned native Lean goal-management primitives and compare
   candidate scheduler semantics to vanilla. Verify ordinary unassisted
   replay, exact context fidelity, nested cuts/typed holes, P=G, false P,
   circular discharge rejection, rollback and full terminal correctness.
2. Determine if any operational freedom is genuinely new relative to
   native interactive Lean. If only syntax/token convenience remains,
   reconsider the mechanism rather than sell it as new logic.
3. If an operational difference exists, compare standard terminal RLVR in
   equal-interaction native environment against optional scheduler RLVR,
   with no new reward term or imposed use. Separate chronology-only diagnostic
   uses matched self-generated obligations if scientifically justified.
4. Primary outcome is unassisted ordinary proof generation on new families;
   secondary assisted performance at matched resources; diagnostic usage,
   unused/rolled-back P, repeated/type-invalid P, P=G and solver shares,
   proof modes and generalization. No other trained intervention yet.

No experiment registered or run. The user requested critiques and requirements,
not implementation or compute.
