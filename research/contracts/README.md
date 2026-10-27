# Closed atomic contract instrument

This CPU-only instrument checks a training-permitted **single integer row
shear**. Its hypothesis, stated in the runner before each check, is that Lean
can accept the closed contract and a premise-consuming adapter while rejecting
incompatible interfaces, missing premises, admissions, and new axioms. This is
an engineering feasibility result, not evidence of model learning.

`AtomicShear.lean` supplies the closed telescope `a b c d k : ℤ`, unconditional
initiation (`P = True`, elided), and output

```lean
(a + k * c) * d - (b + k * d) * c = a * d - b * c
```

The frame is one already closed theorem, with no external goal or open local
context. The adapter explicitly takes this output and the premise
`a * d - b * c = target`, then produces the updated determinant's equality to
`target`. Its elaborated proof uses both input facts. This establishes use by
this witness, not necessity for every possible proof. The two incompatible
interface cases also have closed impossibility certificates, using the zero
registers as a counterexample; rejection is not merely a weak tactic failing.

`ClosedAudit.lean` reads elaborated declarations. Its JSON preserves the full
closed type expression, dependent binder structure, binder info, local let
values, and universe structure. Binder names and expression metadata are
erased; binders are represented by Lean's bound-variable indices. No regex
extracts binders. The generated `alpha_interface_sha256` identifies that
canonical syntax in the recorded environment, **not arbitrary semantic
equivalence**. A separate kernel definitional-equality query checks the three
declared comparisons and treats kernel errors as errors.

The certificate must be a fully elaborated theorem with no free variables,
loose bound variables, or metavariables in its type or proof. Lean compilation
kernel-checks the new theorem; the audit then traverses its transitive axiom
dependencies. The only allowed axioms are `propext`, `Classical.choice`, and
`Quot.sound`. Imported oleans are trusted as in the pinned production runtime;
this does not recheck the entire Mathlib library from source. No historical
verifier, correctness signal, model, reward, or scheduler is changed.

Run from the repository, choosing a new output directory:

```bash
../environment/venv/bin/python scripts/project/check_procedure_contracts.py \
  --output ../runs/procedure-contract-check-NEW

PROCEDURE_CONTRACT_RUN="$PWD/../runs/procedure-contract-check-NEW" \
  ../environment/venv/bin/python -m unittest tests.test_procedure_contracts -v
```

The run contains exact generated Lean sources, stdout/stderr, positive olean,
source/toolchain/checker hashes, git/environment metadata, elapsed time, and
machine-readable interfaces/results. Existing directories are refused. A
timeout kills the entire lake/Lean process group. No negative case is accepted
as evidence unless the positive audit passes first.

Only explicit closed lemma certificates are supported. Arbitrary `have`
extraction, shared-metavariable cuts, multiple focused goals, and polymorphic
interface comparison are unsupported. The toolchain/manifest provenance does
not hash every transitive olean. This does not establish a general semantic
contract ID, a complete training bank, or end-to-end procedure transfer.

No frozen transfer tasks or witnesses are read. There is no iteration,
nonzero-row target, Bezout construction, rational recurrence, or equivalent
held-out multi-edge graph. Rational and fixed-coefficient variants here are
only interface-identity fixtures for the same one-step atomic identity.
