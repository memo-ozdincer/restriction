# Reversible circuit word compression: exposure beyond correctness bootstrapping

## Registered hypothesis (before pilot runs)

Ordinarily competent policy can minimize gate count through local edits, but
may consolidate only simple shrinking edits. Exposure to equally or less
efficient equivalent circuit words could teach voluntary neutral/expanding
restructurings, yielding lower gate counts on held-out ordinary roots. The
pilot is null if competence fails, if frozen held-out root score does not
improve, or if the improvement lacks the expected motif evidence. No finite
budget establishes that ordinary RL can *never* acquire a strategy.

### Exact environment and fixed experimental design

Four symbolic wires; all 12 directed CNOT gates (each gate is invertible),
unit gate cost. State is a word of at most 40 gates computing a fixed GF(2)
linear map. All contiguous replacements of input lengths 1..3 by distinct
output lengths 0..3 are generated mechanically by permutation equality,
over the complete 16-point input space. No-opt rewrite is allowed as a
separate unchanged move. A native action replaces one window with an exactly
equivalent word; length cap 40. Every accepted edit preserves semantics,
including temporarily expanding edits. No human-selected rewrite family or
reference-minimum circuit. Verify replay separately by binary-matrix
multiplication. Initial words are length 24 uniformly random gates; split
256 train, 64 validation, 128 hold-out by distinct exact target permutations
(fixed dataset seed 20261127, before training); no search for useful instances.
Held-out test uses eight stochastic rollouts per root from original words,
not supplied resets. Additional held-out length-32 set generated independently
with disjoint target permutations (diagnostic transfer to longer words).

A shared small stochastic linear-softmax policy scores 32 sampled legal
replacement candidates plus a no-op per decision; candidate proposals:
sample window uniformly among all input-length 1..3 windows, then uniformly
sample a distinct equivalent word from the full class; if no replacement,
or length exceeds cap, candidate is no-op. Uniform window sampling is the
fixed action interface in all arms, not uniform among all edit pairs. Features
are generic categorical raw local gate-pattern hashes and before/after word
lengths, no distance/solver values/future simulation or motif label. Identical
architecture and proposal mechanism in all arms. Fixed 24 decision horizon,
terminal reward 1+(40-final_word_length)/40, no intermediate score.
Sampled REINFORCE with group-standardized terminal returns (32 rollouts per
update from same training root), Adam learning rate .01. Because non-learning
random prefixes vary by rollout, centering is per original root group, not
per identical exposed state; the experiment is not exact GRPO.

Four paired initialization seeds 42..45. Common ordinary phase 300 updates.
Gate to fork: on untouched validation root words, at least 80% complete
with strictly reduced size, mean reduction at least 20%, averaged over
four rollouts/word. If a common seed fails report failed gate, do not run
its fork. Branch phase 900 additional updates: first 600 intervention,
last 300 ordinary for all. Every episode rewards valid semantics at terminal
from initialization, even if no reduction. Evaluate frozen baseline, phase
switch and final with independently seeded fixed validation/test rollout
streams; no held-out information changes training.

Arms:
* ordinary: all 24 learned actions.
* exposure: first six actions use uniformly sampled nonshortening proposals
  from 32 legal slots (or no-op), followed by 18 learned actions. Those
  six actions may preserve or enlarge the circuit; never improve gate
  count. After 600 updates restore 24 learned actions.
* entropy control: ordinary 24 decisions with softmax temperature 2 in
  first 600 updates, then 1. Controls extra exploration without changing
  start distribution. It receives more learned actions than exposure.
* frozen search control: evaluate common frozen policy with and without
  random nonshortening prefixes on held-out words, same action and sampling
  budgets as regular evaluation; does not train from exposed completion.

Match total episodes, action slots (including every reset step), candidate
proposal slots, verifier calls, optimizer steps; policy gradient decisions
are conservatively fewer during exposure. Explicitly count these and report
reset edits, gate length, terminal scores, motif counts. At no time can reset
work supply a free shorter word. Independent held-out evaluation: exact
full-word semantics for every trace, gate count, fraction strictly improved,
fraction of voluntary neutral/expanding edits followed within five steps
by a new running minimum (possible restructuring; not causal proof),
fraction of trajectories with such a motif, and cost-conditioned diagnostic.
Replay after removing neutral/expanding action choices (same mask in both
learners, same RNG/proposal slots) as a causal diagnostic only, not native
training. No assertion of mechanism solely from motif counts; a higher-quality
solution can still merely reflect access to higher reward. If baseline fails
competence or no transfer, report and stop rather than scale.

## Prelaunch smoke and scheduling

Local clang++ -O3 -std=c++17 -Wall -Wextra smoke (10+10+5 updates,
competence gate overridden only in smoke) verified 1,600 independent
replays and all 512 distinct target maps; 1,885 short words form 651
equivalence classes and 13,644 directed replacements. No smoke
performance is considered evidence. Debug partition already occupied
by independent job 2939388; use compute partition on the preferred
def-zhijing account rather than cancel or delay unrelated work.

## Results (2026-11-26)

Slurm job 2939396, def-zhijing/compute, node tri1203, 192 allocated
CPU cores, 16 seconds observed elapsed (2-second queue/startup),
exit 0:0. Four C++ worker processes (one per paired seed; whole-node
allocation is scheduler requirement). GNU C++ 12.3.1. Remote path
`/scratch/memoozd/rrl/alchemy-compression-20261127`. Repository HEAD
at staging 4bc8efb4fa2431366b185bf7c1dd8ddae33c3c0a, uncommitted
experiment sources; source hashes recorded in scheduler_evidence.txt.
Local/remote SHA-256 matches for all twelve seed result/data/trace files.
Dataset SHA-256 1c66a93709f34552a6bdea4a0549f710924234b46bdb62a3d10f5fecf9fe3699
identical for all seeds. No model beyond the small policy defined here.

All four common checkpoints pass the competence criterion: validation
mean 16.143 gates from 24, 100% reduced (initial untrained policy mean
39.098, none reduced). Every training episode is exactly equivalent
to its original function. 384,000 total verified training episodes,
9,216,000 action slots and 294,912,000 proposal draws (four common
phases plus 12 forked arms); 115,200 exposure phase reset slots per
seed (460,800 total): these are charged within the fixed action
horizon. Ordinary/entropy get more policy-gradient decisions, not
fewer. No performance claims use the smoke gate override.

Frozen held-out test means across four paired seeds, 128 distinct
target maps x 8 draws x 4 seeds = 4,096 episodes per arm:

| Policy | End of exposure phase (gate count) | Final (gate count) | Final, longer held-out words (32 initial gates) |
|---|---:|---:|---:|
| Common checkpoint (before fork) | 16.344 | — | — |
| Ordinary continued | 15.028 | **14.838** | 22.194 |
| Nonshortening reset exposure | 15.405 | 15.010 | 22.131 |
| High-temperature ordinary | 15.114 | 14.877 | **21.855** |

Frozen common policy with six random nonshortening steps at evaluation
(no exposure learning) produces mean 21.639 final gates. All four
random-start-trained policies are worse than their paired ordinary
controls on the primary frozen held-out metric. Long test is an
exploratory diagnostic; a tiny exposure gain over ordinary is also
beaten by the entropy control.

| Diagnostic on final held-out tests | Ordinary | Exposure | Entropy |
|---|---:|---:|---:|
| Nonshortening-edit motif fraction | 99.780% | 99.927% | 99.854% |
| Neutral non-noop edits per episode | 16.622 | 16.735 | 16.790 |
| Expanding edits per episode | 0.049 | 0.063 | 0.006 |
| Mean final gates with all nonshortening edits masked (same evaluation mask) | 17.229 | 17.215 | 17.229 |

Ordinary already learns many useful neutral restructuring moves, as
shown by similarly worsened gate count when unavailable at evaluation.
The motif measure is extremely saturated and not necessarily causal
by itself: a nonshortening edit followed by a new minimum within five
steps may be incidental, but the ablation checks joint utility of the
operation class, not a particular clever transformation. Ordinary and
exposure both depend on it and rarely expand. The intervention fails
the preregistered beyond-bootstrapping hypothesis at this budget; it
does not improve primary held-out cost nor introduce a distinctive
reusable strategy. Do not scale merely for significance.

`audit.py` independently replayed all 6,400 saved evaluation traces,
confirmed every individual edit and full trajectory mapping for all
16 inputs, checked exact dataset target disjointness, compared
recomputed motifs and checked aggregate counters. All 384,000 training
terminal circuits were checked via independent row-matrix verifier
inside the C++ runner, but individual training traces are not retained.
`summary.json` aggregates the compact seed evidence; raw per-seed
gate-cost histograms and policy parameters are in seed*.json, one
sampled trajectory per held-out root/evaluation in seed*.traces.jsonl.
`verified.json` records the independent replay counts.
