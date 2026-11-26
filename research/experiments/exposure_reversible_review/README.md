# Reversible synthesis: temporary time freedom versus state exposure

## Registered hypothesis (before smoke testing)

The earlier rare three-wire diameter-eight task has precisely six shortest
words. Native goal-centered resets produced millions of correct assisted
episodes but suppressed the exact root-path probability; a switch did not
recover it. See ../hard_reversible_bottleneck/README.md and three_task.json.
The earlier horizon panel used the different, easier diameter-eight target
with 622 shortest words (../freedom_reversible_new/README.md). Therefore
test time freedom on the *same prior rare target*, rather than extending a
failed reset-only run: longer legal root-origin trajectories can reach
reward through many more routes, which may teach useful structure that
near-goal snapshots alone did not expose. The limiting question is whether
that experience transfers to the original eight-gate acceptance criterion
after the horizon is restored. No additional action types, oracle advice,
target changes, rewards for progress, or supplied shortest words.

Target permutation fixed at (7,3,6,1,5,4,2,0), 3 wires, all 12 positive-
control NOT/CNOT/Toffoli gates. State is the exact permutation; same 64
one-hot features, linear categorical policy, centered binary REINFORCE,
Adam (.01,.9,.999), and initial weights as the previous rare task. Goal
equality gives one reward at first hit; all other rewards zero. Target is
fixed, but accepting longer correct circuits during assisted phase is a
temporary **resource relaxation**; report this as distinct from a
state-distribution intervention. At test all arms start at identity and
must hit target within eight legal primitive actions. No exact distances
enter reset selection, policy features, or training rewards.

## Arms

Fully crossed exposure source (identity root; legal 1..4 step uniform
goal-origin walk, excluding already solved starts) and training horizon
(8,16,32), each continued or switched to root/horizon 8 at 60% of training;
the identical root/8 arms collapse to a single control. Thus 11 arms.
Four paired seeds 42..45, 6,000 updates, 1,024 padded policy action slots per
update (128/64/32 episodes according to horizon). The original rare task
had 10,000 updates; this is a new mechanism screen, not an extension to
improve statistical power. Hold policy/update count and padded primitive
slots equal. Episode count/gradient variance differ by horizon; report
active executed actions, padded slots, episodes, mixed batches, terminal
wins, and pre-reset sampling cost separately. Same random number stream
initialization; streams diverge as horizon changes. Fixed goal-walk
distribution is precomputed by exact forward Markov propagation solely
under uniformly random gates, excluding the goal; count graph setup as
offline preprocessing and report it, no per-episode reset simulator
actions. This matches previous rare-task sampler semantics. Same policy
observations and action dynamics.

## Diagnostics and decision

Exactly enumerate the 40,320 native states and all transitions; certify
root distance 8 and six shortest paths (BFS). Independently compute the
exact finite-horizon root hitting probability for H=8,16,32 (offline
only). Shell-wide exact H=8 mean probability diagnoses where skill reaches
beyond practiced starts. Final ordinary fresh 512 episodes use an independent
scalar bit-gate replay, compared against indexed simulator. Track the first
ordinary reward after removing the intervention and exact H=8 probability
at fixed checkpoints.

If time-only root exposure succeeds at H=16/32 but cannot help the original
H=8 solve, then additional reward alone is insufficient. If combined
exposure succeeds where either source alone fails, report interaction,
not a single-mechanism causal claim. If a switched arm reaches >=10%
original root success in multiple seeds and the persistent assisted and
ordinary arms do not, that supports restoration-dependent transfer in
this specific task/architecture. If longer horizon merely increases
H=16/32 success without H=8, reject transfer. No post-hoc switch-time
selection or additional seeds just to improve significance.

CPU implementation is standalone NumPy/Python. Use
`OPENBLAS_NUM_THREADS=1 python3 run.py --out results --workers 16` for full
panel, or `python3 run.py --out /tmp/reversible-exposure-smoke --steps 2
--seeds 42 --workers 1` for smoke. Trillium quickstart: staged unique
directory, scipy-stack/2026a, def-zhijing, one full-node allocation if
parent authorizes; 44 independent full runs fit into a shared node.
No cluster submission by this implementation agent.

## Smoke result (mechanics only, no performance claim)

Four unit tests passed; sequential 2-update and parallel 3-update panels
both completed all 11 arms on seed42. The latter uses two worker processes.
The compact parallel smoke is saved in smoke.json. Every run consumed
3,072 padded training slots; independently replayed 512 final ordinary
evaluation calls. No root winners are expected at this tiny budget.

The exact *random-policy* root hit probabilities are H8 = 1.395408e-8,
H16 = 4.940141e-5, H32 = 3.493866e-4. This confirms the intervention creates
substantial previously inaccessible reward probability (roughly 25,000x
at H32) without state resets or solution information. By contrast, the
goal-walk-4 initial random-policy hit probabilities are 3.652%, 3.757%,
3.810%, so the time crutch provides a much stronger relative improvement
at the ordinary root. Final policy exact diagnostics use float64 softmax
on policy weights to avoid avoidable float32 underflow.

Independent reviewer caveat: the legacy rare-task optimizer centers reward
over the whole batch, including different reset states. "Mixed batches" here
are batch REINFORCE variation, not same-state GRPO groups; do not equate
them with GRPO signal or attribute changes to the optimizer. Horizons
16/32 also produce two/four times fewer episodes per update at matched
primitive slots, so the experiment measures the practical compute-matched
time freedom, with estimator variance as a confound. Exact hitting
diagnostics represent the mathematical float64 softmax, while training
and sample replay retain the earlier float32 sampler.
