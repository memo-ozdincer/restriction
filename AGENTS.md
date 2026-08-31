# Agent Operating Contract

## Governing principle

Treat the released implementation as the controlled baseline. The scientific
claim depends on changing exactly one mechanism:

```text
soft unlikeliness weighting -> hard dominant-mode exclusion + base-model restart
```

Do not improve unrelated components while implementing the intervention.
Preserve the base model, data, prompts, verifier, reward correctness signal,
sampling settings, optimizer, evaluation, and seeds.

If an upstream discrepancy prevents exact reproduction, document it in
`research/DECISIONS.md` before choosing a value. Never silently resolve an
ambiguity.

## Primary model

Use `deepseek-ai/DeepSeek-Prover-V1.5-SFT` for the actor initialization and
frozen reference model.

Do not use a learned judge in the primary experiment. Lean is the only
correctness verifier. Mode signatures must be deterministic and auditable.

## Required work order

1. Run `scripts/project/preflight.sh`.
2. Make the upstream base-model inference path work unchanged.
3. Reproduce C0 and one short C1 smoke run.
4. Implement and unit-test proof canonicalization and mode signatures.
5. Build a persistent dominance archive from C0 rollouts.
6. Implement hard exclusion behind a disabled-by-default configuration flag.
7. Prove with tests that incorrect rollouts retain their original treatment.
8. Prove with tests that blocked correct rollouts receive zero policy advantage.
9. Prove with tests that an all-blocked/no-alternative prompt is skipped rather
   than trained as if it were incorrect.
10. Start C3 from the pristine base model, not from a C1 or C2 checkpoint.
11. Run the registered evaluation and write results to a new run directory.

## Non-negotiable invariants

- Never train from the mode-discovery checkpoint. Restart from the exact base
  checkpoint.
- Never reward incorrect-but-different proofs.
- Never alter the Lean verifier to make an alternative proof pass.
- Never increase the rollout proposal budget only for C3.
- Never hide blocked proposals from compute accounting.
- Never change more than one experimental factor in a comparison.
- Never claim tactic-signature diversity is semantic mathematical diversity.
- Never use test-set rollouts to construct a training blocklist.

## Implementation boundary

The likely intervention seams are:

- generation and verification:
  `verl/trainer/ppo/ray_lean_trainer.py::_generate_and_verify_full_proofs`
- advantage computation:
  `verl/trainer/ppo/ray_lean_trainer.py::_compute_advantages`
- existing proof parsing:
  `verl/lean/utils.py::parse_proof_steps`

Add the smallest possible new module for canonical mode signatures and a
persistent archive. Avoid broad trainer refactors.

## Testing expectations

At minimum add tests for:

- comments and whitespace do not change a mode ID;
- materially different tactic heads do change a mode ID;
- archive counts survive save/load exactly;
- dominance threshold behavior at, below, and above the boundary;
- blocked correct advantages are zero;
- incorrect advantages match the upstream calculation;
- disabled blocking is bit-for-bit equivalent on a fixed synthetic batch;
- restart refuses a non-base checkpoint unless explicitly running a control.

## Reporting

For every run save:

- git commit and dirty status;
- complete resolved config;
- model revision;
- dataset path and SHA-256;
- seed;
- hardware;
- wall-clock time;
- proposal, verified, correct, blocked, and trained sample counts;
- blocklist snapshot and archive checksum;
- pass@N and proof-mode coverage metrics.

Update `PROJECT_STATE.md` at each milestone.
