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

## User idea-dumps, verbatim (from known propositions to unspecified help)

> A - do models use the lean supplied assume(p) at all? Also, I don't get how it exists in lean, the whole point is to skip over an obligation, how would lean possible let a model skip over an obligation? Also, am I using the obligation word right?
> THe idea is, the object is supposed to be something LIKE the invariants, the model needs to PRETEND it got some eureka moment from the object (just like how it got a eureka moment from the invariants) so that it can start ACCESSING more NONTRIVIAL juice from RLVR. Just like how we saw rlvr would teach it capability unconstrained, we maybe unconstrain it FURTHER, by having it literally push itself in new reasoning directions using this new object, with hopes of it capturing things like the invariant push aturally. so some object that allows for that. Is there really something in lean that already does that??
> B -

> now the issue obviously is we tried many counterexamples to the invariants, such as giving it the bare or irrelevant ones, and it was 0/128, so obviously a generic block seems useless. okay.

> Alright alright nice. So we definitely don't want to go that direction. Is the other direction any better?

> Oh you're talking about multi agent. Well I think that has a problem too cuz like I said, eve if it places the eureka in the exact right spot, if its not the exact eureka object, it doesn't actually learn anything.

> Tell me about the temporal idea

> so literally just allow for backward movement?

> that has been done to death no?

> Okay wait. The lean counterpart of assume(P) requires the model to know what it needs right?

> Okay. What if we make it so it DOES NOT need to know what it needs? The assume(P) is a wildcard that it can do absolutely anything on top of. I'm asking you. is that really stupid?

> Okay. What about the multi agent idea? The model decides where to get help...
> or
> the model decides where to put the wildcards
>
> And we only reward if the wildcards turned out to be solvable
> what do you think about that?

> lets develop the multi agent idea. Where are we so far?
> 1 - The model puts assume(p), and can only resume if the other agent was able to put something there.
> Issues
> - how do we make the original model continue over assume(p) if it doesn't know what it needs to assume?
> 2 - We force the original model to end up with a full proof on its own after whatever intermediate steps it needed
> 3 - We actually train the partner model to FILL IN where the smaller model needs help SUCH THAT the smaller model produces a good proof.
> Issues - Once again, the continuation problem
>
> I'm having trouble

> Hmmmm this is interesting for sure. It could also be a larger model, but i don't want to complicate it with specifics. Get the subagents to do another round of critiques, similar to before please

## Revised candidate: unspecified, verified HELP

The actor chooses whether and when to request help without knowing P. The
partner chooses and constructs a typed local mathematical object from the
actual context. Only a checked object is installed and then observed by the
actor, which continues. A failed help attempt consumes resources but does not
leave an assumed fact. No human designs the intermediate object or supplies
it to the policy. Both roles receive only the original verified root reward.
Partner model sizes and freezing/co-training are unresolved; avoid making
them defining features of the idea. This differs from the rejected known-P
assumption direction and ordinary backtracking alone, by allowing the learner
to request an unknown mathematical insight rather than prescribe it.

The motivating invariant result is evidence about mathematical content
(27/128 linked nonzero proofs, 0/128 bare and irrelevant controls), not about
a generic help operation; see REPAIRED_LIBRARY_RESULT_2026-11-19.md.
These examples may motivate hypotheses but must not supply the intervention's
training lemmas or select helpful P. Whether actors discover effective
requests and helpers discover useful objects remains untested.

## Independent critique, round two: verified insight collaboration

The same three reviewers independently assessed the revised HELP proposal.

### RL objective and collaboration reviewer

HELP transfers the object-discovery decision from the actor to the partner.
The joint policy may be autonomous and outcome-trained, but the actor can
still receive a supplied stepping stone. Distinguish joint learning from
individual autonomy. The actor's naturally learned role may simply be when
to request help and how to consume a returned object. The partner's role is
what to invent and establish. If both roles train, shared terminal root
reward applies to each actual sampled role action (including unsuccessful
calls); no pseudonegative samples for a partner that was not called, no
separate proof-of-P reward, no selection on successful message. Do not treat
partner text or rendered final proofs as actor-generated actions.

The partner can return P=G or an equivalent reformulation. That gives the
actor an easy finish and can dominate terminal reward. It is valid team
success, not invalid proof or cheating, and prohibiting equivalent answers
would impose a human view of decomposition. A generic finite shared
resource budget limits waste naturally, not a goal-equivalence filter or
help penalty. Allow no call, multiple calls within budget, and no-result
responses. Count all attempts and resources. Diagnose full-solution
outsourcing, repeated/trivial facts, and consumer reliance without making
these reward terms. If the actor cannot improve without the helper, the
system learned division of labor, not the desired individual capability.

Separate fixed partner, same-policy/shared-role parameterization, and
separate co-training; they are different causal variants. A fixed partner
simplifies actor learning but cannot learn to discover useful objects from
terminal reward itself. Joint training admits a learned communication
protocol and changes the actor's observation distribution; the Lean
environment remains indifferent, whereas the partner is part of the
learned joint policy. Larger partner size is not a defining feature; any
extra information/capacity is controlled rather than attributed to RL.

### Lean semantics and native implementation reviewer

Give HELP ordinary native local-declaration semantics. For live goal
m : Γ ⊢ G, partner chooses a well-typed pair (A : Sort u, t : A) in the
exact pre-help context, and environment checks t without introducing any
new assumption, axiom or unresolved metavariable. A local declaration
transition leaves the original target unchanged, adding h with type A:

- `have h : A := t` for local fact/opaque value;
- `let h : A := t` when the actual value must be computationally accessible.

A proposition and its proof is the special case A : Prop; do not
automatically exclude verified witness values, functions, or other
native typed objects. A generic sequence of dependent local declarations
is another possible interface, not preselected. Model chooses object and
binding type; no synthesized invariant or relevance ranking by environment.
Keep exact Lean internal context, local instances and dependencies rather
than reconstructing goals from text. Term elaboration can instantiate
native metavariables: audit and expose such legal changes, never let
unnoticed target/witness changes replace the original goal. Fresh binding
names and session-local scope, no imported facts from other episodes.
An invalid attempt is atomic failure/rollback with cost; no forced
proposal, post-processing correction, automatic useful-P selection, or
hidden retries. Actor observes the resulting native proof state, not a
human-authored explanation. Showing the partner's proof or rationale is a
separate bandwidth choice (could teach by copying; hiding it may starve
learning). For transparent let values, the actual value is necessarily
part of the ordinary state. Keep every role's observation interface fixed
within each contrast. Root proof includes partner's checked term and must
pass unchanged fresh Lean verification with allowed axioms.

### Experimental reviewer

The closest existing work is not just Lean's suffices. [Prover Agent](https://arxiv.org/abs/2506.19923) already uses generated, verified auxiliary
facts/special cases beyond direct subgoals in a multi-model proof search
pipeline. [Bourbaki](https://arxiv.org/abs/2507.02726) uses self-generated
subgoals in evolving proof states and a modular multi-model search system.
[STP](https://arxiv.org/abs/2502.00212) studies mutually improving conjecturer
and prover roles. The basic helper-lemma idea is not new. A candidate
distinction is optional, policy-selected help at arbitrary live states,
partner inventing genuinely unspecified useful checked knowledge, both
roles learning only through original-root success, and measured autonomous
transfer after the partner is removed. Novelty remains unestablished.

A typed fact can also communicate hidden advice (e.g. proposition syntax
encodes a message) or permit private actor/helper conventions via hypothesis
names. It is not mathematically invalid, but it weakens an interpretation
that invariant-like mathematical knowledge caused improvement. Use neutral
fresh names, no extra nonmathematical metadata by default. Diagnose actor
continuation replay with and without P (and with a separately verified
irrelevant fact) under identical context and resources, where replay
is logically well-defined. A failed deletion establishes local dependency,
not semantic novelty or indispensability. Alpha-renaming/partner-swap
robustness is diagnostic, not a training constraint. No semantic filtering
of proposed P, including G itself.

### Reconciled minimal candidate

HELP is a **verified local knowledge request**:

1. Actor chooses when to call, without specifying a missing proposition.
2. Partner sees the authentic proof state and may return any legal typed
   object (or fail/decline), from that state. The choice of actor-history
   visibility also matters: state alone may not reveal the actor's
   internal attempted strategy. Keep this unresolved but explicit; don't
   conceal extra hints or information.
3. Environment validates the object in the pre-help state and installs it
   via ordinary Lean declaration semantics. Nothing assumed for free.
4. Actor continues using, ignoring, or requesting additional knowledge
   as it chooses.
5. Terminal reward only on unchanged verified root proof; all help work
   charged. Both roles are trainable in the joint variant, not necessarily
   in the frozen-partner diagnostic.

The major benefit is precisely that the actor can resume **after the object
is known and established**. There is no need for a wildcard to be used
before its type/content has been determined. The major unresolved problem
is discovery: no design guarantee that a partner finds the right eureka,
or that the actor could not have done it alone. Opposite roles create
different exploration contexts but also potential outsourcing.

Minimal matched comparisons (design only, no decision on model sizes):

| Condition | Mechanism |
|---|---|
| Solo | Equal-budget ordinary interactive terminal RLVR. |
| Direct solver | Same optional HELP and same partner; helper attempts current G directly, not selects an arbitrary new object. |
| Insight partner | Same optional HELP; partner chooses any typed local object to establish. |

First compare these with fixed matched policy identities in a frozen
diagnostic if justified by a registered discovery hypothesis. Equal total
resource accounting and same actor state feedback. Do not infer compound
RL learning from frozen inference. Only a motivating result warrants a
specific prospective learning contrast; frozen vs jointly updated
partner and shared vs distinct weights remain distinct mechanisms.

No-help held-out evaluation is the capacity-building endpoint. A gain
only with help is legitimate cooperative search but not individual
learning. Direct solver matching the insight partner would undermine the
specific claim that new mathematical objects enable discovery. If the
partner chooses G every time, allow and measure this; if that alone accounts
for gains, the insight hypothesis has not earned support. No improvement
does not establish that all collaborative approaches are impossible.

Add to the magic-of-RL rubric: (i) role/accounting sovereignty (distinguish
external helper cognition from actor policy actions), (ii) information
transparency of both roles, (iii) valid no-help/no-result path, (iv) root
only joint credit, (v) honest control for direct outsourcing, (vi) separate
individual unassisted transfer from joint competence. These are
non-compensatory gates, not reward features. The user's larger-model
possibility remains open, not an implementation requirement.

No experiment registered, sampling, proof verification or training launched.

## User idea-dump, verbatim (two propositions and multiple HELP responses)

> Partner gets multiple rollouts per original model, and everything is rewarded at the verrry end.
>
> Okay. Yes, indifferent to which object is produced, yes. And the magic of RL by some terminal reward that doesn't allow for the original model to end up stupid or something, will make that object look like whatever it needs to.:
> "we do not have to define what a Eureka moment consists of mathematically." good. yes.
>
> Also, I like every point. so document all.
>
> 4
> - I think one proposition should be: "developing a great mathematical team".
> - And one proposition should be: Making the original model seriously expand what math and what kind of RLVR gradients were available to it. This may be more difficult. It is a question of exposing it to all types of juice, so like: regular RLVR exposes you to one type of juice; we set up some setup (HELP is just one idea) that exposes the model to EVERY INKLING OF JUICE IN THE ENVIRONMENT WE CAN REACH, AND NOT REACH. So it learns in very unexpected ways.
> This COULD be improved ev en further by us proposing multiple responses per HELP, and either feedng them to the same model, or feeding them to parallel rollouts. I haven't decided yet, but note proposition 1 and 2, and those forks in 2.
>
> Prover agent seems like it doesn't preserve the magic of RL at all. lets not get clouded by that.
>
> Bourbaki - it's undoubted that there's a lot of multi agent RL research. lets not get clouded, we're just trying to design something that captures the magic of RL perfectly. a perfect design just like RLVR is perfect.

## Two independent research propositions (accepted direction, not results)

**Proposition 1 — Developing a great mathematical team.** A joint policy
could discover its own division of mathematical labor, including when to
request assistance, what kind of verified mathematical object to produce
and how to use it. Its success is evaluated by complete, verified original
tasks at honest matched total resources. A team may improve even if the
individual actor does not; that is a legitimate independent research
objective, not a failed team result. Direct solver assistance remains the
important alternative explanation/control for the specific knowledge-sharing
claim.

**Proposition 2 — Expanding the original model's accessible RLVR learning
signal and mathematical capability.** Ordinary rollout RLVR supplies
gradients through the experiences the policy happens to reach. The hypothesis
is that a minimally structured, indifferent environment with optional
verified knowledge interactions could expose it to useful future contexts,
mathematical operations and terminal success/failure contrast that its own
current rollout distribution rarely or never reaches. The ultimate result
sought is much greater *unassisted* mathematical capability, discovered by
the model rather than prescribed by a reward model, authored invariants,
proof targets or intermediate progress metric.

HELP is one candidate way to expand the reachable experience distribution,
not the research proposition itself. We do not define a Eureka object's
mathematical form. A sufficiently general typed-object interface permits the
learner(s) to discover what matters. The user's aspiration to access every
possible bit of gradient signal is a design principle, not a claim that a
finite rollout budget can literally reach every proof state or that every
new interaction yields a useful gradient. The experiment must test whether
the additional reachable experiences actually support autonomous learning.

## Multiple partner rollouts per original actor rollout

User refinement: partner receives multiple rollouts for an original actor
rollout/HELP decision; everything rewarded at the very end. No partner
attempt earns reward merely because its local object is valid. There are
two distinct candidate forks in Proposition 2, explicitly unresolved:

| Fork | Mechanism | Scientific distinction |
|---|---|---|
| Multiple responses in one trajectory | Sample multiple independently proposed/verified objects at a HELP state; actor receives the resulting legal mathematical context and chooses how to use it. | Exposure to simultaneous alternative insights and their possible composition. |
| Parallel continuation rollouts | At the same actor HELP state, fork descendants, each receiving a different independently proposed/verified object and continuing separately. | Counterfactual variation in available mathematical knowledge with a shared pre-HELP history, and possibly richer terminal-success contrast. |

No choice of partner size, number of responses, shared or separate parameters,
frozen versus joint training, or rollout fork is registered. In both forks,
a failed partner response is a charged attempt, and no valid object is
selected by author-rated promise. Native context compatibility and ordinary
scope rules determine which proposed objects can coexist. If independent
proposals are installed together, verify the actual resulting context and
do not silently use another response to justify an independently claimed
object. Reconcile all physical proposals, continuations, failures and tokens;
branching is an explicit compute allocation, not free additional samples.

Particularly for parallel continuations, sibling rollouts share prior history
and are not independent examples. Credit must use probabilities of actual
sampled actor and partner actions under their actual conditioning contexts.
Shared-prefix accounting, attribution of terminal returns to the sampled
branches and the GRPO grouping/normalization semantics need a deliberate
design; neither copy a successful sibling reward onto a failed child nor
pretend all repeated shared actions constituted independent proposals.
Do not introduce a per-P correctness reward to solve credit assignment.
These are trainer design constraints, not a selected implementation.

There is an unresolved tension: the team terminal reward by itself does not
guarantee individual capability (outsourcing may be optimal). Proposition 2
therefore needs an autonomous no-HELP evaluation and perhaps a different
terminal task arrangement, not an intermediate supervision signal or a
requirement to discover specific propositions. No such arrangement is
selected yet. Distinguish an autonomous learning result from a useful
collaborative system rather than defining one away by the other.

## Literature stance

The user explicitly does not want related multi-agent work to dictate the
design. The earlier Prover Agent/Bourbaki references remain recorded as
context, not recipes or reasons to reject this idea. Aim for a clean
environment/terminal objective that meets the magic-of-RL rubric on its own
terms, then separately evaluate related work and novelty when the mechanism
is clear. The user accepts the substance of the second critique round and
wants it all retained. No training or experiments launched.

## Independent critique, round three: multiple partner rollouts and learning-signal access

User requested another critique of both independent propositions and both
multiple-response forks. The three reviewers reached independent conclusions
below. No implementation or registered run is selected.

### Reviewer A: terminal outcome and credit assignment

The central ambiguity is the unit of terminal success. A shared prefix followed
by K alternatives is not K independently sampled complete episodes. It can be
a single joint search episode, or a sample of K conditional proof policies.
Both are legitimate but the objectives, policy gradients, and interpretation
differ. Do not choose the accounting that produces a larger apparent gradient
after seeing results.

**Bundle/union.** K helper attempts are actually sampled; all legally verified
objects are exposed in the same continuation, with no author-rated relevance
filter. One completed root yields one terminal reward R. For a frozen helper,
its objects/tokens are observations, not actor action tokens. For a trainable
helper, include sampled helper action logprobs in the joint episode objective.
All invalid attempts and verification work cost resources, regardless of root
outcome. Root-level credit can be noisy, especially for unused responses, but
per-object reward would be a different objective.

**Alternative branches.** Let a single sampled actor prefix x (including HELP)
produce K conditionally independent continuations, root verdicts R_i ∈ {0,1}.
Two plausible terminal objectives:

- Team search succeeds if any valid root closes: R_OR = max_i R_i. This
  is a joint terminal episode reward for an entire search policy, not the
  correctness flag of each individual proof. The common prefix is scored
  once; every sampled branch action belongs to the joint search episode.
  Broadcasting R_OR as the *proof verdict* of every failed child is false.
  Reinforcing only the winner, while ignoring failed samples/cost, is also
  not the joint sampled-trajectory objective.
- Expected branch closure: R_mean = (sum_i R_i)/K, prefix scored once
  weighted by R_mean; for independent children, child i's score gradient
  weighted by R_i/K. This remains outcome-only, but it is not the same
  objective as best-of-K search. Do not silently substitute one for the other.

For independent branches, a variance-reducing baseline for the OR objective
can subtract R_{-i} (whether another sibling solved), giving marginal
unique-rescue credit R_OR-R_{-i}. It is a legitimate action-independent
baseline only under the specified conditional independence; it gives zero
credit to each redundant success and is not recommended as the first
implementation. If branches communicate, these independence formulas do not
apply. The clean starting candidate is explicit joint episode terminal return.

**Critical GRPO issue:** if the K children of one sampled HELP prefix form the
entire GRPO group, centered group advantages sum to zero. Under equal-weight
score gradients at the sampled policy, sum_i A_i ∇log π(x)=0. Learning what
to do after HELP may remain possible, but the shared decision to ask for
help gets no direct group-relative gradient. Treating shared prefixes as K
independent actions creates pseudoreplication. Instead group independently
sampled original-theorem episodes, explicitly account their internal branching
and chronological sampled actions. Verify the actual implementation (token
weighting, clipping, KL, masks, prefixes, variable budgets) rather than assume
this idealized cancellation identity always holds unchanged in every trainer.

A higher helped success rate can also saturate relative rewards (all-success
GRPO groups), eliminating contrast. Mixed groups can increase because partner
luck, not actor decisions, determines the outcome. More nonzero gradient is
not automatically more useful mathematical learning. No trainer can guarantee
actor competence under pure joint-success reward: direct delegation of G can
be optimal for the team. Evaluate propositions separately.

### Reviewer B: Lean semantics, multiple responses and branch independence

Freeze authentic state S (goal identities, contexts, local instances, mvar
assignments, imports/options). Sample K helper trials from S without seeing
siblings, unless sequential cooperation is explicitly chosen instead. Each
returned object is checked in the same pre-help S (with its own native
dependent local sequence, if that is the declared response interface).
Every invalid/trivial/duplicate attempt is counted.

- **Union/bundle:** install all independently checked objects via native
  local bindings in an output-independent order, e.g. trial index. Actual
  assembled context must reverify; incompatible native metavariable
  assignments (e.g., distinct witness values for the same open existential)
  may not be merged by string manipulation or silently resolved by ranking.
  A failed snapshot attempt rolls back exactly. Extra facts can change
  simp/typeclass resolution and context length even when actor never names
  them, so implicit availability is a substantive affordance. Bundle
  permits genuine mathematical composition.
- **Object pool (additional unresolved variant):** expose checked objects
  with neutral identifiers; actor optionally chooses which to install as
  ordinary native bindings. This provides more control of context and use,
  but adds a selection action and observation interface. Not identical to
  automatic union, not selected by user.
- **Branches:** clone S per trial, install only its result, continue from
  each independently (invalid help gives unchanged state/failure according
  to declared generic interface). No facts, native constraints or future
  observations from sibling branches can cross implicitly. Each proof must
  replay against actual original target and allowed axioms.

Keep actual context and dependent local identities, not pretty-printed
goal matching, no global declarations/cache, no proof-strength change.
For a pool, use valid-native compatibility at installation; do not
silently discard disfavored objects or make a heuristic semantic-dedup
filter. Preserve trial order, duplicate/failure logs, whole-episode
resources including shared-prefix physical savings and per-branch continuation
work. Parallel latency is not a free increase in generated model/verifier
compute. Native type/scope/compatibility restrictions are required by
logical validity, not experimenter beliefs about good mathematics.

### Reviewer C: falsifiability of the two propositions

The hypotheses are different:

- H-team: final verified roots per matched total resources improve beyond
  direct solver and ordinary resampling/search controls. A legitimate result
  even if no one learns independent proving.
- H-learning: the actor receives richer effective outcome contrasts than
  matched baseline and improves tool-free proving on unseen theorem families.
  Nonzero advantages, conditional state novelty, and root performance are
  diagnostic evidence, not intermediate training rewards.

With K attempts, any-success automatically increases for an independent
per-attempt success q as 1-(1-q)^K. Do not use this arithmetic effect as
evidence of mathematical insight. Essential controls: same total actor+helper
resources, K direct continuations of actual G with identical helper,
ordinary forward resampling/backtracking at matched budget. Compare
pretrained/frozen assisted performance to later policy improvement. A
shared-prefix paired diagnostic can compare K objects, bundle, branches, and
ordinary no-help continuations from the same actor state with predeclared
budgets; do not assume naturally selected HELP states are causally
comparable to unselected states. K and per-path length cannot both be
arbitrarily held fixed if total work changes; declare budget regime honestly.

Gradient-access audit by role and phase: actual sampled pre-HELP
actions, HELP decision, post-HELP continuation, helper tokens (only if
trainable); independent root/group count, mixed binary outcome group rate,
nonzero advantages/trainable action tokens, prefix multiplicity, context
length, action/logprob provenance, KL/loss weighting, effective return
variance and cost. Hold a sampled actor prefix fixed and vary partner
responses to measure partner-dependent reward variation, and compare
distinct sampled prefixes to diagnose genuine actor-action signal versus
helper lottery. This is not a complete causal variance decomposition
without a defined sampling design. Do not equate reward contrast with
novel mathematical knowledge or use these diagnostics to shape training.

For bundle: if a verified continuation relies locally on two or more
independently proposed objects under separate single-fact omission replays,
that is evidence of realized composition (not necessity in all proofs).
For branches: different outcomes under identical-root prefixes offer
conditional opportunities, not proof that actors learned new math. Replay
unchanged continuations with/without the object, or use independently
verified neutral-context controls, only as diagnostic comparisons, never
reward or author selection. Direct target solve/trivial objects allowed,
diagnosed not banned.

Tool-free held-out evaluation must use normal Lean and ordinary available
tactics, identical proposal/token budgets, no helper retrieval/context
caches/proofs, and novel theorem families, not solely handcrafted variants.

### Reconciled additional requirements

1. Decide the terminal unit and objective (OR joint search vs expected
   individual branch closure) explicitly before trainer implementation.
2. Preserve independent original rollout groups for GRPO, correct shared
   action accounting, and actual on-policy sampled token provenance.
3. Separate mathematical validity (whether a fact can be introduced) from
   terminal usefulness (whether the actual root closes) and individual
   learning (whether the actor subsequently proves independently).
4. Native snapshot and exact-context semantics; no hidden sibling sharing,
   ranking, invalid witness merge or pruning.
5. Preserve no-HELP, failed-HELP and all-zero/all-one groups under baseline
   treatment; do not inject artificial reward contrast or free replacement
   attempts when an episode produces no usable group signal.
6. Match aggregate resource cost, direct-solving and resampling, and
   independently audit each objective's diagnostic claims.
7. Evaluate actor/tool-free and team/assisted outcomes separately. Team
   progress need not be dismissed because the actor does not improve;
   likewise team progress cannot establish H-learning.

No model size, K, update schedule, fork or loss formulation selected. An
informative next step would be a frozen discovery test before training only
after registering a discriminating hypothesis, and an exact small synthetic
trajectory accounting test for any chosen trainer before GPU use.

## Critical decision map

| Result | Interpretation |
|---|---|
| HELP equals matched direct solver/retries | No support for new object-specific teamwork beyond inference. |
| Team gain, no extra informative actor credit | Collaborative inference supported; gradient-access mechanism unsupported. |
| More mixed terminal outcomes, no tool-free gain | Richer sampled reward contrast established, useful autonomous learning unproven. |
| Team gain and tool-free gain over matched ordinary RL and direct help | Strongest evidence for both propositions; still examine how new contexts drive transfer. |
| Only tool-free gain | Support for learning signal, not necessarily a better deployed team. |
| Bundle wins with controlled local dependency on multiple facts | Evidence of composition of independent discoveries in those traces. |
| Branch wins at matched budget | Evidence for alternative-context exploration, not necessarily compositional reasoning. |

The user wants the design judged against the terminal-only RLVR principle,
not automatically shaped by existing multi-agent literature. The critiques
do not establish the proposed mechanism's novelty or effectiveness.
No model proposals, verification, training or experiment were run.
