# Research Roadmap

## Recommendation

Start with the current Rewarding the Unlikely fork, not full STP.

It is the fastest credible mechanism test because:

- the released trainer already performs GRPO on Lean proofs;
- the paper already diagnoses distribution sharpening under the exact base
  model we want;
- Lean provides deterministic correctness;
- the intervention has a narrow advantage-computation seam;
- STP uses the same Lean base model but adds conjecturer training, iterative
  data generation, replay, and substantially larger compute.

This ordering is about time-to-interpretable-result, not a judgment that STP is
less interesting.

## Phase 1 - Rewarding the Unlikely fork

Goal: compare paper-matched soft rank weighting against persistent hard
dominant-mode blocking plus pristine restart.

Use:

- `deepseek-ai/DeepSeek-Prover-V1.5-SFT`;
- the checked-in Lean verifier;
- deterministic tactic/lemma mode signatures;
- C0-C3 from `research/EXPERIMENT_PLAN.md`.

Fast gate: a small offline replay must show that the proposed archive blocks a
meaningful number of correct rollouts without eliminating all positive signal
for most prompts. If it does not, revise the mode signature in a newly
registered experiment before spending on full RL.

## Phase 2 - Rewarding the Rare fork

This is the smallest human-legible strategy test. Reuse the paper's exact
three-stage clustering prompts and its two worked AIME taxonomies:

- `aime24_i_p10`, with five canonical methods;
- `aime2025_ii_p3`, with four canonical methods.

Paper-matched smallest route:

- Qwen2.5-7B-Instruct actor;
- Qwen2.5-72B judge;
- eight rollouts per training prompt;
- correct rollouts only may receive diversity-related changes.

Swap inverse cluster-frequency reweighting for persistent hard exclusion and a
pristine actor restart. Keep the judge prompts, correctness scoring, task
prompts, and taxonomy fixed. This phase can show recognizable strategy
coverage, but the judge makes enforcement less deterministic than Phase 1.

## Phase 3 - STP fork

Run STP after Phase 1 establishes that the blocking mechanism is worth scaling.
Fork the official repository:

```text
https://github.com/kfdong/STP
```

Use its Lean path and `deepseek-ai/DeepSeek-Prover-V1.5-SFT`. Do not attempt
the paper's full 241M-proof scale initially.

The clean first STP experiment is event-triggered refresh:

1. retain STP's conjecturer, prover, verifier, data, prompts, and refresh code;
2. detect persistent dominant tactic/lemma signatures on verified proofs;
3. trigger the existing refresh/restart machinery on dominance rather than a
   fixed schedule;
4. block the archived mode after restart;
5. compare against the original scheduled-refresh control at matched proposal
   compute.

Keep claims separate:

- Phase 1/2: within-problem solution-mode coverage;
- Phase 3: self-generated problem frontier and proof behavior.

STP's topic-distribution projection addresses conjecture-topic balance, not
proof-strategy diversity. Do not treat those as the same intervention.

## Stop/go rules

Proceed from Phase 1 smoke tests to full runs only if:

- the upstream baseline works unchanged;
- mode IDs are stable under comments and whitespace;
- disabled blocking is equivalent to upstream;
- block hits and no-positive events are measurable;
- the base restart is auditable.

Proceed to STP only if Phase 1 yields either:

- credible additional verified modes; or
- a clear failure mode that STP's iterative conjecturing can specifically test.

An interpretable negative Phase 1 result is still a result. It is cheaper and
more useful than discovering the same failure after reproducing full STP.
