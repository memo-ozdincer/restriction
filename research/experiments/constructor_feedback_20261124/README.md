# Checked feedback did not produce a verified constructor

Neither a numerical counterexample nor a symbolic error produced an accepted
universal constructor. All six conditions scored 0/16; both registered feedback
criteria fail. No training or second repair round follows this screen.

| Contract | Failure notice | Numerical counterexample | Symbolic residual |
|---|---:|---:|---:|
| Quadratic composition | 0/16 | 0/16 | 0/16 |
| Bezout transport | 0/16 | 0/16 | 0/16 |

All 96 proposals are retained. Two Bezout/failure responses fail parsing and
remain in the denominator. There are 37 unique Lean source checks, zero unresolved
judgments, and eight successful feedback/correctness fixture checks. The independent
audit also checks exact tokenizer inputs, generated token decoding, seeds, selected
prior candidates, feedback text, complete sources, axiom acceptance and counts.
Generation used 5,989 response tokens and 28,032 supplied prompt tokens.

The most frequent exact response in every condition still contains the rejected
function: the wrong-sign quadratic pair or unchanged Bezout coefficients. See
[modal responses](modal-responses.json). This describes the modes, not all outputs.
Supplying a failed candidate may itself encourage copying; these results do not
isolate that effect or show that all feedback mechanisms fail.

Feedback came from symbolic evaluation of the frozen prior modal candidates.
Lean checked the residual identities and concrete inequality witnesses before
sampling. The numerical quadratic example has all inputs one, giving -4 versus 0;
the Bezout example gives 2 versus 1. No correct implementation entered a prompt.
The original universal contracts and correctness verifier stayed unchanged.

This is inference on inspected tasks using authored specifications, not learned
transfer, a new synthesis algorithm or a revolutionary paradigm. It preserves the
previous 0/64 results and failed binary-reward gate. The next research mechanism
must address a different bottleneck; this experiment provides no verified repair
trajectories to distill. The [frozen protocol](../../CONSTRUCTOR_FEEDBACK_2026-11-24.md)
sets the claim and stopping boundaries.

Execution was frozen at 0bec080. Job 1399674 used one H100 on trig0016 under
def-zhijing for 5m11s; its batch step completed with exit code zero and its wrapper
released the allocation. During its initial wait, a requested switch to debug was
rejected because the same job had already started on compute. It ran on compute;
no duplicate job or scheduler renewal occurred. Both the failed request and actual
allocation are preserved.
