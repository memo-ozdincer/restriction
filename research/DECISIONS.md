# Decision Log

Record decisions before running the affected experiment.

## D-001 - Repository base

- Date: 2026-07-18
- Decision: fork official repository commit
  `ca1cff05ebdf2cfe9737fd416897da838a93e11a`.
- Reason: preserve a reviewable causal diff from the paper implementation.

## D-002 - Primary model

- Date: 2026-07-18
- Decision: use `deepseek-ai/DeepSeek-Prover-V1.5-SFT` for actor and reference
  initialization.
- Reason: exact paper model; changing it would confound the comparison.

## D-003 - Mode detector

- Date: 2026-07-18
- Decision: deterministic tactic/lemma signature, plus exact normalized proof
  hash as a secondary identity.
- Reason: no learned judge, repeatable enforcement, and auditability.
- Risk: this remains a proxy for mathematical strategy.

## D-004 - Blocking threshold

- Date: 2026-07-18
- Decision: dominant share must be greater than 0.50 with at least 4 verified
  correct proposals.
- Reason: simple majority rule and a minimum evidence guardrail.

## D-005 - Compute accounting

- Date: 2026-07-18
- Decision: blocked proposals consume the fixed proposal budget and are not
  resampled for free.
- Reason: avoid giving the intervention extra inference compute.

## D-006 - Track order

- Date: 2026-07-18
- Decision: test the mechanism in the Rewarding the Unlikely Lean/GRPO fork,
  then open a Rewarding the Rare fork, and defer STP until the small controlled
  experiment is interpretable.
- Reason: the first fork supplies deterministic verification, a narrow code
  seam, and the same DeepSeek-Prover base used by STP without requiring STP's
  conjecturer and large iterative data pipeline.

## Open decisions

### Dataset identity

Verify which checked-in parquet files reproduce the paper's 10K main analysis
and approximately 11K final experiment. Record row counts, content hashes, and
the selected primary split here.

### Exact model revision

Record the resolved Hugging Face commit:

```text
TBD
```

### Cluster compatibility patches

List every required environment or compatibility patch. Keep them separate
from the algorithmic commit where possible.
