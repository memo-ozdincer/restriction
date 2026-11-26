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
