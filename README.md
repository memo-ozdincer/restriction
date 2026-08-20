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

## Registered seed-42 result

The full C0/C1/C3 signal-finding experiment is complete. On the 223-theorem
registered-valid split, hard blocking recovered proof-mode coverage lost by
ordinary GRPO and modestly improved pass@32:

| Condition | pass@1 | pass@32 | Correct tactic modes |
|---|---:|---:|---:|
| C0 base | 57.44% | 68.61% | 2,591 |
| C1 GRPO-Default | **63.90%** | 68.16% | 2,233 |
| C3 HardBlock-Restart | 60.94% | **69.06%** | 2,477 |

The paired theorem-level analysis finds no significant difference in the
identity or category of theorems solved by C1 and C3 at pass@32: five are
C3-only, three are C1-only, and exact McNemar `p = 0.727`. The strong signal
is within already solved theorems. C3 produces 1.03 more correct tactic modes
per theorem (`p = 7.9e-15`) while producing 0.67 fewer correct samples per
theorem (`p = 8.6e-11`). This is consistent with reduced concentration, not
yet with discovery of a distinct class of hard theorems.

Read [research/RESULTS.md](research/RESULTS.md) for the complete results,
provenance, intermediate findings, statistical tests, failures, and claim
boundaries. Machine-readable artifacts are indexed in
[results/README.md](results/README.md).

## Start here

1. Read [research/THESIS.md](research/THESIS.md).
2. Read the frozen contract in
   [research/EXPERIMENT_PLAN.md](research/EXPERIMENT_PLAN.md).
3. Read the staged roadmap in [research/ROADMAP.md](research/ROADMAP.md).
4. Follow [cluster/HANDOFF.md](cluster/HANDOFF.md).
5. Give the cluster agent [AGENTS.md](AGENTS.md) as its operating rules.
6. Track progress in [PROJECT_STATE.md](PROJECT_STATE.md).
7. Read the completed seed-42 report in
   [research/RESULTS.md](research/RESULTS.md).

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

The registered signal-finding comparison executed in this repository is:

| ID | Condition | Purpose |
|---|---|---|
| C0 | Frozen base model | Establish the original proof distribution |
| C1 | GRPO-Default | Reproduce distribution sharpening |
| C2 | GRPO-Unlikeliness-2 | Planned soft-intervention reproduction; not executed in the completed seed-42 comparison |
| C3 | HardBlock-Restart | Replace soft rank weighting with hard mode exclusion and restart |

The completed C1/C3 comparison is informative but not a causal estimate of
hard blocking alone: C1 uses one PPO epoch and KL 0.02, while C3 uses two PPO
epochs and KL 0.10. The next decisive control is C3 with blocking disabled and
all other C3 settings unchanged. C2 remains necessary for a direct hard-versus-
soft intervention comparison.

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

Implementation, focused tests, C0 archive construction, full C1/C3 training,
registered C0/C1/C3 evaluation, and paired theorem-level analysis are complete
for seed 42. The result is a positive mechanism signal: C3 substantially
mitigates C1's tactic-mode collapse, but it does not exceed base-model mode
coverage and its pass@32 improvement is small. No multi-seed or matched
blocking-disabled C3 control has been run, so stronger causal or population
claims are not supported yet.
