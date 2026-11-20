# Repaired invariants unlock 27 dependent nonzero proofs

One newly sampled consumer continuation is just:

```lean
  contrapose h
  simp_all
```

It closes a previously unsuccessful nonzero task when the local context contains
the checked invariant produced by a repaired base-model proof. The exact same
continuation fails with the useful fact removed or replaced by a valid reflexive
identity. The producer and consumer together form a closed kernel-checked proof;
the consumer never sees the prerequisite proof's implementation.

Across the fixed experiment there are **27 linked successes, all dependent on
the useful fact under both replay controls**. Bare and irrelevant-fact generation
produce zero successes. All linked successes are nonzero proofs; witness tasks
remain unsuccessful. This establishes one usable prerequisite-to-consumer edge,
not the registered two-schema outcome or a learned training paradigm.

## Complete result

| Consumer root | Bare / 32 | Linked / 32 | Irrelevant / 32 |
|---|---:|---:|---:|
| Nonzero variant 0 (`pt_04`) | 0 | 5 | 0 |
| Nonzero variant 1 (`pt_05`) | 0 | 12 | 0 |
| Nonzero variant 2 (`pt_06`) | 0 | 3 | 0 |
| Nonzero variant 3 (`pt_07`) | 0 | 7 | 0 |
| Witness variant 0 (`pt_08`) | 0 | 0 | 0 |
| Witness variant 1 (`pt_09`) | 0 | 0 | 0 |
| Witness variant 2 (`pt_10`) | 0 | 0 | 0 |
| Witness variant 3 (`pt_11`) | 0 | 0 | 0 |

Each condition receives 256 proposals: linked succeeds on 27/256 overall,
including 27/128 nonzero proposals; bare and irrelevant are each 0/256. These
are finite-budget observations, not impossibility claims. Only `pt_05` meets
the registered 8/32-versus-at-most-1/32 root criterion. No witness root qualifies,
so the registered requirement of a root in both schemas is **false**.

All 27 accepted linked continuations were replayed unchanged under both control
prefixes: 54 logical ablations, all rejected, through 44 distinct extra sources.
The first illustrative continuation above does not even explicitly name the
library fact; its success depends on what simplification can derive from the
context. This is more specific than checking for a library identifier in text.

## Provenance and limits

The first accepted repaired producer per variant was fixed before consumer
sampling. Only the recursive function identifier is renamed. Producer and
consumer recursive definitions match byte-for-byte under that rename. The
consumer sees the external theorem type and a typed local instantiation; the
verifier receives the complete repaired prerequisite proof. The irrelevant
library provides a reflexive determinant equality, not the initial/output link.

**The original benchmark authored the invariant statements.** The model supplied
unsuccessful proof bodies; a human-specified scope repair made them valid. This
experiment does not show that the model invented the invariant, independently
discovered the repair, or learned a reusable internal representation. All eight
consumer roots have been inspected. There are no parameter updates, no new
held-out result and no evidence yet that success persists when the scaffold is
removed. Four coefficient variants of one schema are not four independent
generalization domains.

The informative and irrelevant prompts are not token-identical. Both expose a
checked interface and use the same local-fact name; the irrelevant equality is
longer. Prompt lengths, exact tokens and all generated outputs are archived.
Proposal and output-token capacities are matched across conditions. Useful
mathematical information is the deliberate intervention.

## Validation and accounting

All sixteen transferred/irrelevant library theorems accept. All twenty-four
unfinished consumer prefixes reject with only unfinished-goal/parser-end errors,
and the saved Lean contexts contain the expected typed local fact. Two invalid
proof controls reject. No prefix already solves its consumer.

All **768** proposals completed, followed by **607** distinct primary full-source
checks and **44** extra ablation checks. No verdict is missing or unresolved.
The separate audit reconstructs producer selection, exact definition/proof
renames, hidden implementation boundary, full consumer sources, sampling seeds,
all cells, every dependency replay and the outcome criterion. It passes.

Job **1373856**, one H100 on `trig0038` under `def-zhijing`, released its allocation
after **20m13s**. The controller used frozen source commit `fde13f1`, pristine
DeepSeek-Prover-V1.5-SFT 7B weights, float32 Transformers SDPA, and the registered
seed/budget. Full-source caching never uses tactic labels as correctness evidence.

## Next decision

Do not turn this partial success into passage of the two-schema criterion or
the earlier scope-repair training gate. Do not resample the witness roots to
chase a threshold. The unresolved boundary is now concrete: the checked invariant
supports nonzero reasoning, but the model does not construct the witness from it.

A previously verified base sample on the local witness bank contains
`exact ⟨w, -z, by linarith⟩` (`base/witness_2/15` in the fresh policy-update batch).
Thus there is an existing constructor procedure to investigate, not a reason to
assume that the primitive is absent. A separately registered next mechanism can
test typed composition of that procedure with the repaired invariant. Any later
learning study needs fresh tasks, same-information controls, and evaluation
with the entire library removed. The broader research goal remains unachieved.

## Recovery

Compact analysis, audit, launch/accounting receipts and complete producer/consumer
proof chains are under `research/experiments/repaired_library_20261119/`.
The separate release archive contains every proposal, all exact source/verdict
pairs and dependency replays, frozen execution source, panel and prerequisite
provenance. Its inventory and downloaded checksum-verification receipt are
tracked with those compact results.
