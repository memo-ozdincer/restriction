# Three-bit reversible terminal-reward learning pilot

Registered hypothesis: exposure to randomly initialized native permutations
provides successes unavailable from a fixed diameter-eight start, and
subsequent identity-start policy learning exploits that experience. Compare
root-only, uniform-only, uniform-to-root, near-only and near-to-root.
The near reset is a separate positive control: a 1..4 step random walk
from the target, no supplied trajectory or distance-based reward. All use
the same fixed target, 8-action limit, binary terminal reward, network,
initial weights, optimizer, rollout count and evaluation schedule. Switch
at 30% of training. Root evaluation uses only identity. One paired seed
is a discovery pilot, not a statistical replication or an LLM result.
The three-bit target is the lexicographically first permutation at exact
distance 8 from identity, certified by BFS; BFS distances are never
observations or rewards. A simple linear stochastic policy suffices to
test whether the learning procedure is viable, not to establish a general
capability claim. No reference action labels.

First result, seed 42, 300 batches of 128 episodes: root-only 0/512,
uniform-only 1/512, uniform-switch 0/512, near-only 5/512, near-switch
164/512. Near-switch remained at 0/512 at batch 225, then 1/512 at
250, 7/512 at 275, and 164/512 at 300. The switch was at batch 90.
All policies evaluated from identity only; training successes were
0,111,4,26753,3641. Active actions differ because success stops episodes,
but identical numbers of policy forward steps and sampled episodes.
The initial near-start sampler may reset to the goal after cancelling
moves. Follow-up hypothesis: excluding those already-solved starts still
allows delayed root transfer, showing that positive reward from actual
actions, rather than zero-action episodes, is sufficient. Same seed,
budget, optimizer and schedule with solved near resets resampled.

Exclusion follow-up produced near-switch 0/512 at step 300 (2/512 at
275), despite 3821 training wins. Both sampling distribution and random
stream changed. To distinguish a single lucky breakthrough from a
repeatable nonterminal-reset effect, run a prespecified paired seed
panel 42..49 for root, near-only and near-switch with both near-reset
variants. This is motivated by the sharp reversal, not by polishing
significance. Record whether each policy ever reaches >=10% root
success and when; this distinguishes latent transfer from occasional
one-off successes. No hyperparameter selection on these results.

Paired follow-up result: ordinary RL 0/512 at every checkpoint for all
eight seeds. No near-only policy exceeded 8/512 at any checkpoint.
Two switched runs crossed the prespecified 10% threshold: seed 42 with
solved resets allowed (164/512), seed 46 excluding solved resets
(129/512). The other 14 switched runs did not cross it. Thus zero-action
resets are not necessary for the phenomenon, but the delayed breakthrough
is rare and initialization-sensitive at this budget. This is a concrete
replication of the phenomenon, not a reliable improvement claim.
Results in seed_panel.json; reproduce with seed_panel.py.
