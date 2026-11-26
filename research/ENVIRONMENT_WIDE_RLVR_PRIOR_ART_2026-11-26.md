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

## Clarification: human-written Lean code as reset corpus

User distinguishes terminal-only suffix RL applied to *ordinary formal code
authored by humans*, e.g. Mathlib, from cutting model-generated natural-language
reasoning traces. PrefixRL's main experiment (§2, §5) generated one accepted
trace per hard problem through large-scale rejection sampling from the same
starting checkpoint, not a necessarily larger teacher. It also tested
cross-family Qwen3-4B/Llama-3.1-8B sources. AdaBack and R3 do use existing
dataset reference solutions (GSM8K/MATH/DeepScaleR), so using already-written
solutions as reset data is also prior art outside Lean. RRPO samples failed
policy-generated traces rather than a pre-existing human formal-proof corpus.

Kimina-Prover's July 2025 technical blog directly describes cutting human
formal proofs lacking intermediate reasoning traces, including proof truncation
and infilling. It does not specify enough about the isolated training
objective or matched downstream comparison to equate that passage with
fixed-depth terminal-only suffix RLVR across an ordinary human Mathlib
corpus. Distinguish the direct ingredient precedent from an unverified
claim that the exact isolated experiment has been performed. The narrower
experimental comparison may still be worth doing, but a change of corpus
alone does not establish a fundamentally new RL method.

## Second clarification: terminal-only is not the claimed novelty

The user explicitly clarified that the novelty sought is repurposing existing
human-authored proof corpora as a broad source of RL initial states, not
binary reward itself. Rechecked primary methods sections, rather than
equating papers from abstracts:

- [AdaBack v2, §2.1 and §3](https://arxiv.org/html/2506.18110v2) explicitly
  starts from existing (question, target response) pairs and samples a
  per-item prefix fraction, adapting it to observed rewards. Studies MATH,
  GSM8K, DeepScaleR and synthetic tasks. It does not study a corpus of human
  formal Lean proof states. Its comparison with R3 reports static mixtures
  of segmented existing reference solutions in R3.
- [R3 v2, §§3.1–3.4](https://arxiv.org/html/2402.05808) explicitly mixes
  intermediate starts from correct demonstrations across stages, including
  procedural reasoning with Python. All RL arms in the main study warm
  up with SFT; numeric answer reward is partial in some experiments.
- [Kimina July 10, 2025 post](https://huggingface.co/blog/project-numina/kimina-prover)
  expressly describes using random proof truncation and infilling on human
  annotated formal proofs without intermediate reasoning chains. It does
  not state corpus breadth, exact optimization phase/objective for this
  component, allocation over cut depths, or an isolated comparison. Its
  April [Preview technical report](https://arxiv.org/html/2504.11354)
  does not describe random proof cuts. Therefore the direct data-construction
  overlap is established, but the exact corpus-wide training study is not.
- [AlphaProof Nature paper, §1.3](https://www.nature.com/articles/s41586-025-09833-y)
  uses approximately 300,000 Mathlib human state–tactic pairs in SFT;
  the described primary RL phase uses formal statements and self-generated
  search experience. Human-state training exists but is not evidence for
  the proposed initialization distribution in RL.

Revised verdict: no confirmed exact public demonstration of the entire
broad human Lean corpus-as-reset-distribution experiment in sources inspected.
Significant overlap remains (Kimina's data augmentation, R3/AdaBack's
existing-solution reset mixtures, PrefixRL's continuation learning).
Do not assert the exact experiment is scooped or novel with certainty.
The research value, if any, would come from demonstrating that very broad
human formal-state exposure is a stronger use of the corpus for generalized
mathematical learning than imitation or root-only training, under appropriate
controls. This is a hypothesis and not a literature novelty guarantee.
