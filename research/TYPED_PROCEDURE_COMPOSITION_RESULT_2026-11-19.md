# The procedures compose, but fixed-depth search does not find the connection

Four complete witness proofs now check using two existing components: the
repaired model invariant and the base model's previously sampled local witness
constructor. The manually specified connection is the same term in all four:

```lean
exact witness_constructor _ _ _ _ (Eq.trans (linked_contract n a b c d) h)
```

The constructor's original body is unchanged:

```lean
exact ⟨w, -z, by linarith⟩
```

Lean infers its four integer arguments from the invariant application and the
consumer goal. The supplied connection explicitly chooses the prerequisite,
its inputs and equality transitivity. This is a checked composition of available
procedures, not spontaneous model generation or automatic discovery.

The registered bounded search **does not** find these connections. All four
both-component searches fail at the fixed depth of four. No depth tuning or
additional sampling was performed.

| Check | Accepted / checked |
| --- | ---: |
| Both components, bounded search | 0 / 4 |
| Constructor only, bounded search | 0 / 4 |
| Invariant only, bounded search | 0 / 4 |
| Irrelevant invariant plus constructor, bounded search | 0 / 4 |
| Explicitly connected components | 4 / 4 |
| Original constructor recheck | 1 / 1 |
| Invalid proof control | 0 / 1 |

All 22 corrected checks resolve with no system errors. The independent audit
reconstructs every complete source, verifies the constructor's original sampled
trajectory and prior local correctness, checks every axiom audit, and reproduces
the result. **The registered positive outcome is false.** Because both-component
search fails, failed search controls do not establish a successful search's
dependence on either component.

## Scope and next decision

The preceding repaired-library experiment had 0/128 linked witness samples;
the five-policy pilot also had zero successes on these original witness roots.
The new explicit proofs show that missing root samples did not imply absence of
all useful component procedures. They do not give a matched pass-rate comparison:
the compiler received selected verified components and a manually supplied
connection. All four roots are inspected coefficient variants of one schema.
The original theorem statements are benchmark-authored; the invariant requires
a human-specified scope repair. No training or new model sampling occurred.

This does not establish a new theorem-search method or training paradigm, pass
the earlier two-schema gates, or justify scaling the current search. The next
useful question is what prevents the fixed search from recovering the known
checked connection. Diagnose its actual proof-state trace before selecting a
new search representation or training intervention; do not infer the cause from
the failure count or tune this panel until it passes. A learning study would
need fresh tasks, identical information in its controls, and evaluation with
the procedure library and connection supplied by the model itself or removed.

## Preserved runtime failure

The first attempt is retained separately. It had sixteen verifier subprocess
errors, five unsupported configuration-syntax errors and one accepted explicit
term; it is not a valid aggregate result. Pinned Lean 4.9-rc1 requires
`solve_by_elim (config := {maxDepth := 4})`. The correction preserves depth,
lemma order, cases and the outcome criterion.

Lake also re-cloned ImportGraph at its pinned revision and removed compiled
files. Direct Lean exposed the missing package; the REPL suppressed that import
error and reported downstream errors. Rebuilding the same pinned dependency,
using one verifier worker, and requiring arithmetic imports in warmup restored
execution. The verifier source and correctness predicate were unchanged.
Initial source commit: `2818864`; corrected frozen execution: `856346f`.
No GPU allocation was used for either attempt.

## Recovery

Compact analysis, audit, runtime receipts and all four complete Lean proof
chains are in `research/experiments/typed_procedure_composition_20261119/`.
The separate evidence archive preserves both attempts, every source and verdict,
the original constructor trajectory and correctness records, input panel,
frozen first driver and current execution/audit sources. Its tracked inventory
and downloaded verification receipt identify the published payload.

[Complete evidence release](https://github.com/memo-ozdincer/restriction/releases/tag/typed-composition-2026-11-19):
157,719 compressed bytes, 33 files, 1,480,697 logical bytes. Downloaded archive
and every member verified. SHA-256:
`d5c9340b0412123a19185d14a32700755408c5f2b3a1fab9ac563d1e8d4e71a6`.
