# Cluster Agent Handoff

## Mission

Produce the fastest credible answer to:

> Does hard exclusion of the dominant verified Lean proof mode, followed by a
> reset to the same base model, cause RLVR to discover additional verified
> proof modes?

Read `AGENTS.md` and `research/EXPERIMENT_PLAN.md` before editing code.
Read `research/ROADMAP.md` before beginning an STP or Rewarding the Rare experiment.

## First session

```bash
git status --short --branch
git remote -v
bash scripts/project/preflight.sh
```

Then:

1. create an environment following `UPSTREAM_README.md`;
2. install and test DeepSeek-Prover-V1.5's Lean verifier;
3. install `leanprover-community/repl`;
4. make one proof from `data/minif2f_test.parquet` reach the verifier;
5. run base inference on a tiny training slice;
6. save the full command, environment, and output under a run directory.

Do not implement blocking until unchanged inference and a GRPO smoke run work.

## Recommended run layout

```text
runs/
  c0_base/
    seed-42/
  c1_grpo_default/
    seed-42/
  c2_unlikeliness_2/
    seed-42/
  c3_hardblock_restart/
    seed-42/
```

Each run directory should contain:

```text
command.sh
resolved_config.yaml
environment.txt
git_state.txt
dataset_hashes.txt
model_revision.txt
metrics.json
proofs/
block_archive.json        # C3 only
```

`runs/` is ignored by git. Commit small summaries under `results/` only after
review.

## Fast engineering ladder

### E0 - Environment

- model loads;
- vLLM generates;
- Lean verifier accepts a known proof;
- one official inference shard completes.

### E1 - Baseline smoke

- run unchanged C0 on a tiny slice;
- run unchanged C1 for a few updates;
- confirm logged proof counts and rewards.

### E2 - Mode signature

- implement a small module with no ML dependency;
- unit-test canonicalization;
- create an offline archive from E1/C0 proof logs;
- inspect at least 20 signatures manually.

### E3 - Disabled-feature equivalence

- add hard-block configuration with default disabled;
- fixed batch and seed must match upstream advantages exactly when disabled.

### E4 - Hard block smoke

- load a frozen archive;
- confirm block hits are logged;
- confirm blocked correct advantage is zero;
- confirm incorrect advantages are unchanged;
- confirm no checkpoint from mode discovery is loaded.

### E5 - Registered runs

Execute C0-C3 according to `research/EXPERIMENT_PLAN.md`.

## Implementation hint

Keep the archive and mode signature logic outside the large trainer module.
Suggested modules:

```text
verl/lean/proof_modes.py
verl/lean/mode_archive.py
```

The trainer should only:

1. call the signature function after generation;
2. attach mode metadata to each rollout;
3. load a frozen archive;
4. zero blocked-correct advantages;
5. log counters and checksums.

## Definition of done

- C0-C3 use matched configurations;
- C3 demonstrably starts from the pristine base;
- proposal budgets are equal and auditable;
- at least three seeds, or a clearly labeled one-seed pilot;
- pass@N and mode coverage are reported;
- negative results and all-blocked prompts are reported;
- the final diff is small enough to review against the pinned upstream commit.
