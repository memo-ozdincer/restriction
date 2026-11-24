# Closure learning produces two isolated transfer examples

> Interface qualification (November 24): the standalone C1 experiments used a
> leading BOS marker and omitted C1's trained proof-boundary BOS. Recorded counts
> remain valid under those prompts; they do not establish native-interface
> capability limits. See the [confirmed audit and controlled comparison](../../PROMPT_BOUNDARY_2026-11-24.md).

Training on compiler-generated experience produces two concrete successes on
new specifications: an executable-trained adapter reuses the sampled program at
a quartic argument, and a transport-trained adapter constructs a program for an
arbitrary coefficient function with renamed variables. Each scores **1/16**;
all other arms score zero on those same cells. **Both registered success criteria
fail.** This is not reliable abstraction or a new training paradigm.

| Task/sign | C1 | Hindsight | Executable | Transport |
|---|---:|---:|---:|---:|
| cubic/-1 | 0 | 0 | 0 | 0 |
| cubic/+1 | 0 | 0 | 0 | 0 |
| quartic/-1 | 0 | 0 | 0 | 0 |
| quartic/+1 | 0 | 0† | 1 | 0 |
| arbitrary function/-1 | 0 | 0 | 0 | 0 |
| arbitrary function/+1 | 0 | 0 | 0 | 0 |
| renamed arbitrary function/-1 | 0 | 0 | 0 | 1 |
| renamed arbitrary function/+1 | 0 | 0 | 0 | 0 |
| original/-1, training-target diagnostic | 0 | 0 | 1 | 0 |
| original/+1, training-target diagnostic | 3 | 16 | 5 | 10 |

All cells contain 16 proposals. † Two hindsight quartic/+1 proofs time out at
the unchanged 60-second verifier limit and remain unresolved, not known invalid.
One executable quartic/-1 and one transport arbitrary-function/+1 response fail
parsing. All remain in denominators. Even treating both unresolved controls as
correct cannot make either gate pass: neither intervention reaches its thresholds.

## The actual sampled programs

The [quartic response](executable-quartic_1-sample-8.lean) wraps the exact original
sampled lambda at `((d^2+2*d+2)^2+1)`. Its full universal contract verifies with
the fixed-style `dsimp`/`ring` proof. Training argument substitutions have degree
at most two. The new degree-four expression was generated without compiler
assistance at evaluation.

The [arbitrary-function response](transport-renamed_-1-sample-4.lean) constructs:

```lean
fun metric rho u v p q =>
  (u*p - (-(metric rho))*v*q, u*q + v*p)
```

Its proof establishes the norm-product identity and both basis laws for every
function `metric : ℤ → ℤ` and every integer argument. The prompt supplies neither
a source lemma nor a constructor. This response uses a direct formula and
`ring_nf`, rather than proving and reusing an abstract contract. It is a real
unassisted accepted sample, but a single success among 16 does not establish a
reproducible advantage over direct executable supervision.

## Comparison and integrity

The [frozen protocol](../../CONTRACT_CLOSURE_LEARNING_2026-11-24.md) fixes four
arms, ten tasks, 640 responses and two separate gates. Hindsight receives the
eight prior unchanged relabeled responses. Executable and transport receive the
same eight target statements and mathematical programs from the verified
compiler stage. Executable uses transparent wrappers with direct certificates;
transport locally proves the source contract and reuses it. Thus hindsight
tests whether closure-generated data helps; executable tests whether abstract
contract proofs help beyond direct demonstrations.

Each adapter receives 32 updates on final ordinary-GRPO C1, independently
initialized rank-8 q/v LoRA, float32/TF32 disabled, identical anchored likelihood
objective and optimizer. Exact response tokens per epoch differ: hindsight 521,
executable 802, transport 3272. This is matched steps, not matched tokens or
compute. The intervention is offline supervised learning, not an on-policy RL
experiment. Historical pristine-SFT/C3 results remain unchanged.

All 44 CPU preparation checks and all 44 allocated-node fixture checks pass.
All 453 unique evaluation judgments are reconstructed from the 640 responses.
The independent audit passes, including exact prompts/tokens/seeds, update order,
frozen references, adapter hashes and every cell/gate. An audit passing does not
mean every verifier judgment resolved: the two timeouts remain explicitly open.
Serialized adapters exactly match their live tensors. The parent hashes match
the preceding C1 experiments. Generated response tokens total 37,652: C1 6,663,
hindsight 7,053, executable 15,290 and transport 8,646.

Descriptive string counts find zero `source_contract` or `have ` occurrences in
all 640 responses. These are not a semantic proof classifier, but the accepted
transport-trained example in particular provides no evidence that the taught
abstract-contract proof strategy was used. Neither sparse success justifies an
epoch/seed sweep under the project's discovery-first rule.

Frozen execution: `942364f` under def-zhijing, H100 at trig0024, job 1400174.
The bounded keeper allocation ends after 20m15s, its batch exits successfully,
and the wrapper releases the GPU. CPU preflight took 69.403 seconds separately.
Full source, all responses/verdicts and all three actual adapters are included
in the archive inventory. Bulk C1 weights and optimizer states are excluded.
The [GitHub release](https://github.com/memo-ozdincer/restriction/releases/tag/contract-closure-2026-11-24)
contains the actual three adapters and full evidence. A fresh download verifies
all 131 members; see the [publication receipt](publication.json). Archive SHA-256:
`67ca48159ef43383af2609b166f4cbe552c2861dd7b526fb7ce6a47c2a5c1c1d`.
