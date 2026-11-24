# A failed sampled program supplies eight verified constructors through contract transport

> Interface qualification (November 24): the standalone C1 experiments used a
> leading BOS marker and omitted C1's trained proof-boundary BOS. Recorded counts
> remain valid under those prompts; they do not establish native-interface
> capability limits. See the [confirmed audit and controlled comparison](../../PROMPT_BOUNDARY_2026-11-24.md).

One unchanged sampled function now supplies a valid constructor for every one of
the eight inspected target specifications. The compiler infers argument bindings
from contracts, proves the transformation using the abstract source contract,
and separately checks each executable wrapper. **All eight transformations pass
both checks.** No model sampling or parameter updates occur in this experiment.

The original sampled function is:

```lean
fun d a b x y => (a * x - d * b * y, b * x + a * y)
```

It fails the original norm x²-d*y² but its unchanged complete proof verifies for
x²+d*y². Instantiating that verified program at `-d` gives the missing original
constructor: mathematically `(a*x+d*b*y, b*x+a*y)`. The compiler does not edit the
function body. It solves a polynomial coefficient identity in the specifications.
The [original-sign executable proof](proofs/original_-1_executable.lean) and
[proof using the abstract source contract](proofs/original_-1_logical.lean)
make the distinction inspectable.

| Target norm coefficient | Inferred source argument |
|---|---|
| ±d | ±d |
| ±rho, all variables renamed | ±rho |
| ±2d | ±2d |
| ±(d²+1) | ±(d²+1) |

The source parameter ranges over all integers, so negative substitutions are
legitimate. Each resulting function satisfies the entire universal norm-product
contract and both basis laws, not merely a few evaluated inputs.

## Controls and retained first attempt

| Check | First attempt | Final attempt | Expected |
|---|---:|---:|---:|
| Abstract-contract transport | 7/8 | 8/8 | 8/8 |
| Executable wrapper | 8/8 | 8/8 | 8/8 |
| Identity binding | 2/8 | 2/8 | 2/8 |
| Wrong-sign binding | 0/8 | 0/8 | 0/8 |
| Valid source / invalid zero source | accept / reject | accept / reject | accept / reject |

Both attempts have 34 unique executed Lean judgments and no unresolved result:
68 executed checks total. The first overall criterion fails because the
nonlinear positive logical certificate stops at `True ∨ b = 0`. One final `simp`
was appended uniformly to the basis-law proof template, including controls.
No target-specific proof branch, function edit, changed binding, new source
selection or expanded search language was introduced. Inputs, provenance and
binding plans are byte-identical across attempts. Both independent audits pass;
the final experiment criterion passes.

First execution: commit `6595ac7f633fa765dae46de1dd4ed64a96825d0a`, 71.716 seconds.
Final execution: commit `d2f56304d958ab6186d4f9004960e53735d8c07a`, 58.605 seconds.
These are measured CPU driver durations, excluding independent audit and
publication. Four verifier workers were used. No GPU was allocated.

## What this establishes

Verified hindsight programs can supply target-valid demonstrations through an
automatically inferred constructive connection between contracts. Here that
connection supplies successes where the previous unchanged C1, hindsight replay
and context-contrast training did not solve the original-sign targets.

These are compiler successes, not model successes. The contract family,
degree-at-most-two substitution language and proof templates are researcher
supplied; all eight target specifications were already inspected. This is one
mathematical family, not unrestricted law discovery or general program synthesis.
The earlier model pass counts and failed criteria remain unchanged. Substitution
and theorem instantiation are established techniques; this result alone is not
a novel training paradigm. Its next question is whether compiler-generated
experience teaches construction that survives removal of the compiler.

The [frozen protocol](../../CONTRACT_TRANSPORT_2026-11-24.md), complete
[plans](plans.json), [independent audit](independent-audit.json) and all sixteen
accepted transport proofs are tracked here. The archive inventory includes both
complete runs, all verdicts, frozen sources, the original 128-response bank,
selected hindsight responses, target specifications and C1 parent identity.
Bulk model weights are excluded. The [hindsight-contracts release](https://github.com/memo-ozdincer/restriction/releases/tag/hindsight-contracts-2026-11-24)
now includes `contract-transport-20261124.tar.gz` and `transport-inventory.json`.
A fresh download verifies the archive and all 35 members; the
[publication receipt](publication.json) records that check. Archive SHA-256:
`8a59f219a27d94e54a4bc33e62700400a99dbc83299917d90ed055e6303756a2`.
