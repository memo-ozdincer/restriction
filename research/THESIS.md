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

The held-out shift is not explained by C3 simply producing more correct
rollouts. At exactly 16 correct draws, C3 has 10.27 expected tactic modes per
eligible theorem versus 9.14 for C1 (`p = 7.20e-15`). Its coverage advantage
is positive under every frozen representation from first tactic head to exact
normalized proof. Within the observed pass@32 distribution, C3 starts behind
C1 at one proposal but crosses by four and grows to a 14.0% mode-coverage
advantage at 32, consistent with a lower-probability but broader sampled tail.

This comparison establishes a distributional difference between the realized
C1 and C3 policies, not yet a blocking-specific causal effect. C1 uses one PPO
epoch and KL 0.02, whereas C3 uses two PPO epochs and KL 0.10 in addition to
blocking. The registered no-blocking control matches C3's optimizer settings
and is required for causal attribution.

## Current direction

Two complementary experiments are active. Fresh pass@128 evaluation tests
whether the broader tail continues beyond 32 samples. A full C3-matched
no-blocking run tests whether blocking, rather than the optimizer and KL
change, causes the training distribution shift; its final checkpoint will be
evaluated on the same held-out set. Their joint result will select the smallest
decisive follow-up among replication, likelihood/mechanism diagnosis, the
registered cross-fitted StableTopBlock ablation, or a workload with richer
within-problem proof variation.
