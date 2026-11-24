# Correct the C1 prompt-interface discrepancy before further mechanism claims

## Confirmed implementation discrepancy

Historical C1 training uses `prompt_fn_deepseek` followed by tokenization with
`add_special_tokens=False`. The function appends `<｜begin▁of▁sentence｜>` after
the theorem, immediately before the proof. The recent standalone drivers use
the same textual instruction/header/theorem but `tokenizer.encode(prompt)`:
this prepends that marker and omits it at the proof boundary.

This is an implementation error in the standalone C1 research interface, not a
model capability finding. The exact producing commit `5ced4c3`, resolved C1
configuration and saved final training tensors establish the historical format.
The dedicated CPU audit reconstructs all 128 retained training prompts and checks
the recent transport training records. The latter are internally consistent:
their concatenated training tokens match joint encoding, but their parent model
was trained with a different boundary. Low teacher-forced loss is not by itself
evidence of reliable sequence generation.

Historical C1/C3 trainer-based results use their original interface and are not
changed by this discovery. All saved standalone proof counts and Lean verdicts
remain as observed under their recorded prompts. However, recent standalone
C1 failures do not establish limits under C1's trained interface, and claims
about GRPO suppressing capabilities or about subsequent adaptation must be
qualified. Do not silently regenerate or relabel old experiments.

## Prospective marker-placement comparison

The concrete result sought is a valid universal constructor under C1's historical
interface where the standalone format failed. This is a correction/control
experiment, not a revolutionary paradigm or a new training method.

Freeze unchanged final C1 and four token formats in a 2×2 comparison:

| Format | Leading BOS | Proof-boundary BOS |
|---|---|---|
| neither | absent | absent |
| legacy standalone | present | absent |
| native historical | absent | present |
| both | present | present |

Construct marker positions explicitly and disable implicit insertion. Verify
that native matches `prompt_fn_deepseek` token-for-token and legacy matches the
recent standalone tokenizer call. All other prompt text, model weights, sampling
settings and correctness checks remain identical. The difference in marker
position/count is the intervention, not an extra mathematical hint.

Four inspected tasks: original universal quadratic composition, original Bezout
transport, and both signs of the arbitrary-function quadratic contract from
closure learning. Sixteen new responses per task/format: 256 proposals. Use
temperature 1, top_p 1, top_k 0, a uniform 768 generated-token cap, and seeds
20261129 through 20261132 in listed order. Native and legacy each contain one
marker; the other two formats diagnose leading versus trailing contributions.
Record exact token arrays and prefix likelihoods for `  have source_contract :`
and `  use fun`, without supplying those prefixes to generation.

All four positive and invalid contract fixtures were already checked; recheck
the eight fixtures in this frozen run. Keep the fixed 60-second Lean limit and
axiom policy. Preserve parse errors and unresolved judgments separately. No
parameter updates or adapter use. Run one bounded def-zhijing allocation with
the Python keeper and manual SSH driver, and release it when done.

Report every cell. A large correction effect requires native to exceed legacy
by at least four accepted responses on at least two of the four tasks, with all
judgments resolved. Whether or not this gate passes, the input-format discrepancy
is already established independently of outcomes. Do not tune markers, tasks,
seeds or budgets afterward. No old failure becomes a success retroactively.

## Forward implementation rule

Use the explicit prompt-interface helper for new C1 experiments. Any departure
from native must be named as an intervention, with exact IDs and comparison.
Leave frozen historical sources intact for reproducibility. Do not globally
rewrite the old drivers and then imply their existing artifacts used new code.
After the control, select the next training comparison using the corrected
interface evidence; do not infer that an interface correction is a new paradigm.
