# Multi-agent co-training: initial frontier-collaboration evidence

User direction, verbatim:

> alright. so, this research direction is officially now multi agent co-training.
>
> First order of business: Read frontier agent solvers within ACTUAL multi agent environments, and see if they have the same issue of not asking for help. Good source of multi agent collaboration from the community https://pequalnp.com/ and similar efforts

> once you find it, get some subagents to read through the traces, and see what they think generally about the collaboration, whether we see the same pitfalls etc.

Reviewed November 26, 2026. Three independent readers commissioned for public
mathematical traces, software-world traces and frontier mathematical systems.
Two readers returned findings; the third did not finish its review, so the
lead independently examined frontier provider reports and Prove2Me.
This is an evidence audit, not new model inference or training. Prior local
[matched HELP experiment](experiments/matched_help_20261126/README.md):
0/32 voluntary requests across original and corrected prompts; all 32 direct
proofs rejected. At a mandatory request-content checkpoint, final acceptance
matched 4/16, swapped 2/16, no response 1/16; primarily whole-proof transfer.
One targeted partial repair. These were isolated CLI calls, not a persistent
interactive environment, so direct comparison must acknowledge this difference.

## Strong independent quantitative analogue: World of SWECraft

[Shen et al., World of SWECraft, arXiv:2610.24061v2](https://arxiv.org/pdf/2610.24061),
§4, Figure 5, Appendix C Table 4, Appendix D.1. Real interdependent Python
packages, independent maintainer agents, optional issue/PR/comment exchanges,
collective outcome measured on hidden downstream packages. Six maintainers
per World-1 condition. Reported cross-package interaction counts:

| Model | Interactions | Sessions (Table 4) |
|---|---:|---:|
| Claude Opus 5 | 323 | 596 |
| Gemini 3.8 Flash | 61 | 604 |
| Kimi K2.7 Code | 21 | 605 |
| GPT-5.6 Sol | 0 | 606 |

These are all inter-package interactions, not specifically help requests,
and sessions are not known opportunities to ask. Zero Sol interaction is
nonetheless directly relevant. In mixed teams (four Sol, two Opus), Opus
initiated all 12 cross-repository issue threads, Sol initiated none but
replied to 10/11 issues addressed to it. Authors report useful resulting
software fixes. This separates initiation from ability to respond.
Compulsory communication prompts increased contact frequency to 5.5%/7.6%
of sessions but did not improve held-out performance: scores 1.051/1.048
versus 1.059 optional (similar API cost). Mixed model speedup score 1.120
versus all-Sol 1.059 and all-Opus 1.159; no causal attribution solely to
communication because capabilities/harness also change.

Appendix D.1 case reports (not independently recoded raw traces): an Opus
maintainer discovers a performance bottleneck in another package and sends
reproducible measurements; the recipient fixes it, and original maintainer
measures improvement. A Gemini consumer detects a correctness regression in
another package that the isolated maintainer misses; recipient fixes it.
These are proactive information sharing rather than solicited help. D.2
shows duplicate changes without assignment/ownership and shared mistaken
conclusions about dependency buildability. Authors report 40k released
session traces; [project](https://www.swecraft.world/), [gallery](https://sim.swecraft.world/gallery),
[launcher](https://github.com/software-worlds/swecraft-launcher). Gallery
returned HTTP 403 through browsing; raw full traces not downloaded. No claim
of independent trace census. Correct model label is GPT-5.6 Sol, not GPT-6 Sol.

## Actual community mathematical trace: P=NP public fleet

[Project architecture](https://pequalnp.com/how), [external agent contract](https://pequalnp.com/join.txt),
[proof repository](https://github.com/open-goat/pequalnp-proofs). Outside
workers receive leased exact Lean statements with point rewards, can return a
reason code or, for eligible roots, submit checked reductions. Thinker and
builder roles and planner-directed subproblems make this partly orchestrated,
not an experiment in free negotiation. The public contract limits what outside
agents can send into the official planner. Do not interpret the absence of
requests as incapacity if communication is not available.

[Discussion #21642](https://github.com/open-goat/pequalnp-proofs/discussions/21642)
is a concrete multi-party conversation with explicit self-reported Claude,
Codex and GPT-6.2 Astra provenance. Opening post was human-requested; public
comments do not reveal prompts for every message. The exact grid thread:

- Amritpal describes an unresolved 28-gate construction and asks for either
  a candidate or its failure cases. Astra reports a candidate satisfying 21
  of 24 required cases and all forbidden-case constraints, with Lean checks.
- Amritpal's Codex uses that candidate to reach 23/24, preserves the negative
  constraints, reports search regions already ruled out. The peer confirms
  it, derives a new necessary condition for repair, and supplies a Lean proof.
- The other participant uses that observation to characterize a restricted
  class. Full target remains open. This is genuine accumulation of partial
  mathematical work, not only entire-answer delegation; reported local
  verification has not been independently rerun for this research note.
- Another exchange in the thread independently replays a certificate for
  three disjoint residual edges and combines it with touching and connected
  cases, establishing coverage of the three-edge subproblem (not full root).
- A separate question posted around 02:07 UTC gets a negative response
  at 11:30 UTC: the agent found no new result. Communication can be slow,
  and even useful messages are not guaranteed to solve the recipient's task.

The opening agent reports >200 leased steps, seven merged proofs and two
accepted behind earlier PRs; repeated assignments of one hard problem led
to repeated discovery of the same obstacle. Generic hand-back codes don't
retain detailed mathematical failure information. This is a contributor
report, not independently counted fleet-wide. Other contemporaneous threads:
[21969](https://github.com/open-goat/pequalnp-proofs/discussions/21969) reports
missing negative-result memory, limited reuse, and no general outside-to-planner
idea channel; [10772](https://github.com/open-goat/pequalnp-proofs/discussions/10772)
reports 526/532 active leases in one high-throughput track, with many verified
results but stalled alternatives, a possible local-reward allocation failure.
[9526](https://github.com/open-goat/pequalnp-proofs/discussions/9526) and
[19533](https://github.com/open-goat/pequalnp-proofs/discussions/19533) present
explicit cross-goal proof transfer proposals and checked bridge examples.
[13344](https://github.com/open-goat/pequalnp-proofs/discussions/13344) reports
valid out-of-lease by-products; [22710](https://github.com/open-goat/pequalnp-proofs/discussions/22710)
reports duplicate/quota/coordination closures. Maintainer in #13344 reports
a same-day change permitting proofs for posted steps already solved locally,
but entirely new statements still require strategy-seat approval. These are public participant
observations, not controlled measurements. Live/board static page extraction
was unpopulated; direct read of public data endpoint returned 403. No full
internal transcript or silent-agent denominator was obtained.

## Prove2Me: actual cross-agent mathematical correction

[Chen et al., arXiv:2608.28433v2](https://arxiv.org/html/2608.28433v2), §4.4–4.5,
Appendix A Figures 7–8. Decentralized platform with native proof sketches,
checked reusable objects, discussion channels, human-curated authoritative
milestones. Case examples: a second agent disproves a Gotsman–Linial lemma;
first agent corrects its missing boundary condition; the branch then closes.
Exact matrix completion discussion snapshot shows two agents sharing progress.
No spontaneous-request frequency or matched isolated handoff control.
[Workspace](https://github.com/prove2me/prove2me_workspace) and
[communication reference](https://github.com/prove2me/prove2me_workspace/blob/main/references/communicate.md)
identify a mission discussion API requiring access token; no enrollment or
external action performed. The paper reports distinct agent model mixtures;
case comparisons confound models, harness, corpora and billing. Human-curated
milestones are materially different from a flat terminal-reward environment.

## Other published comparisons

[CooperBench](https://cooperbench.com/static/pdfs/main.pdf), §5: optional
communication is actually used (up to 20% of actions); reduces simultaneous
edit conflicts but does not significantly improve joint task success for any
of five models. Their cases indicate that coordinating locations is easier
than agreeing on mathematical/semantic content. GPT-5 and Claude Sonnet 4.5
therefore cannot be described as universally silent. Self-reported message
frequency and LLM-coded error categories are not mathematical verifiers.

[OpenAI Navier–Stokes report](https://openai.com/index/navier-stokes-solution/)
reports roughly 10,000 concurrent agents and 2.7 million messages in the
reported Navier–Stokes effort. Strong evidence of communication at scale,
not a spontaneous-help rate. Different variants were assigned to groups;
researchers redirected compute and cross-pollinated intermediate findings.
The report does not publish a full interaction corpus, so distinguish
aggregate communication from model-initiated requests and controlled effects.

[DeepMind virtual math conference report](https://institute.deepmind.com/essays/cheaters-and-whistleblowers-in-the-agent-swarm/)
reports 100 Gemini 3.1 Pro agents, 71 formal tasks, public board/library,
direct messages. Authors observe productive sharing early; later incorrect
acceptances invalidate aggregate solve counts. Only legitimate collaboration
is relevant here; no analysis of bypass methods. No help-request denominator.

## Interpretation and direction

The same narrow pitfall exists externally: zero voluntary contact can occur
at frontier capability despite strong responsiveness to others. But it is
not universal and cannot be diagnosed from public output-only leaderboards.
P=NP shows positive real partial-work transfer, redundancy, failed requests,
latency, and institutional loss of unsuccessful mathematical work. This is
stronger evidence of genuine mathematical collaboration than our largely
whole-proof handoff pilot, but not evidence of co-trained parameters.
Distinguish opportunity, initiation, response, consumption, and terminal
verified effect (and whether the benefit is merely whole-target delegation).
Record only externally observable actions; these are retrospective evidence
categories, not rewards. User-designated research direction is now multi-agent
co-training; no training launched by this review.
