# One sampled program, a contract covering every integer input

## Interesting result sought

The small prover writes a reusable arithmetic function and Lean proves its
contract for all integer inputs. One accepted rollout then represents an
unbounded family of valid transformations, rather than one successful numeric
answer. The two targets are quadratic-norm composition and transporting Bezout
coefficients through two integer row operations. Display the actual sampled
functions and proofs, with no human repair of their implementations.

The bounded-generator study supplied an entire numerical program in supervision,
yet got no unseen-discriminant solutions. Repeating that supervision is not the
next bet. The proposed mechanism changes the rewarded object to a function
with a universal contract: close its domain of validity inside the verifier,
instead of estimating it only from a task distribution. This follows the earlier
typed-procedure research direction, but asks the model to synthesize a required
constructor. Earlier free-form invariant discovery admitted mostly tautologies.
Here authored nondegenerate contracts rule out the zero/identity shortcuts.

This first screen determines whether that reward has accessible positive and
negative examples. It is not an RL training result or evidence of novelty.
Universal program synthesis, dependent types and proof-carrying code are existing
ideas. A new training paradigm would require a demonstrated learning advantage
and unassisted transfer beyond these supplied specifications.

## Frozen screen

- Final ordinary-GRPO C1 only, unchanged parameters. No generator adapter.
- Two fixed existential-function theorems, saved verbatim in the panel. The
  model sees function types and their mathematical specifications, but neither
  implementations nor example solutions. Specifications are substantial supplied
  information; this is not specification discovery.
- Quadratic contract preserves the product of norms for every d,a,b,x,y and
  fixes two basis values. These boundary values constrain behavior and exclude
  the zero function; they are extra guidance, not an implementation-free miracle.
- Bezout contract preserves the integer pairing through the specified two row
  operations, and returns the original coefficients when both operations vanish.
  It need not compute canonical or unique coefficients.
- Four groups of 16 per task: 128 proposals total, max 768 tokens each,
  temperature/top-p one, top-k zero. Seed 20261124 + 1000*task_index + batch_index.
  Task order is quadratic then Bezout. No retries, prompt edits, extra seeds or
  demonstration insertion after model outputs.
- Existing float32 runtime with TF32 disabled, unchanged parsing, upstream Lean
  correctness and closed-axiom audit. All complete-source hashes and verdicts
  are retained. System errors remain unresolved; parse errors stay in denominators.
- Two authored positive fixtures and two zero-function negative fixtures must
  pass their expected checks before sampling. Fixture bodies never enter prompts.

Advance to designing a learning comparison only if each task has both a verified
positive and a rejected proposal, with all verdicts resolved. This is a reward
support gate, not an effect-size claim. If every proposal already succeeds, there
is no execution deficit here to train. If either family has no valid constructor,
do not launch sparse-reward training or rescue the gate with authored solutions.

Count every proposal and unique Lean check, retain full model responses and
frozen execution, and independently reconstruct the reward ledger. An accepted
existential function theorem proves existence; direct execution additionally
requires a transparent extracted witness. Do not claim a runnable extracted
skill until that witness has actually been recovered and checked. No training,
new numerical task evaluation, or deployment of an external skill library is
included in this initial screen.

## Evidence behind the choice

The November 10 OpenAI study reports that RL can increase control over reasoning
text without explicit process supervision. It does not show that visible proof
style identifies a learned algorithm. We use checked functional behavior instead.
[Primary source](https://openai.com/safety-alignment/cot-monitorability-model-lifecycle/)

Anthropic's May 8 study reports that richer principle-oriented training can
generalize better than narrow behavioral demonstrations. This motivates testing
what object is learned; it does not establish that universal contracts improve
mathematical learning. Our failed numerical-generator trial is direct local
evidence against assuming that supplying more procedural information suffices.
[Primary source](https://www.anthropic.com/research/teaching-claude-why)

Use one bounded H100 keeper under def-zhijing, launch manually through SSH,
persist each generated group and release the allocation on completion or failure.
Publish code and this protocol before model sampling. Preserve the earlier
generator outcome and all historical gates unchanged.
