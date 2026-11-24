# Can the learned construction procedure execute once initiated?

## Result sought and decision

A few supplied syntax tokens cause the transport-trained model to reconstruct
its source contract, prove it, and specialize it to an arbitrary coefficient
function. The same start fails on unchanged C1, while ordinary unprompted
transport samples remain unsuccessful. This would motivate separating selection
of a learned procedure from practice executing it, as in temporally extended
RL options. It would not itself be a new training result or unassisted success.

The motivating observation is specific: the preceding 32-step transport adapter
has low teacher-forced demonstration loss, yet none of its 160 ordinary samples
contains the taught local lemma. That could mean failure to initiate a procedure
or failure to execute it. The user's proposal explicitly distinguishes these.
No epoch extension, new seed sweep or additional unconditioned sampling occurs.

## Frozen comparison

Use unchanged final C1 and the exact saved transport adapter from job 1400174.
Use the four arbitrary-function/renamed-function target statements and the two
original signed target diagnostics from that run, in their original order.
The original targets are training diagnostics; the other four were not updates.

For each model/task, supply one of two incomplete proof starts:

```
  have source_contract :
```

or

```
  have auxiliary :
```

The first name was used in training; the second was not. Neither supplies a
proposition, constructor, parameter substitution, local proof, or test answer.
They do supply a strategy cue and therefore change the information available.
Do not compare them to unassisted sampling without explicitly saying so.
The model must complete the proposition, prove it and finish the whole theorem.

Six tasks × two starts × two models × sixteen samples = 384 new proposals.
Reuse natural samples of these exact checkpoints/tasks from the completed
closure experiment (192 saved responses), retaining their original outcomes.
Use the exact previous per-task seeds, temperature 1, top_p 1, top_k 0. Subtract
the supplied prefix-token count from the 768-token generation budget. Assert
that the natural prompt tokens are a prefix of the extended prompt tokens;
record all supplied/generated tokens and the conditional log probability of
each supplied prefix under each checkpoint. This is an intervention on the
initial continuation, not a measurement of all probability mass of a strategy.

Whole-proof Lean correctness and axiom policy remain unchanged. Reconstruct the
exact supplied start plus generated continuation before checking. No suffix
editing, answer repair, extra source lemma, or extra verifier time. Preserve
unsupported parses and timeouts distinctly in the denominators.

## Gate and claim boundary

A conditional-correctness gate requires at least three of the four new target
cells where, for BOTH supplied names, transport gets >=8/16, C1 gets <=1/16, and
the saved natural transport samples get <=1/16. All judgments must resolve.
The original targets diagnose in-distribution execution and do not count toward
this gate. Report the full matrix even if the gate fails.

An accepted continuation might ignore its local lemma and solve the goal another
way. Thus passing this gate alone does not establish execution of contract reuse.
Before recommending a separate selection/execution training mechanism, inspect
the successful proofs and independently verify the local contract and its causal
use. If the conditional-correctness gate fails, do not tune starts or train a
selection-only intervention on this evidence. Save concrete accepted examples,
but do not replace the gate with a cherry-picked proof.

No training occurs. Freeze source, assert adapter hashes and exact reload probes,
use one bounded def-zhijing persistent allocation, release after completion,
and archive the raw bank and dependencies with verified GitHub readback.

## Primary research context, checked November 24

[Anthropic's robotics interface study](https://www.anthropic.com/research/claude-plays-robotics)
(July 9, 2026) compares direct control, controller code and pretrained-policy
interfaces. Its reported dependence on interface motivates separating procedure
selection from execution; it does not establish this mechanism for proof models.

[OpenAI's beneficial-trait RL study](https://openai.com/safety-alignment/beneficial-rl/)
(June 18, 2026) reports generalization beyond training domains and persistence
under adversarial pressure. It motivates demanding transfer beyond a practiced
surface behavior. It is not evidence that this small SFT adapter has acquired
a similarly broad capability. These are research motivations, not novelty claims.
