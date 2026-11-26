# Task-family audit and early experiments

User goal, verbatim: "spawn subagents to audit task families and then try implementing, see what happens, etc.. We don't want to use super esoteric task types, we want ones where we can apply the magic of RL, random starts, or some other crutch removal, or training method. Ideal is obviously tasks that the model can't easily solve to start"

Three independent reviewers investigated and implemented distinct families.
The main thread also ran a terminal-reward policy learning pilot on one fixed
reversible circuit target. All experiments are local, with mechanically
verified terminal outcomes.

## Candidate families

- Sliding puzzle: ordinary 8-puzzle, exact 181,440-state BFS and diameter 31.
  A fixed distance-29 root failed in both models, while accessible nearer
  starts produced correct solutions. State is intrinsically changing.
  Excellent standard diagnostic, but little opportunity for genuinely new
  algorithm discovery over established search.
- Elementary row operations: Gaussian elimination in an invertible 3x3
  matrix over GF(3), 15 actions and 11,232 states. Exact diameter 7.
  Fixed hard target yielded Luna root 1/4, uniform 0/4, near 2/4. Terra
  4/4 in each. Every output was a substantive legal action sequence.
  Promising for Luna; larger matrices needed for Terra.
- Sorting network synthesis: state is the set of all possible binary rows
  after the current comparator transformations. Exact zero-one verification.
  Standard known optimum sizes 12 (six wires) and 25 (nine wires).
  Random legal comparator prefixes can compress the remaining state
  without any reference solution. Distinguish practice suffix cost from
  original full network cost. Established standard targets may be memorized.
- Reversible circuit: already established fixed state permutation, legal
  gates and terminal exact verification. Three-bit optimum-eight target
  selected by exhaustive BFS, rather than a known four-bit benchmark
  for this first small policy experiment.

## Actual learning result

The reversible pilot uses a linear stochastic policy and REINFORCE with
terminal binary reward, identical batch sizes and horizons. No reference
action labels or intermediate supervision. One fixed target for every
condition. In the exploratory seed 42 comparison, near-goal resets then
ordinary-only training reach 164/512 root successes after 300 batches;
ordinary-only remains zero. Near-only 5/512, uniform-only 1/512,
uniform-to-root zero. Switch occurs at batch 90, with the first large
gain after batch 275.

A targeted follow-up excludes already-solved resets. Seed 42 then fails
to reproduce its breakthrough. The paired seed panel (42..49) finds
another breakthrough with already-solved resets excluded: seed 46
reaches 129/512. Across 16 near-switch runs only two exceed 10% root
success; none of the eight root-only or sixteen near-only runs do.
The effect is rare, and sample distributions and random streams differ.
Independent replay reproduces both training records exactly and verifies
fresh 175/512 and 132/512 successes, with 9 and 6 distinct optimal
action sequences. These are small policy learning results, not LLM
fine-tuning. The causal mechanism and reliability remain unresolved.

## Artifacts

- [Reversible learning](experiments/reversible_learning/README.md)
- [Sliding puzzle](experiments/sliding_initial/README.md)
- [Row operations](experiments/rowops_initial/README.md)
- [Sorting network](experiments/sorting_initial/README.md)

All primary sources and detailed setup instructions are retained in the
individual experiment notes. Frozen model attempts are small exploratory
samples. Uniform resets and near-goal resets are distinct interventions.
