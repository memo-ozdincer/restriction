# Frozen Experiment Plan

## 1. Primary estimand

At a fixed proposal budget and fixed RLVR configuration, estimate the change
caused by replacing the paper's soft rank penalty with:

1. a blocklist learned from base-model rollouts;
2. a reset to the pristine base checkpoint; and
3. zero policy advantage for correct rollouts whose deterministic mode ID is
   blocked.

The primary outcomes are pass@N and correct proof-mode coverage on held-out
theorems.

## 2. Conditions

### C0 - Frozen base

- model: `deepseek-ai/DeepSeek-Prover-V1.5-SFT`
- no training
- temperature: 1.0
- evaluation proposal counts: 32, 128, and 512 where affordable
- purpose: establish pass@N and the initial proof-mode distribution

### C1 - GRPO-Default

Paper Table 1:

- PPO epochs: 1
- KL loss coefficient: 0.02
- rank penalty: 0
- total training epochs: 1
- 32 samples per theorem
- response length: 512

Purpose: reproduce the paper's distribution-sharpening baseline.

### C2 - GRPO-Unlikeliness-2

Paper Table 1:

- PPO epochs: 2
- KL loss coefficient: 0.10
- rank penalty: 0.25
- total training epochs: 1
- 32 samples per theorem
- response length: 512

Purpose: reproduce the strongest soft intervention used in the main analysis.

### C3 - HardBlock-Restart

Identical to C2 except:

- rank penalty: disabled;
- the blocklist is frozen from C0 mode-discovery rollouts;
- actor and reference initialize again from
  `deepseek-ai/DeepSeek-Prover-V1.5-SFT`;
- blocked correct rollouts receive zero policy advantage;
- incorrect rollouts retain upstream treatment.

The primary C2/C3 contrast therefore changes the diversity intervention.

## 3. Mode definition

Use a deterministic `mode_id` computed from verified proof text.

Version 1 should:

1. strip Lean comments;
2. parse top-level proof steps with the existing `parse_proof_steps`;
3. normalize whitespace;
4. extract the ordered top-level tactic heads;
5. retain ordered explicit lemma identifiers when extraction is reliable;
6. serialize the versioned signature and hash it.

Store both:

- `exact_proof_id`: comment-stripped, whitespace-normalized proof hash;
- `mode_id_v1`: tactic/lemma signature hash.

The primary blocking key is `mode_id_v1`. Report exact-proof coverage as a
secondary metric. Do not change the signature after seeing C3 results. If the
signature is inadequate, register `mode_id_v2` as a new experiment.

## 4. Dominance archive

Build the archive using C0 training-split rollouts only.

For each theorem:

- consider only Lean-verified correct proofs;
- count mode IDs;
- mark the most frequent mode dominant only if:
  - at least 4 correct proposals were observed; and
  - its share is strictly greater than 0.50.

Tie behavior: no block.

The threshold is fixed before C3. Sensitivity at 0.40 and 0.60 is secondary and
must not replace the registered 0.50 result.

Persist:

- theorem ID;
- mode ID;
- count;
- correct-rollout denominator;
- share;
- signature version;
- source model revision;
- data split;
- sampling seed;
- archive SHA-256.

## 5. Hard exclusion semantics

For every proposal:

1. generate normally;
2. verify normally;
3. compute the mode ID;
4. account for the proposal in the fixed compute budget;
5. if incorrect, preserve the upstream reward/advantage path;
6. if correct and unblocked, preserve the upstream path;
7. if correct and blocked, set final policy advantage to exactly zero.

Do not relabel blocked correct proofs as verifier failures.

Do not resample for free. A blocked proposal consumes the same proposal budget
as every other proposal.

If a theorem's selected batch contains no unblocked correct proof, do not
create a positive update for that theorem. Record the event and skip the
prompt-level update if necessary to prevent a batch containing only blocked
correct proofs from teaching the policy that correct behavior is incorrect.

## 6. Restart semantics

Mode discovery and C3 training are separate runs.

C3 must initialize:

- actor from the pristine base checkpoint;
- reference from the same pristine base checkpoint;
- optimizer from a fresh state;
- rollout buffer empty;
- global step zero.

The frozen blocklist is the only artifact carried over.

## 7. Data

Use the repository's paper-associated data, but do not trust the current
launcher default blindly.

Priority:

1. reproduce the 10K experiment with
   `data/mff-lwb-10k-seen.parquet` if it matches the paper split;
2. use `data/mff-lwb-goedel-holdout-800.parquet` and
   `data/mff-lwb-unseen-200.parquet` as the paper-associated validation slices
   after verifying their roles;
3. use `data/minif2f_test.parquet` for the external benchmark;
4. treat `data/mff-lwb-goedel-28k.parquet` as a later scale-up until its
   relation to the paper's stated 11K experiment is resolved.

Before the first real run, log row counts, columns, and SHA-256 for every split.

## 8. Metrics

Primary:

- pass@1, pass@4, pass@8, pass@16, pass@32, pass@128;
- pass@512 where affordable;
- number of held-out theorems with at least one verified proof;
- mean verified `mode_id_v1` coverage per theorem;
- number of theorems where C3 discovers a correct mode absent from C0's first
  32 proposals.

Secondary:

- exact normalized proof coverage;
- tactic-head coverage;
- block hit rate;
- fraction of prompts with no unblocked positive sample;
- verified proofs per generated token;
- verified novel modes per GPU-hour;
- training stability and KL.

Every result must report proposal counts. Do not compare accepted-sample counts
without compute accounting.

## 9. Seeds and stopping

- paper/default data seed: 42
- smoke test: seed 42
- main comparison: at least seeds 42, 43, 44 if budget permits
- no early stopping based on test metrics
- abort only for numerical failure, infrastructure failure, or a registered
  safety limit

## 10. Fast falsification ladder

1. Unit tests on synthetic proof strings.
2. C0 inference on a small training slice.
3. Offline replay: apply the proposed blocklist to C0 rollouts and quantify how
   much signal would be removed.
4. Short C1/C3 smoke runs on an identical small slice. Label these engineering
   checks, not scientific results.
5. Full C0-C3 on the registered split.

Proceed to STP only after the full Lean result is interpretable.

