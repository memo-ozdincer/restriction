# Typed composition of two existing model procedures

## Expected interesting result, registered before execution

A bounded search over types closes all four witness roots by joining the repaired
recursive invariant with the base model's existing local Bezout constructor.
These roots had zero free-form successes even with the useful invariant exposed.
The constructor sample is `base/witness_2/15`, whose unchanged body is
`exact ⟨w, -z, by linarith⟩`. No new witness body or model sample is supplied.

This tests whether the missing operation is connecting available procedures by
their types. It is a compiler capability on inspected examples, not a new learned
capability. The mathematical statements came from the benchmark; invariant scope
repair, library selection and search algorithm are human-specified. Existing
automation and equality transitivity are additional supplied capabilities.

## Fixed experiment

Use the four linked records pt_08 through pt_11 in the authenticated D-133 panel.
Preserve their recursive definitions, original target statements and repaired
prerequisite bodies. Extract the local constructor statement and body directly
from the saved fresh policy-update trajectory; rename only its theorem name.

Remove the manually materialized `hbridge` prefix. The full consumer gets only
the closed library declarations and its original theorem context. Run the same
bounded tactic `solve_by_elim (maxDepth := 4) only [...]`, with available library
names, `Eq.trans`, and the original initial-determinant hypothesis `h`.
Lean performs parameter unification; the driver supplies no witness expressions
or intermediate equality. Freeze depth four, with no retry or depth tuning.

For each root run four search conditions: both components; constructor only;
invariant only; constructor plus the already validated reflexive irrelevant
contract. Remove unavailable component names from the search list so failures
are ordinary unsolved proofs, not unknown identifiers.

Also check one fixed explicitly wired term per root, using the two components
and equality transitivity. These four diagnostics distinguish search failure
from inability to compose the types; they do not count as search successes.
Recheck the original constructor alone and one invalid proof control.
Total: 22 complete Lean checks, no GPU, no fresh sampling, no parameter updates.
Use the unchanged pinned verifier and final theorem axiom audit.

The registered positive outcome requires all four both-component search proofs
to accept, all twelve search controls to reject, all four explicitly wired terms
to accept, the original constructor to accept, the invalid control to reject,
and every check to resolve. Save every source, verdict, input hash and full proof.

## Decision boundary

Success establishes verified composition of existing components, with the
search and library supplied externally. It does not establish autonomous
discovery, novelty of theorem search, task generalization or training benefit.
It cannot pass the earlier two-schema sampling or repair-training gates.
Failure is reported at the fixed search bound without tuning this panel.

A positive result can motivate a separately designed learning experiment:
whether compiling failed root attempts into verified component graphs yields
useful training data, with same-information replay controls and fresh
scaffold-free evaluation. Do not train on these inspected roots and call it
held-out improvement.

## Pinned-runtime correction before interpreting results

The first attempt is preserved in `runs/typed-procedure-composition-20261119`.
Sixteen checks had verifier subprocess errors, five returned the unsupported
configuration syntax error, and one explicit wiring check accepted. This is
not a completed scientific outcome. Lean 4.9-rc1 requires
`solve_by_elim (config := {maxDepth := 4}) only [...]`; the original shorthand
was invalid. Correct only that syntax, preserving depth, lemma order and cases.

Lake also re-cloned ImportGraph and removed its compiled package. Direct Lean
reported `unknown package 'ImportGraph'`; the REPL omitted that import error
and returned misleading downstream namespace/parser errors. Restore ImportGraph
at its already pinned revision `7983e959f8f4a79313215720de3ef1eca2d6d474` using
`lake build ImportGraph`, without changing the verifier or dependency versions.
Run checks sequentially to avoid concurrent Lake package mutation. Strengthen
this driver's warmup to require imported arithmetic syntax, BigOperators and
`ring`, since `True`/`trivial` alone could pass after an import failure. Preserve
all initial sources and errors. Re-freeze a new run before execution.
