# Dominant-Mode Blocking for RLVR

This repository is a controlled research fork of
[Rewarding the Unlikely](https://arxiv.org/abs/2506.02355). It tests one
specific hypothesis:

> After identifying a dominant correct proof mode, reset to the unchanged base
> model and run RLVR with that mode hard-excluded. This may expose correct
> modes that ordinary GRPO and soft unlikeliness weighting fail to surface.

The project deliberately avoids novelty bonuses, entropy rewards, learned
diversity rewards, and other positive incentives. The intervention is hard
exclusion plus restart.

## Start here

1. Read [research/THESIS.md](research/THESIS.md).
2. Read the frozen contract in
   [research/EXPERIMENT_PLAN.md](research/EXPERIMENT_PLAN.md).
3. Read the staged roadmap in [research/ROADMAP.md](research/ROADMAP.md).
4. Follow [cluster/HANDOFF.md](cluster/HANDOFF.md).
5. Give the cluster agent [AGENTS.md](AGENTS.md) as its operating rules.
6. Track progress in [PROJECT_STATE.md](PROJECT_STATE.md).

All three supplied papers, the literature search, and the original governing
memo are preserved under [papers/](papers/README.md) and
[research/source/](research/source/README.md). Notes on the primary paper and
configuration discrepancies are in
[research/PAPER_NOTES.md](research/PAPER_NOTES.md).

## Model choice

Use exactly:

```text
deepseek-ai/DeepSeek-Prover-V1.5-SFT
```

Use it for both the initial actor and the frozen reference policy. Do not swap
in a newer or smaller model for the primary experiment. Correctness is supplied
only by Lean verification; no learned reward model or LLM judge belongs in the
primary loop.

See [research/MODEL_AND_COMPUTE.md](research/MODEL_AND_COMPUTE.md) for the
reasoning, optional follow-on models, and hardware guidance.

## Experimental conditions

The minimum publishable comparison is:

| ID | Condition | Purpose |
|---|---|---|
| C0 | Frozen base model | Establish the original proof distribution |
| C1 | GRPO-Default | Reproduce distribution sharpening |
| C2 | GRPO-Unlikeliness-2 | Reproduce the paper's soft intervention |
| C3 | HardBlock-Restart | Replace soft rank weighting with hard mode exclusion and restart |

C2 and C3 must share the same base checkpoint, data, prompts, verifier,
sampling budget, optimizer, PPO epochs, KL coefficient, response length,
evaluation code, and seeds. The intended comparison changes only the
intervention.

## Repository lineage

- Upstream repository:
  `https://github.com/AndreHe02/rewarding-unlikely-release.git`
- Upstream commit pinned for this fork:
  `ca1cff05ebdf2cfe9737fd416897da838a93e11a`
- Local development branch: `dominant-mode-blocking`
- The original upstream README is preserved as
  [UPSTREAM_README.md](UPSTREAM_README.md).

The official code is retained rather than vendored into a fresh framework so
that differences remain reviewable with:

```bash
git diff ca1cff05ebdf2cfe9737fd416897da838a93e11a
```

## Push to a new remote

The authors' remote is named `upstream`, so an accidental push to it is less
likely. Add your own repository as `origin`:

```bash
git remote add origin <YOUR_GIT_URL>
git push -u origin dominant-mode-blocking
```

On the cluster:

```bash
git clone <YOUR_GIT_URL>
cd dominant-mode-blocking-rlvr
git switch dominant-mode-blocking
```

## Current status

The research package and upstream fork are ready. The hard-block
implementation is intentionally not marked complete. The first cluster agent
should reproduce inference and baseline behavior before changing the trainer.
That separation prevents an untested local implementation from being mistaken
for a reproduced baseline.
