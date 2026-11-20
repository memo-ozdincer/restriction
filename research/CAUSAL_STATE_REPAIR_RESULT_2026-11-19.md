# One scope correction repairs 43 previously unsuccessful model proofs

This exact base-model continuation failed:

```lean
  induction n <;> simp_all [op_00]
  <;> ring_nf
  <;> linarith
```

Changing only its first line produces a complete, kernel-accepted proof:

```lean
  induction n generalizing a b c d <;> simp_all [op_00]
  <;> ring_nf
  <;> linarith
```

Every remaining byte is identical. The correction quantifies the induction
hypothesis over the four state registers, so the same hypothesis can apply to
the changed registers in the recursive call. It supplies no new invariant,
algebraic lemma or witness. The structural repair rule is human specified.

## Complete registered screen

The fixed input is all 256 pristine-base samples from the sixteen original
composition roots in job 1373310. All were previously rejected with resolved
Lean verdicts. Exactly 201 have supported, unambiguous induction syntax. The
other 55 are recorded as ineligible: 52 lack a matching induction, two use
unsupported primed case-binder syntax, and one already generalizes variables.
None were selectively retried or replaced.

| Original root | Original correct / 16 | Scope-repaired correct / 16 |
|---|---:|---:|
| Integer invariant, variant 0 | 0 | 12 |
| Integer invariant, variant 1 | 0 | 9 |
| Integer invariant, variant 2 | 0 | 10 |
| Integer invariant, variant 3 | 0 | 12 |
| Other twelve roots combined | 0 / 192 | 0 / 192 |

There are **43 repaired successes among the 64 invariant attempts** (67.1875%),
43/201 among applicable edits, and 43/256 over the full fixed source pool.
They span four variants of **one** authored schema. There are 38 distinct
repaired proof-body strings; this is not a count of semantic strategies.

For every accepted repair, remove each of the four newly generalized state
variables in turn. **All 172 logical omission controls reject**. This establishes
local necessity of each addition for these exact continuations under these
checks, not that every possible invariant proof must use all four variables.

All results are resolved: 189 distinct primary full-source Lean checks and 152
distinct ablation checks, with no system errors. Identical complete sources alone
are cached. The checker retains its original 60-second timeout and axiom audit.
A separately logged import warmup is additional compute. The primary/ablation
phase took 302.9 seconds. No new model sample, parameter update or GPU allocation
was used. An independent audit reconstructs original rejections, scope-only
edits, accepted source hashes, all omission controls and the outcome gate.

## What this changes

The previous four-arm training pilot failed on every original composition root.
This screen identifies a much more specific obstacle within one family: many
generated continuations already form valid proofs when an earlier state-binding
decision is repaired. The rest of their induction/algebra program need not be
replaced. This supports studying causal credit for structural decisions and
repair of attempted methods, rather than continuing the length-confounded reward.

It does **not** establish that a newly prompted model would regenerate those
continuations, that the model learned state lifting, or that the capability
survives removal of the repair. The inputs are inspected, post-hoc examples;
the compiler supplies additional structural knowledge and verifier work. This
is a controlled within-proof intervention, not held-out generalization.

The registered training-feasibility gate requires successful repairs in at least
two target schemas. It **does not pass**: nonzero, witness and rational proofs
remain unsuccessful. Do not start the planned broad repair-training study on
the strength of these four correlated invariant variants. The next substantive
question is whether the now-verified invariant procedures can become usable
intermediate constructions for the other tasks. That would test composition of
repaired prerequisites, a different mechanism requiring its own matched controls
and prospective design. Do not resample this panel to turn its gate positive.

The full research objective remains active. This is a concrete example of a
repairable weak strategy, not a revolutionary training paradigm.

## Evidence and recovery

The source is registered in commit `190f910`; the frozen manifest hash is
`1a567259464d13e382a429db373ae0f262ed1c4b6431e4e6ea22700b10f97a1f`.
Compact analysis, audit, and original/repaired standalone proofs for the first
success on each root are in `research/experiments/causal_state_repair_20261119/`.
The separate release archive preserves all 256 source records, primary/ablation
sources and verdicts, execution source, and the exact original evidence needed
by the independent audit. Its inventory and downloaded verification receipt are
stored alongside the compact report.
