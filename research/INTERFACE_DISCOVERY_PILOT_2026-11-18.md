# The result we want to see: one discovered lemma unlocks two problems

Prospective small experiment, November 18, 2026. The user requests a concrete,
exciting sampled behavior before a falsification checklist. This is a bounded
inference experiment using cached 7B models, not a new large training campaign.

**The hoped-for artifact:** a model, shown a state transition but neither later
question, invents a checked invariant. The exact same generated lemma makes
two different downstream targets solvable for ordinary GRPO, which obtained
zero checked successes in 128 bare attempts on each target. We can display the
actual lemma and two actual proofs. This would identify a specific useful
behavior for a subsequent training objective rewarding reusable discoveries.

## Frozen question and scope

Two synthetic integer recurrences start at `(1,0)` and repeatedly multiply by
`[[3,4],[2,3]]` or `[[2,3],[1,2]]`. The model sees the recursive definition and
is asked to state and prove an informative algebraic equality for arbitrary
iteration count. The downstream questions are hidden from that producer:

1. The first coordinate never becomes zero.
2. The two coordinates admit integer Bezout coefficients producing one.

The authored upper-bound lemmas preserve `x²-2y²=1` and `x²-3y²=1`, respectively.
These lemmas and their proofs are never placed in producer prompts. They are
not novel mathematics. The families are correlated instances of a quadratic
invariant; this is not evidence of broad cross-domain transfer. These tasks are
separate from October's determinant/rational-iteration panel. No old held-out
proof log selects tasks, constructs training data, or changes the old gates.

The producer and consumer can each be the pristine pinned DeepSeek-Prover-V1.5
SFT base or the existing completed C1 standard-GRPO checkpoint. No parameters
are updated. This tests whether useful intermediate interfaces can be elicited,
not whether a new training method learns them. A positive result justifies
designing that later training experiment; it does not establish a paradigm.

## Sampling and artifact selection

- Generate 16 producer candidates per world per producer model (64 total).
  Use seed 20261118 with deterministic request-specific offsets, temperature 1,
  top-p 1, no top-k, and at most 768 generated tokens.
- Select the first four kernel-valid candidates by generation index for each
  world/producer, without reading target success. Keep uninformative valid facts.
  Publish every proposal and rejection, not just chosen success cases.
- Bare baseline: 128 fresh attempts per target per consumer (1,024 total).
- Cross every selected artifact with both fixed consumers and both downstream
  targets in its world, 16 attempts each (at most 1,024).
- Authored invariant and irrelevant valid `n=n` lemma controls: 32 attempts per
  target per consumer per control (512 total).
- Maximum 2,624 model proposals; fewer if fewer valid artifacts exist. All
  consumer continuations have 512-token caps. Prompts are capped at 1,536 tokens.
  Count supplied tokens, generated tokens, verification calls, failed proposals,
  model loads, and retained allocation time. Helper proof text is supplied:
  it is additional information and inference work, not free capability gain.

Every consumer receives the exact same artifact bytes for a given candidate.
No routing to the best candidate or selection using the target is permitted.
We may highlight interesting completed pairs after reporting the full matrix;
that is descriptive discovery, not a post-selection significance claim.

The irrelevant lemma controls generic presence of an extra declaration, but
is not token-length matched. The authored lemma localizes producer versus
consumer failure; it is not a fair learned-method competitor. Baseline sampling
and helper discovery have different cost vectors; report them separately.

## The interesting outcome

The prespecified strong artifact is a **single model-produced lemma** for which
the GRPO consumer has at least 4 checked successes in 16 attempts on *each* of
the two downstream targets, while its bare baseline has 0/128 on both. Do not
declare this strong artifact if baseline zeros include verifier timeouts or
missing verdicts, or if the irrelevant-lemma control exceeds 1/32 on either
target. Report
the frozen-base consumer as a crossover, plus oracle/irrelevant controls. This
is a practical discovery threshold, not a significance test. Even 0/128 is
finite-sampling evidence, not proof that GRPO can never solve the problem.

If the baseline already solves these problems, report that honestly; do not
replace targets or invent a zero-baseline story. If authored lemmas help but
generated ones do not, abstraction creation is the identified bottleneck. If
even authored lemmas do not help, this instrument does not yet support the
consumer-execution prerequisite. Do not turn a null into repeated seed sweeps.

## Correctness and execution

Use the pinned upstream `verify_lean4_file` completeness predicate with exact
Mathlib/Aesop imports and production namespace opens. Only operational paths
are supplied explicitly. Verification is capped at 60 seconds per proposal,
shorter than historical 300-second runs, and equal across conditions. Report
timeouts distinctly; do not interpret them as mathematical invalidity.

An appended `#print axioms` audit requires a closed theorem using only `propext`,
`Classical.choice`, and `Quot.sound`. Reject `sorry`, extra declarations, and
unsupported metaprogramming through a conservative lexical gate. This gate is
an instrument restriction, not a general Lean sandbox, and its false-negative
possibility must be counted. Validate authored witnesses, `sorry`, and a fresh
untrusted axiom before model execution. No verifier acceptance source is edited.

Request one H200 for one hour under `def-zhijing`, held by the existing Python
keeper. Launch phases manually inside the allocation. Preserve partial outputs
if the time budget is exhausted; incomplete counts cannot be called pass@128.
Use at most eight Lean workers. No automatic allocation renewal or new training.

The user has explicitly redirected this small exploratory experiment from the
old execution-screen gate. The old gate remains mandatory for its own matched
training experiment, which this pilot neither runs nor redefines. This pilot
is an initial restricted producer-consumer instrument, not the broader
two-domain graph/representation crossover described in October.

## Research context

The existing October primary-source review remains the scientific background.
A November 18 check again located OpenAI's
[beneficial-RL study](https://alignment.openai.com/beneficial-rl/), which reports
transfer beyond directly trained tasks, and Anthropic's
[reward-seeker study](https://alignment.anthropic.com/2026/reward-seeker/), which
illustrates behavior transfer after RL. Neither demonstrates this lemma
mechanism. Their relevance is to test the behavior that transfers, rather than
infer it from reward improvement. No survey of competing novelty/exploration
methods was used to select this experiment.
