# Native freedom sorting-network audit

Preregistered before running: compare a fixed six-wire comparator interconnect
with eight links (five adjacent plus (0,3),(1,4),(2,5)), exact optimal
budget 12. The policy sees the current native binary-row set and chooses
comparators, with no solution shown. Each successful terminal state sorts
every binary row, hence all total-order inputs under the zero-one principle.
No distance, comparator utility, intermediate correctness, or reference
sequence enters the loss. Exact BFS is used independently to certify
difficulty and to furnish a diagnostic equal-distance reset control.

Hypotheses: random native comparator prefixes can expose terminal reward
without solution-derived starts; training on short (root-neighborhood),
medium, long and mixed prefix lengths tests whether broader coverage
is useful or whether easing dominates. Uniform reachable-state resets offer
a broad state-space comparator; equal-distance resets are an oracle-based
diagnostic and preserve shortest remaining length. Because the state evolves
monotonically, this latter class may have only the root. Compare each
continued reset regime with its 30% switch back to ordinary root training.
Time freedom (24/36 action horizon, then restore 12) supplies extra
opportunities without changing the exact sorted target, and combined
medium-reset/time freedom tests interaction. Also test macro granularity:
two independent primitive moves sampled from one observation, evaluated in
sequence and charged individually, then restore primitive observations and
action choice after 30% of training. This is a compositional action
granularity intervention, not a hand selected macro set or privileged
unpriced transition.

Policy: common linear softmax over binary row-presence features,
terminal-only REINFORCE with a batch mean baseline and Adam ascent.
All regimes use 300 optimizer steps and exactly 1,536 maximum primitive
action slots per update, batch size changes when budget 24 or 36
(using horizon 36 batch 42 gives only 1,512; instead use horizon 48
batch32 for exact match). Track actual active actions, policy calls,
reset generator actions, already-solved rejections and wall clocks.
Macros use half the decision calls and backpropagate each active primitive
log probability conditional on the pre-chunk observation; this differs
in granularity and compute, so report separately. Evaluation is independent
ordinary-root sampling, 12 primitive moves, no assistance, same policy.
Eight paired seeds 42..49 as an exploratory mechanism panel; no tuning.
Initial random-policy success probability is computed against the same
state distribution with exact dynamic programming. Report results across
fixed seeds and learning curves, not a guarantee of a universal method.

## Targeted follow-up registered after core panel

Core panel found the most productive ordinary-root transfer came from short
random walks despite far lower training success than longer random resets,
and switching off the best short regime reduced aggregate performance.
Hypothesis: useful reset geometry has a limited range; mixing easier states
can suppress credit for relevant earlier configurations rather than aid
learning. Discriminate by using walk maxima 2, 6, 8, and a mixed distribution
that draws half from 1..4 and half from 1..36. Same 300-update/primitive-slot
budget, paired seeds, continued/switch arms. To test whether additional
time unlocks same-distance learning or removes the need for short starts,
run equal-distance plus horizon24 and short plus horizon24, with and
without switch. These follow-up comparisons are motivated by the observed
short/long contrast and weak horizon-only result, not selection of a best
radius. Exact free-reset cost and actual actions remain recorded.

## Outcome

All 184 core runs and 96 follow-up runs completed normally. Each run had
300 updates, 1,536 padded primitive action slots/update (460,800 total),
11 checkpoint evaluations plus 512 fresh ordinary-root episodes.
Eight paired initializations in each arm. The exact graph holds 8,583
states; its shortest remaining distance histogram is
[1,5,24,132,551,1385,2256,2192,1309,544,156,26,2] for distances 0..12.
Only two states at exact distance 12, including the root, so equal-distance
variation is extremely limited in this irreversible environment.

| Initial reset (12-action budget) | Mean distance | Random policy hit % | Root wins, continued / 4096 | Root wins, switch / 4096 |
|---|---:|---:|---:|---:|
| Ordinary root | 12.000 | 0.0000323 | 0 | n/a |
| Tiny, 1..2 | 10.836 | 0.00218 | 0 | 0 |
| Short, 1..4 | 10.271 | 0.01968 | 1437 | 416 |
| Radius 1..6 | 9.742 | 0.09467 | 1575 | **2609** |
| Radius 1..8 | 9.249 | 0.30449 | 342 | 915 |
| Medium, 1..12 | 8.353 | 1.51582 | 107 | 441 |
| Long, 1..24 | 6.202 | 13.25935 | 0 | 0 |
| Wide, 1..36 | 5.078 | 24.65179 | 0 | 0 |
| Uniform reachable | 6.490 | 5.06628 | 0 | 0 |
| Equal-distance shell | 12.000 | 0.0001010 | 0 | 0 |
| Half short / half wide | 7.675 | 12.33574 | 543 | 54 |

The largest gain on this panel is **63.7%** final ordinary-root success
after radius-six exposure then root-only specialization, versus zero
ordinary baseline. This is not a robust optimum claim: radius six was
introduced after observing initial radius-four and radius-twelve results;
the same seeds were reused across the follow-up. This is an exploratory
mechanism finding, not a held-out hyperparameter estimate. Six of eight
radius-six switched policies exceed 10% final root success; final fresh
hits per seed [0,478,0,461,463,458,433,316]. Continued radius-six training
wins [0,367,0,347,336,0,342,183], so switching improves each previously successful policy and unlocks a
previously unsuccessful seed; two seeds remain at zero. In the radius-four
arm, switching is worse in aggregate than continuing.

| Alternative freedom | Continued root wins / 4096 | Switched root wins / 4096 |
|---|---:|---:|
| Root horizon24 | 32 | 30 |
| Root horizon48 | 0 | 0 |
| Medium reset+horizon24 | 1 | 2 |
| Equal-distance reset+horizon24 | 5 | 16 |
| Short reset+horizon24 | 9 | 9 |
| Root two-action granularity | 0 | 0 |
| Medium reset+two-action granularity | 80 | 3 |

Horizon 24 gives an untrained root hit chance of 6.243%; horizon 48 gives
80.759%. These do not transfer to optimal 12-action solving at this budget.
Long and wide resets and broad uniform starts provide 210k–236k training
wins across eight policies, but zero fresh root successes. Root-centered
short/radius-six states are therefore superior here despite much lower
training reward access. This differentiates reward availability from
useful sequential state coverage. There is no goal-centered random walk
control because every comparator leaves the sorted target unchanged.

## Independent audit

The fixed restricted comparator graph and terminal goal are unchanged
throughout. Every stored successful sequence is re-executed by an
independent scalar implementation over all 64 possible binary rows,
including exact 12-action length, and its multiplicity equals reported
fresh root wins. Radius-six switched finds 90 distinct successful root
sequences across seeds; continued finds 321. All reported root successes are verifier facts. Primitive action alphabet
never changes; macro granularity chooses two primitives from one
observation, costs both, and updates both log probabilities. It does not
test a learned macro vocabulary or extra primitive power.

| Requirement | Audit |
|---|---|
| No reference proof/network or process supervision | Pass: no witness sequence in policy or gradient; terminal correctness only. |
| Same native task at final evaluation | Pass: all arms evaluated from all 64 input rows with original 8 links, 12 actions and exact universal checker. |
| Same initial policy and optimizer | Pass: paired seeds, one linear softmax, same Adam and update count. |
| Native randomization indifferent to solution | Pass for random walks: uniform legal comparator draws, random lengths, exclude solved. Uniform reachable state sampling uses enumerated topology; equal-distance uses goal-distance oracle and is a labeled diagnostic, not a neutral scalable method. |
| Reset does not supply a trajectory/human action labels | Pass: only native row sets supplied, no prefix retained in the policy. |
| Training objective unchanged | Pass for resets and macro granularity; horizon24/48 explicitly relax count constraint in training and restore 12 for evaluation, so alternate-task comparison only. |
| Matched compute | Matched optimizer count and maximum policy primitive slots; actual active actions and reset generation differ, explicitly tracked; total environment transitions are NOT held constant. Horizon arms have fewer episodes and macro arms fewer policy forwards. |
| Final success checked and reproducible | Pass: every recorded fresh successful trace scalar-verified, seed/mode/config retained. Independent replay uses exact same task and 512 fresh draws per seed. |
| Evidence of delayed transfer | Descriptive: learning curves retained. No causal claim about semantic internal skills. Radius switch timing fixed at 30%; no selection on intermediate evaluation. |
| Established scope | One restricted interconnect task, one architecture, no LLM. No claim generalization to new tasks or robustness of best radius. |

Exact compute for radius-six switch across eight runs: 3,686,400 padded
primitive policy slots, 3,685,592 active policy actions, 322,854 reset
generation actions, 48,278 training wins, 3,686,400 policy forward calls.
Root-only: same padded slots/forward calls, 3,686,400 active actions,
zero reset actions and wins. This is about 8.7% additional active
transition simulation for the assisted method, not equal total
environment compute. For long/wide exposure additional reset compute
is greater but still no observed root wins. Results.json, followup.json,
audit.json contain complete per-mode/seed counters, checkpoints and
compact successful path evidence. Reproduction:
`python3 train.py`, `python3 followup.py`, `python3 audit.py`.

**Interpretation:** moderate, unselected root-neighborhood exposure can
produce significant optimal root-solving skill where ordinary terminal
RL encounters no initial positive rewards. Very broad/easy reset
coverage and generous time freedom do not provide the same benefit.
Mixing easy and root-near exposures harms the observed gain relative to
the best root-near regime. The result supports the user's radius/intended
start intuition on this task; the exact mechanism remains open, and
this panel does not demonstrate equal-distance exposure benefit.
