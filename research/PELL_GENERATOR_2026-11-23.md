# Learn a witness generator, then use it beyond the demonstrated computations

## Expected interesting result

A trained model emits a short, self-contained program that repeatedly multiplies
a norm-one Pell unit until its first coordinate crosses the requested bound.
Lean executes and checks that program, producing a new large witness without
the prompt supplying an intermediate solution or the required iteration count.
We want this to work on unseen discriminants and bounds that require more
multiplications than any training example, where matched answer supervision and
the unchanged GRPO checkpoint fail.

The previous one-step expression adapter learned useful numerical transfer, but
depended on familiar names and supplied current coordinates. This experiment
changes the supervised object from a single multiplication expression to a
bounded conditional generator. All prompts are closed numerical goals, with no
global declaration names. The generated program chooses its own local names.
This removes that specific interface dependence; it does not prove general
renaming robustness. The generator is authored supervision, not model discovery.

## Fixed comparison

Start both adapters independently from the same final C1 GRPO checkpoint, as in
the separate Pell learning track. Preserve the original SFT/C3 experiments and
their conclusions. Eight training prompts: D=2,3,5,7, at unit powers two and three.
For each, the prompt supplies only the fundamental norm-one pair and requests a
solution whose positive first coordinate is strictly above the previous unit's
first coordinate and at most twice the fundamental first coordinate times that
bound. This upper bound prevents arbitrary overshooting. It is not the exact
answer. No iteration count or current second coordinate is supplied.

`literal` receives the computed final coordinates. `expression` (the existing
runner's arm name) receives a program with a conditional multiplication step and
a fixed eight-step Nat.rec budget, followed by norm_num and kernel decide. The program keeps the
state unchanged once it crosses the bound. Both demonstrations prove exactly
the same target and yield the same pair. All are kernel checked before training.
The program has more procedural information and may have more response tokens;
record the counts rather than claiming equal-information supervision.

Reuse the already executed Pell trainer unchanged: four epochs, eight examples,
32 steps per arm, response-mean likelihood, reference anchor coefficient 0.02,
rank-eight q/v LoRA, learning rate 1e-4, identical adapter initialization/order,
float32 computation. Preserve exact tokens, metrics, adapters and reference
checks. This is supervised learning on C1, not an online RL result.

## Frozen evaluation

Eight cells, each with 16 proposals for unchanged C1 and both adapters:

- New D=11,13 at powers two, four and six.
- Training D=3,7 at power six, to separate longer execution from new inputs.

The only supplied starting pairs are (10,3) and (649,180) for the unseen
discriminants. No completed test witness, previous full pair, or program is
supplied. Powers are authoring metadata, not prompt instructions. All test goals
are numerically distinct from training. Use the existing shared task-hash seed
rule, 20261203 plus SHA-256 task prefix, temperature/top-p one, cap 512 tokens.
The cap is increased uniformly for all three arms because a full program must
fit; no outcome-dependent retry. Total 384 proposals, one final checkpoint.

The desired result requires at least 8/16 accepted program-arm proofs on each
of the four new-D power-four/six cells, versus at most 1/16 for each control,
with all judgments resolved. Report all eight cells and actual complete proofs.
The fixed eight-step program budget is an authored capacity, not learned
unbounded iteration. Success would show reuse of a supervised conditional
construction across new numerical inputs and longer executions. It would not
show discovery of Pell theory, fundamental units, or a revolutionary paradigm.

## Execution and decision

Validate 32 positive demonstrations and 16 invalid controls on the fixed panel
before training. Use a bounded H100 keeper under def-zhijing with manual SSH and
terminal release. Commit the protocol and execution code before model outputs;
archive small adapters, every proposal, Lean verdict and source. Verify downloads.
Do not add seeds, adjust the fuel, or edit evaluation prompts after outcomes.
If program and literal supervision tie, the proposed program-supervision benefit
is unsupported. If only within-depth cells work, the longer-execution question
remains open; do not replace it with a claim about familiar calculations.

## Authoring correction

Before model sampling, Lean rejected the generator demonstrations because the
implicit Nat.rec motive could not be inferred without an expected type. Supply
`(motive := fun _ => ℤ × ℤ)` explicitly. This changes no mathematical task,
algorithm, fuel budget or experimental criterion. Preserve the first panel and
its invalid authoring proofs; validate the corrected panel separately.

The explicit motive resolves elaboration; norm_num alone then leaves the closed
Nat.rec computation unreduced. Appending kernel `decide` (not native_decide)
closes the diagnostic with only Quot.sound and propext. Apply that proof-tail
correction uniformly and preserve the second rejected panel as well.

For a successful program-learning interpretation, additionally take the first
accepted expression-arm proof on each of the four primary cells with exactly
one single-line Nat.rec assignment ending in a literal fuel value greater than
two. Replace only that fuel by two and recheck the unchanged continuation.
Require all four replays to reject without system errors, confirming dependence
on more steps than the training computations used. This adds at most four
checks, no new sampling. Unrecognized generated syntax is reported as unclassified,
not repaired or silently counted as evidence for the mechanism.
