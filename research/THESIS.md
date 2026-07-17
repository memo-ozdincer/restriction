# Project Thesis

## Question

Can an RLVR policy discover additional correct solution modes without a
positive novelty reward if we:

1. identify the dominant correct mode;
2. discard all learned policy changes;
3. return to the same base model; and
4. restart RLVR while making the dominant mode ineligible for positive policy
   updates?

## Hypothesis

Standard on-policy RLVR repeatedly samples and reinforces solutions that are
already probable under the base model. Rewarding the Unlikely addresses this
with continuous rank-based reweighting. We hypothesize that the simpler
intervention is sequential elimination:

```text
discover dominant correct mode
        |
        v
freeze a deterministic blocklist
        |
        v
reset actor and reference to the pristine base model
        |
        v
run the same RLVR loop, but give blocked correct modes zero policy advantage
```

This is not a novelty bonus. An unblocked proof receives only the original
verifier-derived learning signal. Incorrect proofs remain incorrect.

## Why this is scientifically interesting

Soft diversity objectives must choose a coefficient and continuously trade
dominant against rare outputs. Hard blocking asks a more direct counterfactual:
what latent correct behavior is reachable when the policy cannot learn from its
usual winning mode?

Three outcomes are informative:

1. **Alternative modes emerge.** This supports the view that the base policy
   already contains accessible, under-sampled proof strategies that ordinary
   RLVR suppresses.
2. **Only superficial variants emerge.** Blocking exact trajectories is
   insufficient; the intervention needs a better operational definition of
   mode.
3. **No alternative mode emerges.** The dominant mode may be the only correct
   behavior inside the base policy's reachable support. Positive exploration
   mechanisms or new data may then be necessary.

## Claim boundary

The primary experiment studies formal Lean proof behavior. A deterministic
tactic/lemma signature is an auditable proxy for proof mode, not proof that two
formal scripts correspond to distinct human mathematical ideas.

Do not generalize a positive result to natural-language reasoning without a
separate strategy-level evaluation.

## What this project is not

- not an entropy bonus;
- not a semantic embedding reward;
- not a learned novelty reward;
- not a prompt-diversification study;
- not a new verifier;
- not a larger-model or larger-data study;
- not an attempt to beat theorem-proving state of the art.

The value comes from causal isolation, not leaderboard performance.

