# Experimental Notes

This page collects provenance and interpretation details for the completed
Restriction-RL experiment. It is intentionally separate from the project
overview.

## Provenance

The implementation began from the public code release accompanying
*Rewarding the Unlikely*. The retained upstream baseline is commit
`ca1cff05ebdf2cfe9737fd416897da838a93e11a`, and the original README remains in
`UPSTREAM_README.md`. The experiment uses
`deepseek-ai/DeepSeek-Prover-V1.5-SFT` at revision
`e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`.

## Interpretation

- The completed comparison uses seed 42.
- Standard GRPO and Restriction-RL use different PPO epoch and KL settings, so
  a matched blocking-disabled run is the cleanest isolation of the blocking
  mechanism.
- Tactic signatures are deterministic operational measures of formal proof
  patterns, not semantic labels for human mathematical strategies.
- Current held-out evaluation uses 32 proposals per theorem. Fresh pass@128
  evaluation is queued.
- The registered-valid dataset is a documented reproduction split rather than
  an unpublished split from the motivating work.
- A soft-unlikeliness condition and likelihood-uplift analysis have not yet
  been run.

The paired pass@32 comparison contains five Restriction-RL-only and three
standard-GRPO-only solved theorems (exact McNemar `p = 0.727`). The clearest
measured effect is broader correct proof coverage within substantially the same
solved theorem population.

## Execution notes

An early evaluation attempt encountered node-memory and verifier startup
failures and was excluded before producing a complete result. Successful runs
retain full proposal accounting, including verifier-infrastructure failures.
The immutable implementation and execution decisions are recorded in
`research/DECISIONS.md`.
