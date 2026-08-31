# Restriction-RL

## Research question

Can an RLVR policy preserve and recover a broader range of correct Lean proof
modes by preventing its dominant verified mode from receiving further policy
updates?

## Method

Restriction-RL uses a simple sequential intervention:

```text
sample verified proofs from the base policy
        |
        v
identify each theorem's dominant correct tactic signature
        |
        v
freeze a deterministic dominance archive
        |
        v
restart actor and reference from the base model
        |
        v
train with dominant correct modes blocked from policy updates
```

Alternative correct proofs retain the ordinary verifier-derived learning
signal. Incorrect proofs retain their original treatment. This makes the
blocked mode an explicit counterfactual: what correct behavior does the policy
learn when its most common successful pattern no longer supplies an update?

## Motivation

Standard on-policy RLVR can repeatedly sample and reinforce solutions that are
already probable under the base model. This improves correctness while
concentrating the learned distribution. Restriction-RL redirects the existing
learning signal toward correct alternatives already reachable by the policy.

Lean makes this mechanism directly measurable. Every candidate proof receives
a deterministic correctness verdict, while normalized tactic signatures give
an auditable measure of how many distinct proof patterns remain represented.

## Observed behavior

Across 9,655 training theorems, standard GRPO produced 34,336 correct tactic
signatures and Restriction-RL produced 53,825 at the same 308,960-proposal
budget—a 56.8% increase. On 467 held-out theorems, Restriction-RL produced 481
additional correct tactic signatures while solving 273 theorems at pass@32,
compared with 271 for standard GRPO.

The paired held-out analysis finds 1.03 additional correct tactic signatures
per theorem (`p = 7.94e-15`). Restriction-RL also recovers 43.3% of base-model
modes observed at least twice and absent from the GRPO sample; the recovery
rate reaches 58.8% for base modes observed at least four times.

## Current direction

The next evaluation measures how proof-mode coverage accumulates through
pass@128. The result will determine whether the next training run should use a
more stable cross-fitted blocklist, a matched blocking ablation, or a broader
proof workload.
