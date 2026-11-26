# RRL: selective sharpening rather than global novelty pressure

User's current hypothesis (verbatim):

> eh. it would have to be something rtu doesn't do well already.
>
> Like, idk:
> - RTU never allows for distribution sharpening, which makes RLVR lose its magic (because that's part of the fun)
> - RRL maintains exact RLVR dynamics, or at least very similar, and allows for distribution sharpening around new solutions, it just blocks one type (or a set of them), so you get grpo dynamics WITH non distribution sharpening or something

## Registered retrospective discriminator

Before calculating conditional distributions: RTU's current likelihood-rank
penalty is global/adaptive among admitted correct samples; C3 masks only a
frozen C0 dominant tactic mode. Hypothesis: C3 directs ordinary binary
correctness reinforcement to unblocked alternatives and exhibits stronger
concentration **on alternatives**, not merely continued sampling of original
dominant mode, than matched C2. If concentration is entirely attributable
to the frozen dominant mode, the proposed advantage is unsupported.

Read archived finalized C2/C3 training proof logs only, same 9655 roots,
same order/32 proposals, authenticate both and C0 archive hashes. Use
the original >0.5 dominance threshold, min 4 correct C0 samples (1014 eligible).
Remove that exact frozen mode in both arms counterfactually when computing
alternative metrics. Include all archived eligible roots, including zero
observed alternatives. Primary discriminators: mean maximum nonblocked
mode count / 32 (absolute sampled probability of strongest allowed mode);
mean unbiased collision probability of two distinct sampled correct
alternative draws, on common roots with >=2 alternatives in both arms.
Separate alternative mass, original dominant mass and maximum mode absent
from C0 / 32. Secondary raw mode counts and top-share conditional on any
alternatives. Report frozen training step windows (different roots across
windows, not within-theorem evolution) and independent theorem-paired
directions, no p-value or post-hoc utility labels. C3/C2 are matched
optimizer settings; no-blocking C1 differs, so cannot isolate RRL vs GRPO
causality. The result may or may not establish differential alternative
sharpening; it cannot establish semantic mathematical capability from
syntactic signatures. No new sampling or training.

## What the actual trainer guarantees (and does not)

In `ray_lean_trainer.py::_compute_advantages`, C2 multiplies every admitted
correct reward by (1 - 0.25 * likelihood rank / group size), then normalizes
within group. The relative reward ordering is recomputed from current-policy
mean token logprobs; popular correct outputs can still have positive
advantage when incorrect alternatives exist. It is not a theorem that
RTU never sharpens any distribution. C3 has rank penalty zero, normalizes
ordinary binary rewards, then masks the archived blocked-correct advantage
to zero. Thus unblocked correct proofs have no extra anti-likelihood
preference: all receive the same group-relative binary correctness advantage
before PPO/KL effects (and the blocked originals contribute to group
normalization). The intervention does not preserve all vanilla GRPO
dynamics: all-blocked prompts are skipped, and parameters/KL are shared.
C2 and C3 both discard all-correct groups upstream in their registered
settings; the special possibility of rank preference on all-correct groups
only holds if that admission filter is removed (see SATURATED_PROMPT_MECHANISM).
The distinction is *fixed local exclusion vs repeatedly re-ranking correct
alternatives by likelihood*, not absolute sharpening prohibition.

## Authenticated archived training result

Both registered complete 308,960-proposal logs and exact C0 archive hashes
verified. Physical logs each have 308,992 rows with 32 discarded padding
proposals. The 1,014 archive-eligible roots and 13,906 C3 blocked correct
proposals reconcile. We remove each root's original frozen dominant
signature counterfactually in both C2 and C3, then compare the remaining
correct distributions. The two arms use matching optimizer configurations
and theorem order. No new verifier/sampling/training.

| Metric (equal theorem weighting) | RTU (C2) | RRL (C3) |
|---|---:|---:|
| All correct proposals / 32 | 82.56% | 85.56% |
| Original blocked mode / 32 | 37.93% | 42.86% |
| All alternative correct proposals / 32 | 44.62% | 42.70% |
| Most common alternative mode / 32 | 19.73% | **26.33%** |
| Conditional top alternative mode share (939 common roots with alternatives) | 45.59% | **62.51%** |
| Unbiased two-alternative-draw same-mode probability (887 common roots with >=2 alternatives) | 25.15% | **42.22%** |
| Mean unique correct alternative signatures | 5.91 | 3.76 |
| Most frequent mode absent from C0 / 32 | 9.80% | 9.99% |

Absolute strongest-alternative probability favors C3 on 526 of 1,014
theorems vs C2 on 359 (129 ties); conditional collision favors C3 on
658/887 vs C2 on 207 (22 ties). The result therefore cannot be
explained solely by retention of the original blocked mode, nor simply
by C3 generating more correct alternatives (it generates fewer in aggregate).
C3 has a sharper distribution within the unblocked correct set. Novel
means absent in finite C0 samples, not new mathematical knowledge.
The negligible top-novel difference gives no strong evidence that C3
specifically sharpens modes *absent from C0*. Existing low-frequency
alternatives are a more defensible target.

For the first 100 and last complete 100-step windows (matched root
order across arms, distinct roots across windows):

| Window | C2 max alt /32 | C3 max alt /32 | C2 conditional collision | C3 conditional collision |
|---|---:|---:|---:|---:|
| 1–100 | 14.31% | 17.68% | 23.12% | 29.46% |
| 501–600 | 21.53% | 31.54% | 24.57% | 45.37% |

The growing C3/C2 contrast is consistent with selective sharpening across
training but not a within-theorem temporal measurement. Aggregate archived
results already show all-mode top shares over the same windows of 41.42%
to 38.35% (C2) vs 45.00% to 54.28% (C3). Our stronger audit excludes the
original blocked mode. Held-out overall pass@1 is 46.23% C2 vs 46.84% C3;
both pass@128 solve 277/467; C2 has higher syntactic diversity. Existing
results do not establish a practically meaningful performance gain or
semantic alternative capability. They support a more precise mechanism
distinction and make the following hypothesis worth exploring.

## Proposed contribution: conditional sharpening of alternate capabilities

Potential claim (not established): RRL permits selective exploration of
an already accessible lower-probability strategy and then lets ordinary
correctness reinforcement concentrate on it, rather than continuously
downweighting it once it becomes likely. RTU may be superior for finding
many distinct correct approaches but worse at developing one specific
alternative into a readily deployed reusable skill.

A discriminating target is a *family of math tasks* with at least two
independently verified starting strategies, one dominating the easy
training distribution while an alternative genuinely transfers to changed
tasks where the old approach is mathematically inapplicable (not forbidden
by an eval filter). Predeclare and authenticate the synthetic/real family,
base support and transfer boundary. Freeze training-only mode membership
and avoid claiming tactic signatures are mathematical semantics. C2, C3
and fully matched ordinary GRPO from pristine actor; equal proposal budget,
unchanged verifier and native tasks. If temporary restriction helps
consolidation, subsequent common unrestricted phase is a distinct
registered experiment with matched phase budget and pristine initial
restarts. Primary endpoint is unassisted low-sample success/transfer and
conditional competence of the alternative, not raw mode counts.
Conditional sharpening alone is not a win: C3 may simply concentrate
on an equally unhelpful substitute. If RTU matches/exceeds on this
target or its unassisted transfer, do not claim an RRL advantage.

The first discriminator is already calculated, archived in
`research/experiments/rrl_sharpening_20261126/results.json`. Raw proof
logs remain local under `artifacts/rrl-sharpening-audit` and their source
release inventory remains tracked. Reproduce via
`python3 scripts/project/audit_rrl_selective_sharpening.py artifacts/rrl-sharpening-audit NEW_OUTPUT.json`.

## User refinement, verbatim

> well no... more like, there is a really really good alternative solution (like a shortcut in mkwii, or some other hard to find thing), but equally weighting ALL alternatives REMOVES RLVR dynamics. You need RLVR dynamics preserved while having exploration, this is what RRL promotes. Now, how exactly to come up with ane example that would benefit from that, is quite a bit harder

## Reframed hypothesis: discover and exploit a rare superior route

The proposed contribution is not concentration per se, nor maximal diversity.
It is the combination of exploration beyond a stale/high-probability success
mode with ordinary RLVR reinforcement of an exceptionally valuable alternative.
RTU is not literally uniform weighting of all alternatives; its adaptive
likelihood penalty remains a competing pressure when an alternative becomes
popular. C3 does not apply that pressure to an allowed alternative. Our
conditional sharpening readback supports the mechanism distinction, not the
value of the chosen alternative.

A terminal-only learner cannot distinguish two complete successes merely
because one is human-judged clever. A "really good shortcut" must have a
consequence in the actual task environment: higher chance of completion under
the same noise, action/token/time horizon, or independently held-out context.
Do not add a proof quality or length reward to define it. If all routes always
succeed, registered binary GRPO groups have no correctness contrast; a test
where every route is equivalent under the terminal criterion cannot isolate
useful consolidation.

Candidate discriminating environments, not registered:
- A small original stochastic route/maze game: ordinary long route is
  easy to discover, many decoy routes possible, a rare short route has enough
  remaining time/robustness to reach the same finish reliably under the
  unchanged horizon. The geometry is fixed before outcomes; no shortcut
  bonus, proximity shaping or authored trajectory. Compare identical
  original-goal terminal rewards under ordinary GRPO, RTU and frozen initial
  mode exclusion. A shortcut that is too rare for any condition to sample
  tests discovery scarcity, not consolidation.
- Lean: a family of changing numeric/symbolic instances admitting a dominant
  calculation or case-specific proof and an initially rare reusable
  abstraction. Choose families with independent frozen C0 evidence of
  positive alternative support, and a natural harder distribution where
  ordinary computation is unreliable/inapplicable within the same rules,
  not banned by evaluation. The alternate proof's utility is verified by
  native correctness/transfer, not the author's tactic preferences.
  No test rollouts form a blocklist. Signature membership is syntactic, not
  a guarantee of a distinct mathematical strategy.

Discriminating measurement:
1. Establish rare alternative availability prospectively on training data
   before intervention (otherwise zero-advantage RRL cannot manufacture
   a missing positive rollout).
2. Track separate discovery and consolidation phases. How much resource is
   needed to first find each alternative? Once it is observed, how strongly
   does its probability and unassisted terminal success grow?
3. Repeated fixed diagnostic roots at predeclared checkpoints allow actual
   within-root dynamics, unlike existing different-root chronological windows.
   Equal proposal/optimization settings and compute; RTU, C3 and exact
   C3-matched no-blocking GRPO. If adding common unrestricted late phase,
   freeze schedule as different contrast.
4. Primary outcome ordinary terminal success/held-out transfer at low N
   or decision-relevant horizon. Diagnostic proof family probability,
   duration/token costs, mass concentration and robustness. Avoid claiming
   discovery speed from conditioning on successes without accounting for
   roots/arms in which shortcut never observed. No additional correctness
   signal or preference over alternatives.

The critical result would be RTU finding a valuable alternative but
failing to make it reliable, while RRL discovers and consolidates it,
producing a downstream advantage. The null (RTU consolidates equally
well or better; RRL sharpens a worse local substitute) would directly
undermine the proposed distinctive contribution. No experiment launched.
