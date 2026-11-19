# Hoped-for result: making an existing fact local unlocks proof completion

Registered after the base consumer's oracle results, before any sample from
this follow-up. The original four targets and models remain fixed. Base has
0/32 on each oracle-assisted target despite some completions mentioning the
lemma; its quadratic2 Bezout completions often choose incorrect coefficients.
This motivates a specific interface question, not another seed sweep.

**Hypothesis:** a frozen consumer can finish proofs using the same supplied
invariant when a deterministic adapter places it in the local proof context.
Append exactly `  have h := reusable_fact n\n` to the existing consumer prefix.
Keep the full global declaration and proof, target, model, temperature, seed,
sampling budget, generation limit, parser, and Lean verifier unchanged. This
adds an invocation, not a mathematical witness, coefficients, or target proof.
It is still an intervention supplying an extra proof step and changes the
conditioning prefix; it is not free compute or newly learned mathematics.

Use both original consumers, all four targets, and both original oracle and
irrelevant `n=n` conditions, 32 completions each: 512 proposals maximum.
Keep the original request IDs to preserve request-specific seeds. The two
arms receive the identical invocation prefix; only the already-existing lemma
differs. Compare against the complete original oracle/irrelevant results.
No model-produced artifacts, new producers, target replacements, parameter
updates, extra seeds, or new allocation. Full raw results will be preserved.

The interesting descriptive artifact is a target with 0/32 global-oracle
successes, at least 4/32 local-oracle successes, and at most 1/32 local-irrelevant
successes, with no missing verdicts or resource errors. Publish the entire
matrix regardless. This threshold identifies a candidate interface bottleneck;
it is not a significance test or evidence of a new training paradigm. Failure
means this simple adapter did not resolve consumer execution.

Run only after the original experiment completes, within job 1360929's existing
one-hour H100 allocation. Leave two minutes before allocation expiry, require
at least eight minutes remaining to start, and preserve partial outputs on
deadline failure. No automatic renewal. Registration and execution source must
be snapshotted before the first follow-up generation.
