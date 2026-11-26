# Environment-wide RLVR: initial novelty check

User proposed broadening initial-state coverage instead of adding intermediate
reward or prescribed reasoning. The simplest version: truncate an existing
verified proof around 75%, run terminal-only RLVR on newly sampled suffixes,
evaluate complete proofs from scratch. A related version samples legal
intermediate states of naturally generated successful and failed trajectories.
Physical motivation: user-reported pinball random-start evolutionary training
outperformed entrance-only training when tested from the entrance (92/2048
vs 42/2048); evidence resides in the separate physical-experiment project and
has not been independently audited here.

## Direct precedents (checked November 26)

- [PrefixRL, Reuse your FLOPs (2026)](https://arxiv.org/html/2601.18795v2):
  very close direct overlap. Three uniformly random cuts in the 40–80%
  token range of each correct off-policy solution form three prefixed
  prompts plus one unprefixed prompt per hard problem; on-policy RL on
  continuations, no-prefix evaluation. Sections 4–5 report back-generalization
  even when training exclusively with prefixes, held-out improvements and
  2x compute efficiency versus SFT+RL including rejection collection. This
  substantially anticipates the simple general-purpose prefix/RL proposal.
- [R3, ICML 2024](https://proceedings.mlr.press/v235/xi24a.html):
  reverse curriculum over demonstrations and outcome supervision, including
  program-based mathematical reasoning. Uses additional implementation
  choices; not a purely fixed random-state comparison.
- [AdaBack, 2025](https://arxiv.org/abs/2506.18110): per-problem adaptive
  exposure to partial rationales, evaluates mathematical reasoning and
  latent-parity generalization. Another direct precedent for the sparse
  reward access hypothesis.
- [RRPO/SRPO, Credit Assignment with Resets (2026)](https://arxiv.org/html/2605.25507):
  random and self-localized restarts from failed model-generated reasoning
  traces; suffix-only policy gradient with group-relative normalization,
  reporting both reasoning and coding experiments. Covers much of the
  self-generated-state variant. Coding experiment splits unit tests on
  the same problems and uses fraction-passed training reward, not disjoint
  theorem-family binary terminal transfer.
- [Kimina-Prover technical report](https://huggingface.co/blog/project-numina/kimina-prover):
  random proof cuts include truncation and infilling. Report does not
  isolate an exact compute-matched binary terminal-only suffix-RLVR
  versus whole-proof RLVR experiment.
- [Backplay, 2018](https://arxiv.org/abs/1807.06919) and
  [Reverse Curriculum Generation, 2017](https://arxiv.org/abs/1707.05300):
  direct general RL precedents for shifting start-state distributions to
  reach sparse terminal reward and ultimately solve original tasks.
- [DeepSeek-Prover V1.5](https://arxiv.org/abs/2408.08152):
  truncate-and-resume in inference-time search, not itself the same
  isolated training intervention.
- [HSE student thesis on variational problem synthesis](https://www.hse.ru/en/edu/vkr/1161668994):
  abstract explicitly mentions Lean suffix completion on partial model
  proofs and RL fine-tuning. Full causal isolation not established from
  abstract alone; avoid claiming no Lean-specific precedent.

## Verdict

The general insight and basic suffix-RL method are substantially scooped,
including the prediction of unassisted back-generalization. Do not market
it as new. A narrower empirical question remains: how fixed broad state
coverage vs reward-adaptive reset, prefix knowledge provenance, natural
failed proof prefixes and typed Lean subgoals affect genuine held-out
autonomous performance and capability retention at matched compute.
This is a candidate gap, not a certified novelty claim. No experiment or
training launched; user asked only for a quick novelty check.
