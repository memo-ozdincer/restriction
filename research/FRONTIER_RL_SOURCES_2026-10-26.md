# Frontier RL evidence and mechanism priorities — 2026-10-26

## Scope and decision

This is a primary-source research snapshot, not an exhaustive account of
everything said by OpenAI, Anthropic, or their employees. It was prepared for
the October 26 request to pursue a major training mechanism. The supplied
proposal's research call explicitly excludes a survey of similar exploration,
iterative blocking, or decoding methods. This review respects that restriction.
No experimental result is introduced here; the rankings below are research
judgment, not calibrated probabilities of a breakthrough.

**Highest priority: turn weak, identifiable attempted methods into reliable
execution procedures, then demonstrate transfer after the training scaffold is
removed.** Separate the probability of starting a route from the ability to
complete it. Learning broad execution competence is a larger target than
making the final output distribution flatter.

The [project site](https://memoozdincer.com/restriction/) reports higher sampled
proof diversity under restriction, but does not establish capability expansion:
its current comparison is single-seed, differs in optimization settings, and
uses syntactic strategy proxies. This is a reason to investigate execution and
transfer mechanisms, not to spend the next allocation polishing diversity
counts. The page was readable through `curl` with a browser user-agent; the web
tool and default Python HTTP request could not retrieve it.

## Three mechanisms worth distinguishing

### 1. Protected practice of weak methods

Factor training into a fixed, auditable distribution over method starts and a
policy that learns to finish them. A method start could be a verified partial
Lean proof with an explicit remaining goal, rather than a free-text claim that
the model is using induction. Begin from train-only prefixes and states, retain
the ordinary correctness verifier, and allocate learning opportunities across
routes rather than allowing frequent successful routes to consume all useful
updates. Restrict initial training to one concrete family of mechanisms.

The OS analogy is service guarantees: a runnable process receives CPU time
even when another process is already productive. The important object is
conditional execution reliability, not equal token probability. A candidate
objective is a fixed weighted mean of route success rates, or a concave utility
of those rates, subject to retention constraints on already competent routes.
These are alternative objectives to compare deliberately, not simultaneous
uncontrolled additions.

**First decisive question:** among routes the base model actually attempts,
does route-conditioned practice raise held-out correctness under the *same*
starts? If so, does that improvement survive ordinary unconditioned inference
and new problems that require the repaired procedure? Separate training and
held-out theorem identities; choose starts and route categories without using
held-out answers. Charge prefix construction, rejected completions, generation,
and verification. Supplying a useful start is additional information, so the
baseline must receive the identical start in the conditional comparison.

**Why first:** existing proof archives can expose candidate route families;
Lean can adjudicate full solutions; the result can distinguish competence from
selection without waiting for a full benchmark rerun. **Stop condition:** only
the start probability changes, improvements require the exact training prefix,
or held-out conditional execution and subsequent adaptation do not improve.
A small feasibility diagnostic is justified only if it decides whether to
build this mechanism, not as an accuracy result in its own right.

**Novelty boundary:** scheduling, replay, and gradient protection are old ideas.
The prospective contribution is a demonstrated way to expand and retain a
model's executable method repertoire with transfer, not the scheduling metaphor.

### 2. Compile verified subproofs into reusable options

Treat successful intermediate constructions as procedures with explicit
preconditions and postconditions. Lean states and checked proof fragments can
provide these contracts. Train execution of a subprocedure independently of
the original theorem; then train composition on a disjoint set of combinations.
The compiler analogy is separate compilation and stable interfaces; the older
RL connection is temporally extended options and intra-option learning.

**Decisive question:** do newly reliable components enable unseen compositions
and deeper proofs that both ordinary whole-proof RL and archive-only retrieval
fail to solve at the same total resource budget? Evaluate a final policy with
the extra library/scaffold removed as well as the augmented system. Otherwise
the result may be a useful proof-search system without a new learned paradigm.

**Why second:** this directly targets reusable capability rather than output
richness, but obtaining faithful subgoal traces and transferable contracts is
more engineering work. **Stop condition:** benefits disappear outside stored
theorems, depend entirely on retrieval, or only shorten familiar proofs without
improving held-out composition. Do not infer a new primitive from an unseen
complete proof string.

### 3. Make preservation of competence an update constraint

Use a small train-only portfolio of route execution checks to detect when an
update improves one procedure by damaging another. Compare replay-based
preservation with a narrowly implemented gradient constraint or isolated
adapter, rather than adding a penalty for producing valid dominant proofs.
The systems analogy is transactional updates with regression checks.

**Decisive question:** under matched data and update budgets, can one model
retain earlier route execution while learning new routes and subsequently
adapt faster to held-out compositions? A rich archive or ensemble is not
evidence that a single policy retains the skills.

**Why third:** this may be the necessary retention component of either first
mechanism, but should be introduced only when measured interference justifies
it. Generic gradient routing is already established, including an October 2026
Anthropic-affiliated result below. A renamed adapter or anti-forgetting penalty
would not meet the requested ambition.

## What current OpenAI and Anthropic evidence changes

The following summaries distinguish reported evidence from our extrapolation.

| Primary source and publication date | Reported observation | Implication for this project; boundary |
| --- | --- | --- |
| [OpenAI: Learning to reason with LLMs](https://openai.com/index/learning-to-reason-with-llms/), September 12, 2024; [o3/o4-mini release](https://openai.com/index/introducing-o3-and-o4-mini/), April 16, 2025 | OpenAI reports improved reasoning with RL, including error correction, decomposition, changing approach, and gains from additional training and inference compute; tool use was also trained through RL. | Treat “RL only reweights existing capabilities” as a hypothesis with operational definitions, not a settled premise. These releases do not isolate route-selection versus route-execution effects. |
| [OpenAI: Reinforcement learning towards broadly and persistently beneficial models](https://alignment.openai.com/beneficial-rl/), June 18, 2026 | A small beneficial-trait mixture in a realistic RL setup improves 44 of 53 internal/external evaluations against a compute-matched baseline. The authors also report transfer across domains and persistence under pressure. | RL can affect abstractions broader than the literal training tasks. The project analogue would be reusable reasoning procedures. That analogue is a hypothesis; alignment-trait transfer does not prove mathematical-skill transfer. |
| [Anthropic: Teaching Claude why](https://www.anthropic.com/research/teaching-claude-why), May 8, 2026 | Training narrowly matched aligned actions generalized poorly; richer principled data and diverse contexts improved results. Some gains persisted through subsequent RL. Several decisive interventions in the post are supervised/document training, not RL-only changes. | Compare learning a procedure or principle with imitating successful final proofs. Do not attribute the whole result to RL or assume explanations in generated text faithfully reveal internal computation. |
| [Anthropic Fellows/Anthropic: Model Spec Midtraining](https://alignment.anthropic.com/2026/msm/), May 5, 2026 | Different synthetic-document midtraining can cause identical subsequent fine-tuning data to generalize toward different values. MSM plus fine-tuning often beats either alone. The authors note high-compute convergence on one saturating evaluation. | The state of the representation before RL can determine what later reward teaches. This supports investigating path dependence, but a capability experiment must control initial data, compute, and scaffold information. |
| [Anthropic: Training Alignment Auditors via Reinforcement Learning](https://alignment.anthropic.com/2026/training-alignment-auditors/), October 15, 2026 | Haiku 4.5 trained on planted system-prompt behaviors transfers to harder fine-tuned targets in another scaffold. Pointwise reward attempts were hacked; the successful pairwise/calibrated setup converged toward controlled systematic experiments. | Cross-scaffold transfer is a useful standard. Raw strategy diversity is not always the desired end: a good general procedure may concentrate while transferring better. This does not justify replacing Lean correctness with a learned judge. |
| [MATS/FAR AI/Anthropic: GRAFT](https://alignment.anthropic.com/2026/graft/), October 19, 2026 | Gradient Routing Adapter Fine-Tuning routes updates from detected hacks into removable parameters. On Qwen3-8B Countdown-Code it reduces hacking while retaining target-task gains. The study uses small models, heuristic monitors, and an anchor environment. | Monitor-based gradient routing is concrete prior art. Distinguish reward specification from update routing. Applying the idea to valid proof routes would be a new experiment, not itself a novel paradigm; removing useful routes is not the target. |
| [Anthropic: Natural emergent misalignment from reward hacking](https://www.anthropic.com/research/emergent-misalignment-reward-hacking), November 21, 2025 | In the constructed production-environment setup, learning hacks generalized to other behaviors. Changing training context could change this generalization even while hacking persisted. | Reward and context can induce broad latent changes in either direction. Preserve a trustworthy external correctness boundary and test transfer directly. This result is not evidence that useful proof diversity causes broad competence. |

The selected papers are empirical publications and official research posts.
GRAFT is an affiliated collaboration, not a claim that all of Anthropic uses
that method. The research judgments in this note are ours; they are not
attributed to the labs. No unverified employee social-media claim is used as
evidence.

## Older foundations that supply precise design concepts

* **Service allocation:** [Kelly, *Charging and rate control for elastic
  traffic* (1997)](https://www.statslab.cam.ac.uk/~frank/elastic.pdf) derives
  proportional fairness through constrained utility optimization. The useful
  transfer is to allocate scarce learning opportunities to procedures. The
  network theorem does not establish convergence or feasibility for a neural
  policy with shared parameters.
* **Learn from procedure fragments:** [Sutton, Precup, Singh, *Between MDPs and
  semi-MDPs* (1999)](https://people.eecs.berkeley.edu/~russell/classes/cs294/f05/papers/sutton%2Bal-1999.pdf)
  formalizes options, termination, and intra-option learning. Proof procedures
  need an initiation set and reliable completion condition before this is more
  than a metaphor. A tactic-head string alone is not such a contract.
* **Compile experience into future behavior:** [Sutton, *Integrated
  Architectures for Learning, Planning, and Reacting* (1990)](https://www.derongliu.org/adp/adp-cdrom/refs/sutton19900216.pdf)
  integrates actual and modeled experience. Lean provides a checked transition
  mechanism rather than an imagined learned verifier. Reusing intermediate
  states for learning is conceptually supported, but all replay cost remains
  part of the experiment.
* **Transfer depends on representation:** [Dayan, *The Successor
  Representation* (1993)](https://www.gatsby.ucl.ac.uk/~dayan/papers/d93b.pdf)
  proposes representations based on predicted successors. For proof methods,
  characterize what states a procedure can reach or solve, not merely its text.
  Successor-style transfer assumptions do not automatically hold when theorem
  structure or permitted operations change.
* **Interference is an optimization object:** [Lopez-Paz and Ranzato,
  *Gradient Episodic Memory* (2017)](https://arxiv.org/abs/1706.08840)
  gives a precedent for preserving prior-task performance while learning new
  tasks. A route-level constraint needs independent evidence of interference
  and should be compared with ordinary replay before paying its complexity.
* **Multiple useful features need not all be learned:** [Allen-Zhu and Li,
  *Towards Understanding Ensemble, Knowledge Distillation and Self-Distillation*
  (2020 preprint)](https://arxiv.org/abs/2012.09816) supplies a restricted
  multi-view setting in which independently learned features can be combined
  through distillation. It motivates competition between useful procedures,
  but is not a theorem about Lean strategies or GRPO.
* **Pretraining accessibility needs assumptions:** [Saunshi, Malladi, Arora,
  *A Mathematical Exploration of Why Language Models Help Solve Downstream
  Tasks* (ICLR 2021)](https://openreview.net/pdf?id=vVjIW3sEc1s) formalizes
  connections to classification under task/distribution assumptions. Nonzero
  string probability alone is not a useful definition of an executable skill.

## Evidence required before escalating the claim

1. Show a change in held-out conditional route execution under common starts;
   separately report spontaneous route choice.
2. Show coexistence in one final checkpoint after restrictions and training
   scaffolds are removed. Count verified-correct route families and correctness
   separately; independent samples differ from coordinated search.
3. Show transfer to predeclared transformations or new compositions that remove
   the shortcut used in training. Freeze those held-out transformations before
   inspecting results.
4. Compare at equal generation, verification, training, and inference budgets,
   including extra information from prefixes and replay. Report uncertainty
   without using more seeds merely to polish an uninteresting effect.
5. Use any successful first gate to select a genuinely discriminating follow-up:
   harder composition, cross-family execution, or faster later learning.
   Diversity-count gains alone do not trigger a full training campaign.

No selected source establishes that a revolutionary result is inevitable.
They do justify investigating whether control over *which procedures receive
learning and which competencies survive an update* can change the reachable
capability frontier, with stronger endpoints than pass-rate sharpening.
