# Actual policy updates completed; cross-context credit ties the length control

The concrete successful continuations include nested inductions that close a
new product goal from an empty root:

```lean
  intro xs n
  induction xs <;> induction n <;> simp_all
```

Cross-context training finds a valid List-by-Nat product proof in 4/16 samples,
versus base 1/16, local reward 2/16, length control 3/16 and replay 2/16. On the
Nat-by-Nat product it finds 8/16 versus 5, 4, 7 and 5 respectively. These are
small descriptive frequency differences, not newly acquired capabilities:
the pristine base already solves both tasks. The two tree tasks offset this
advantage, leaving cross-context credit and the length control exactly tied on
the registered aggregate. The hoped-for distinctive training result did not occur.

## Fixed evaluation result

Every policy received all 40 roots, 16 proposals each. Composition includes all
16 original October roots plus four fresh tree/product roots. Each of six
composition schemas has equal weight in the registered macro score; the raw
fraction gives each root equal weight. These are different denominators.

| Policy | Retention correct / 320 | Composition correct / 320 | Composition schema macro |
|---|---:|---:|---:|
| Pristine base | 190 | 27 | 14.0625% |
| Local correctness | 215 | 28 | 14.5833% |
| Cross-context credit | 206 | 34 | 17.7083% |
| Length-matched credit | 206 | 34 | 17.7083% |
| Successful-proof replay | 219 | 29 | 15.1042% |

The raw composition rates are 8.4375%, 8.75%, 10.625%, 10.625% and 9.0625%.
All five policies score **0/16 on every one of the sixteen original October
composition roots**. Every accepted composition proof is on a fresh tree or
product task. No previously unsolved task meets the registered cross-context-only
criterion. Cross's margin over the strongest control is zero; its training-root
retention improves five percentage points over base. The combined registered
exciting-result criterion is false.

| Fresh root | Base | Local | Cross | Length | Replay |
|---|---:|---:|---:|---:|---:|
| List × Nat product | 1 | 2 | 4 | 3 | 2 |
| Nat × Nat product | 5 | 4 | 8 | 7 | 5 |
| Binary tree, paired predicates | 11 | 11 | 10 | 12 | 12 |
| Ternary tree, paired predicates | 10 | 11 | 12 | 12 | 10 |

Each cell is accepted proposals out of 16. All valid proof routes count. The
first accepted cross proof for each product root is saved as a standalone Lean
file, with its sample ID and exact source hash. They are illustrative successes,
not a substitute endpoint or evidence of novel mathematics.

## What actually trained

All four arms started from the same pristine DeepSeek-Prover-V1.5-SFT 7B bytes
and received the same fresh 320 exact-token trajectories, group order and
optimizer schedule. Each completed 40 optimizer steps and 640 candidate passes,
training 3,932,160 LoRA parameters. All 120 adapter parameter tensors changed in
each arm. The disabled-adapter base probe remained bitwise identical after
training. Reloading each saved adapter reproduced its probability probes exactly
(maximum discrepancy 0.0). There are four real final adapters, not just configs.

The fresh training batch contains 199 locally correct proposals. All 1,280
logical candidate/context checks resolve through 544 distinct full Lean sources.
Cross and length assign identical rewards in 16/20 groups; only 12/320 candidate
assignments differ. This is a weak separation of the proposed semantic mechanism
from brevity, even though the four resulting adapters have distinct hashes.

The initial bfloat16 collector stopped on a probability-consistency failure,
before any reward matrix or policy update. It preserved 176 trajectories and
released job 1373078 after 9m36s. D-129 changed computation uniformly to float32
with TF32 disabled, retained the scientific design and original tolerances, and
preserved the failed attempt. The replacement collection passes with maximum
response-mean discrepancy 0.00004168 nats and maximum token discrepancy 0.00026274
nats. This was an engineering repair, not selection for better proof rewards.

Job **1373310**, one H100 on `trig0014` under `def-zhijing`, completed the full
pipeline and released its allocation after **32m59s**. All 3,200 evaluation
proposals were judged through 698 distinct full Lean sources, with no missing
or unresolved verdicts. A separate auditor reconstructs token provenance, source
hashes, reward assignments, adapter identities, optimizer counts, all 200 cells,
schema macros and the registered result directly from the saved evidence. It
passes. Six focused loss/reward/adapter tests also pass.

## Decision

This pilot does not support a distinct benefit from cross-context credit over
the shorter-proof control. The tiny fixed update budget does not establish that
all versions of the idea fail, but there is no basis for a seed sweep or simply
scaling this version. It also does not overcome the recursive-state composition
barrier in the original panel. A next mechanism must produce a meaningful
training contrast beyond brevity and address that barrier; do not label this
frequency shift a revolutionary paradigm. The broader research goal remains
active and unachieved.

## Preservation

The [policy-update release](https://github.com/memo-ozdincer/restriction/releases/tag/policy-update-2026-11-19)
contains all four adapters and the exact training evidence. Its 59,043,341-byte
training archive contains 83 files; downloaded archive and member checksums all
match. SHA-256: `10aa1cd65623c6296741e9415467570b59ee0e43a1432f184dfd7cae1a13c356`.
Evaluation evidence is published separately on the same release with its own
inventory and download-verification receipt. Compact reports and standalone
proofs are under `research/experiments/policy_update_20261119/fp32/`.
Base weights and optimizer state are explicitly excluded. See
`CONTINUE_ELSEWHERE.md` for recovery instructions and the pinned runtime.
