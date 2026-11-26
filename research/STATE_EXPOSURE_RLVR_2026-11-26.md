# State-exposure RLVR: expand experience, not supervision

Discussion, November 26, 2026. Continuation of
[Intrinsic hindsight](INTRINSIC_HINDSIGHT_PROPOSAL_2026-11-25.md) and
Supervision Through a Straw. This document records the user's physical-
environment observation and three independent design critiques. No literature
novelty assessment was requested; reviewers were expressly instructed not
to assess novelty. No new experiments or training were launched.

## User idea-dump, verbatim

> I was talking to some agents I was running physical experiments with, we actually started getting good results from this super complicated training method, but I realized something. I think all the gains are actually from just letting the models be exposed to MORE of the environment than their naive counterparts.
>
> This is a minor advantage when talking about simple tasks, but a MASSIVE advantage when talking about tasks where the model can't get good gradients from scratch (its too low probability).
>
> example set 1: now, this has the issue that its complicated, we're changing A LOT. Still useful, but I don't know what to make of it YET!
> Yes. Valley landing is the cleanest non-slalom example of crutch removal itself. Two others stand out for different reasons.
>
> | Experiment | What the crutch did | What happened on fresh cases |
> |---|---|---|
> | Valley landing | First accept a landing with excess speed, then remove that tolerance and require the real precision landing. The intermediate tolerance was fixed before the test. | At 512 pass/fail queries, removal won 336/768 paired searches versus 255/768 for direct search. 116 wins were unique to removal; 35 were unique to direct. These were 24 fresh throttle scripts with 32 search seeds each, so the 768 trials share 24 underlying setups. Paired trials |
> | Timed-door mazes | Plan with doors open and eight fake passages, then use real moves to discover which crossings need repair. | At 1,000 queries, the assisted planner solved 300/300 fresh mazes. A real-only planner using the same failure and checkpoint-reuse rule solved 168; real bidirectional search solved 101. So 132 mazes were solved that the matched real-only planner missed. The advantage here is that the relaxed map still contains useful geometry, and a failed crossing can establish a reusable fact. Course records |
> | Pinball with hidden checkpoints | Start with a legal prefix and an imagined ending, then replace pieces of that ending with real maneuvers. | On 24 fresh cases, keeping intermediate maneuvers solved 21 versus 17 when the same driver discarded them. In three of the four extra wins, replay confirmed that the final solution actually reused an intermediate maneuver. Replay audit · Visual replay |
>
> I’d show the pinball result first. Valley gives the cleanest test against direct search, and the maze gives the largest margin against systematic baselines. But pinball most closely matches your original idea: the cheating trajectory says the finish is possible from here; the real trajectory gradually takes over. We can point to the exact 60 legal frames retained in a winning run and watch the imagined ending shrink.
>
>
> This, on the other hand is much simpler (example set 2). 1 - let the first agent only explore using normal rl evolution; 2 - let the second agent start from a random state and get to the end. THE STATE INPUTS ITS GETTING ARE THE SAME!!! Its transferable skills. You don't need a continuous trajectory (at least in that case), you need to learn the rules of the game!
>
> So, perhaps yes, its better to teach it the full trajectory, maybe its good to just teach it from EVERY slice of the data, where it can learn a bunch of different positions? Kind of like pretraining, only for RL.
> 1. Random-start training beat 2. Entrance-only training, even when both were tested from the real entrance.
>
> I used evolutionary selection on the same pinball board. The only reward was reaching the hole within 600 frames. Both groups had the same controller, controls, and training budget. Only the starting position changed. Every ball started at rest.
>
> | Fresh replication | 1. Random legal starts | 2. Entrance only |
> |---|---:|---:|
> | Finishes during training | 15,850 / 81,920 | 673 / 81,920 |
> | Finishes when tested from the real entrance | 92 / 2,048 (4.49%) | 42 / 2,048 (2.05%) |
> | Trained controllers that finished at least once from the entrance | 39 / 64 | 16 / 64 |
>
> The initial pilot also favored random starts, 17 vs. 9 entrance finishes. In the larger replication, the improvement was 2.44 percentage points; the 95% interval across paired training seeds was 0.88 to 4.00 points. Results chart · Verified counts
>
> Your intuition held up on this board: changing where practice began made terminal reward much easier to encounter, and some of that benefit carried back to the entrance. Entrance-only evolution did sometimes get lucky, and both groups still failed most entrance attempts. The experiment shows transfer; it leaves open whether the policy learned the route backward from the hole or picked up more generally useful steering.
>   Worked for 3m 33s • 11:59 PM
>
> it gets the current state as input right thats why it workedd?
>
> Yes. At each decision, the controller sees the ball’s current position, current velocity, and time remaining. It has no memory and gets no label saying where the run started. If a run from the entrance reaches the same state it encountered during random-start practice, the controller uses the same steering policy there.
>
> That gives a plausible explanation for how practice transferred. We know random starts improved entrance performance. Both groups saw the current state, though, so the experiment didn’t isolate state input as the cause or establish exactly which steering behaviors transferred.
>   Worked for 6s • 12:05 AM
>
> can i see a comparison of path heatmaps on the game map side by side please?
>
> I’ll replay both sets of trained controllers from the real entrance and plot where the balls spent time, using the same map and color scale side by side.
> • Exited (status 7) cd /Users/memoozdincer/Documents/hello123/game && ls runs/pinball-start-di…
>   └         generations.append(dict(hits=int(hits.sum()),best=int(scores.max()),different=bool…
>             champion=pop[order[0]].copy()
>     000
> • Ran cat > runs/pinball-start-distribution-02/path_heatmaps.py <<'PY' …
>   └ replayed [42, 92] finishes; [1222608, 1215364] frames
> • Ran sips -Z 790 runs/pinball-start-distribution-02/path_heatmaps.png --out /tmp/pinball-heat…
>   └ Warning: Output file suffix should be png
> • Viewed image pinball-heatmap-preview.jpg
> • Used computer · 2 actions
>   ├ Opening the heatmap comparison
>   └ Displaying both pinball heatmaps
> ::browser-complete{title="Displayed side-by-side pinball heatmaps"}
> Opened the side-by-side path heatmaps in Arc. Left: entrance-only training. Right: random-start training. All 2,048 test runs per group began at the same bottom-left ×. The turquoise circle near the top is the hole.
>
> Brighter colors mean the ball spent more time there, on the same logarithmic scale. Both groups spent much of their time near the entrance and in the lower corridors. Their overall coverage looks similar, even though random-start training reached the hole 92 times versus 42.
>
>
> What do you think?

> Okay. Now, how do we give the model access to larger parts of the mathematical environment (or code environment, or game environment, or whatever), such that it still has the same exact environment and in fact the same exact goal, but with access to much more of the environment. You understand? Lets ask the subagents what they think, while preserving the magic of rl. Don't ask them if its scooped.

> they should highlight which requirements are most important too to maintain magic of RL

The physical experiment figures above are user-provided reports, not
independently verified results within this Lean repository.

## Convergent position of all three independent reviewers

**Change where experience begins, not what constitutes successful action.**
The same terminal objective, transition dynamics, verifier and observation
interface apply. Change only the sampling distribution over starting
states (or explicitly disclose any other intervention). This distributes
RL experience across the environment, rather than trying to prescribe
a Eureka object.

The most compelling clean mechanism is **certified native state resets**:
the model or an ordinary explorer obtains intermediate states via legal
actions, stores exact states and their original-root prefix certificates,
and samples new continuations from them. Visit a rare state once and
practice from it many times; new continuations can reach even further
states. Neither the experimenter nor a reward model selects useful
mathematical conclusions.

This changes the expected training return from
E[R | original start] to E_{s~μ}[R | s], despite the same terminal
reward predicate. It is a state-distribution intervention, not
literally identical initial-state MDP distribution. The original-root
test is still unchanged. A state being legal in general does not
guarantee it is reachable from the original start within the original
horizon. That boundary is particularly important in mathematics.

## Ranked requirements

Each reviewer independently ranked terminal objective purity,
state authenticity, no externally prescribed mathematical content,
ordinary action/observation parity, resource/credit accounting and
unassisted transfer. The reconciled order follows:

| Priority | Requirement | Concrete failure to avoid |
|---|---|---|
| 1 | **Exact original terminal condition and dynamics.** No intermediate reward; final task closure under unchanged original rules. | Reward solving only a local subgoal, change the theorem/test/physics, waive a pending obligation. |
| 2 | **Authentic root-derived states.** Exact native snapshot with legal replay certificate from the same original task. | Fabricated Lean assumptions, authored correct partial code, arbitrary unreachable state claimed as legal root continuation. |
| 3 | **Endogenous, outcome-neutral access.** No author-defined useful objects, demonstrations or semantic progress ranking; archive both failed and successful trajectories. | Supply only prefixes from completed proofs, select by known suffix success, inject handpicked invariants. |
| 4 | **Same native observation and legal action interface.** No reset label or extra advice; preserve hidden state and remaining task resources, not merely printed context. | Root-only model gets less verifier feedback; reset agent gains extra time or sees prior solution; state reconstruction omits local instances/metavars. |
| 5 | **Pure sampled-action credit.** Terminal reward credits actual newly sampled actions; old prefix is state provenance, not a supervised target or newly sampled policy trajectory. | Train on archived prefix as if current actor generated it; manufacture GRPO contrast by mixing root difficulty. |
| 6 | **Honest cost and split accounting.** Charge exploration, replay, failed attempts and continuations; archive training-only states; no free suffix samples. | Extra compute, reuse of evaluation roots, hidden archive selection. |
| 7 | **Independent root transfer.** Same ordinary unassisted evaluation on fresh tasks/families; reset archive unavailable at evaluation. | Treat solving easier suffixes as proof of improved root ability. |

These are non-compensatory design gates (1–6) and an empirical test (7),
not a score or reward function. One cannot guarantee that more state
exposure generates useful learning or that root-only ability improves.
The user prioritizes preserving the magic of RL and generalizable skill,
not artificially maximizing visits to particular states.

## Reviewer-specific proposals

### Reviewer 1 — RL objective and learning attribution

Sample naturally reached, valid nonterminal states including states on
failed trajectories, archive immutable prefix certificates, and train
fresh suffixes. The prefix must not receive retroactive policy-gradient
credit as if the learner had generated it. For group-relative RL, draw
independent suffixes from the **same sampled reset state** in a group.
Grouping starts at different depths/difficulty for one theorem can
manufacture advantages due to starting conditions rather than action
choices. Audit mixed groups, saturation, actual nonzero suffix action
advantages and root-only transfer. Root/reset mixture and snapshot
distribution are declared intervention choices, not designed mathematical
targets. Nothing guarantees suffix training transfers to early decisions;
parameter sharing and context representation make transfer plausible,
not inevitable.

### Reviewer 2 — Math/Lean semantics and state authenticity

A saved state must include exact replayable source/actions, native goal
stack, hypotheses, local instances, metavariable assignments/constraints,
environment/version/options and all live obligations. Merely saving
a printed focused subgoal is not enough. Root terminal acceptance requires
the actual archived prefix plus newly sampled actions to reconstruct
the unchanged original theorem and pass unchanged kernel/axiom checks.
Do not introduce hypotheses simply because they look like valid
mathematics. Such hypotheses are unearned unless there is a legal
prefix establishing them. Root budget/remaining horizon is part of
state: do not reset time, tokens or actions at the checkpoint if that
would grant a larger original-task horizon.

Three progressively stronger mechanisms:
1. Natural snapshot reservoir from one frozen actor's own ordinary
   trajectories, including failures (clean first diagnostic).
2. Reset training on a fixed bank of these states, same model and
   interactive interface as root-only control (minimal learning contrast).
3. Recursive exploration from previously discovered snapshots, retaining
   legitimate further states. Can reach very rare parts of environment
   without regenerating the entire prefix on every visit. Archive
   eligibility is structural legality rather than perceived promise.
   Additional stochastic explorer/temperature/model is a distinct
   intervention and must be matched/declared, not hidden as a new state.

There is no uniform distribution over the infinite space of possible
Lean proof states. Uniform sampling over a finite model-generated bank
(or task-balanced uniform sampling, which differs) is a declared neutral
operational distribution, not exhaustive access to mathematics. Sampling
every legal state observed avoids human-directed usefulness filters; archive
capacity and duplicate handling still define a sampling distribution.

### Reviewer 3 — Experimental falsification

A frozen actor diagnostic compares real-root and archived-state
continuations on the same goals, at predeclared matched aggregate
resources. Count terminally complete roots, mixed GRPO groups and
nonzero advantage-eligible actions. Preserve complete relevant context;
the root control must have the exact same interactive Lean state
observation, action granularity and feedback. A one-shot whole-proof
baseline versus interactive state-reset treatment would confound the
mechanism.

Frozen diagnostic tests access to the reward, not learning. The learning
contrast starts from identical checkpoint, uses terminal-only RL and
same total collection/training resources. Root-only versus a declared
root/reset mixture. Evaluate both from original root on fresh theorem
families without archive. Team assistance or suffix performance does
not establish ordinary mathematical competence. Access to alternative
states could merely bypass hard decisions without learning those decisions.

## Generalization across environments

| Environment | Authentic state | Original terminal condition |
|---|---|---|
| Game | Full simulator state, position, velocity, time/checkpoint history, latent RNG, unchanged physics, optional original-start replay certificate | Reach same finish/goal under same rules and horizon |
| Code | Model-originated repository/worktree snapshot plus original task/tests and current runtime state if relevant | Original complete task passes same verifier/tests |
| Lean | Native proof state with exact legal prefix establishing its local context, all live obligations and constraints | Complete unchanged original theorem with allowed axioms |

A random rest position in a game might be legal as a simulator reset
yet unreachable from the original start within its horizon. That is a
valid **broadened initial distribution** experiment but not a
root-certified reachability experiment. Likewise, allowing arbitrary
mathematical problems/contexts from other theorems changes training task
distribution. Neither is necessarily scientifically useless, but neither
should be presented as preserving the precise original root task.

## Minimal experimental sequence, not yet registered

1. Frozen diagnostic: authenticated states from one model's ordinary
   rollouts on a fixed training panel, sampled without inspecting outcome.
   Verify all prior prefix actions and outstanding obligations. Independent
   root-start and reset-start completions, same native state/action interface;
   compare actual costs, mixed outcomes and reachable terminal success.
2. If diagnostic demonstrates a genuinely richer reward-access regime,
   preregister same-checkpoint root-only vs state-exposure terminal RL.
   Equal aggregate sampling/training resources and test protocol; no
   supervised suffix/prefix targets. Measure original-root transfer on
   disjoint theorems, not just convergence from advanced states.
3. Recursive archive exploration is a later distinct mechanism motivated
   if static archive coverage limits learning. It cannot explore truly
   illegal states without altering dynamics, but a valid prefix first
   encountered rarely can expose repeated fresh downstream exploration.

Original hypothesis: sparse-reward bottleneck is restricted exposure to
native states. Reward purity is unchanged; increase the probability
of observing a terminal-reward contrast from states the current root
policy rarely reaches. The decisive empirical finding is improved
unassisted root solving after this broader experience, not the trivially
easier completion of shorter suffixes. No guaranteed outcome asserted.

## User idea-dump, verbatim: environment augmentation

> okay. cool. so kind of "come up with a methodology of taking one RL task (or whatever, proof requirement), and making that into a significantly more interesting training sample by just adding bullshit on top of it and starting the model from there

> see if the agents can come up with another way, perhaps more natural to the pinball random start. also have one see if this environment branching idea has been scooped i'm not sure if its interesting or not yet

## Two independent design reviews: generate new legal states, not merely replay old ones

Both reviewers suggest a genuinely distinct **generative state sampler**:
sample a native partial proof certificate from a general typed grammar or
randomized legal action generator, retain its authenticated full open state,
and start the learner there. The sampled state need never have been visited
by the actor; it need only have a genuine valid connection to the original
theorem. No author selects which its mathematical content should be.

### Candidate mechanisms (not ranked by observed performance)

| Mechanism | What changes at reset | Important caveat |
|---|---|---|
| Random typed local object enrichment | Generate t using ordinary available locals/library/typed expression grammar, infer A from t, Lean-check, introduce `have h : A := t` or `let h : A := t`, retain original G. | Gives the actor mathematically established content, but generic random generator has no target-specific usefulness filter. It is environment-produced reset assistance, not zero additional information. |
| Random structural transformations | Apply valid intro/revert/generalize/change/cases/constructor operations or equivalent native transformations. | Preserves root and native proof obligations, but may mainly alter representation instead of unlocking new mathematical work. A handpicked tactic grammar is still an explicit distribution choice. |
| Random native partial-proof skeleton | A generative typed grammar proposes partial terms/actions from root, elaborates them with native metavariables, exposes every open goal. | May do part of a proof before reset; no known successful suffix used. Every hole and witness constraint remains, root terminal check unchanged. |
| Random case conditioning | Sample arbitrary P, execute native `by_cases h : P`, exposing either conditional world and retaining other branch. | No true fact supplied for free; completing only one branch does not complete root. May add work rather than improve accessible reward. |
| Random deferred cut | Sample arbitrary P, native cut leaves Γ,P ⊢ G and Γ ⊢ P. | Sound but a random P may be irrelevant/unprovable. All obligations still required; no evidence of better reward access. |

Reviewer 1 favors certified independently generated native states and
reversible transformations; Reviewer 2 prioritizes structural-only and
partial-proof skeleton sampling as clean no-proved-content analogues,
with random typed objects as a richer distinct variant.

In particular, typed local object enrichment is close to the user's
"adding bullshit" formulation. An illustrative context with locals
x,y:Nat can admit naturally checked term `Nat.add_comm x y` and its
inferred equality; the generator's sampling law, not an experimenter,
chooses that term. This example is explanatory, not an authored training
fixture or recommended invariant. Arbitrary well-typed terms can yield
proofs, witnesses, definitions, functions, identities or duplicates.
Randomly generated syntax may fail elaboration; charge failures, no
semantic selection or hidden retry. A typed grammar may improve syntactic
admission rate, but its vocabulary/depth/branch count are explicit
environment-sampling design choices. No goal relevance, terminal success,
expected utility, proof novelty or "interestingness" filters in primary
proposal. Preserve ordinary Lean observation/action interface.

A Lean state contains a partial derivation, unlike a ball position sampled
from a geometric domain. There is a strict conservation rule: a local
mathematical truth must be justified by a valid term from the original
context, or be an obligation that is discharged later. A free arbitrary
hypothesis changes the theorem. Sampling a partially solved native state
is distinct from selecting an existing successful proof prefix; it still
supplies an intermediate state through prior mathematical work. A
mechanical generator can supply a replay/term certificate without being
a second reasoning policy. There is no uniform measure over all possible
mathematical states, so "random" must name a concrete distribution.

For state-defined coding tasks, generic random edits of the same
working tree can sample legal task configurations while protecting original
tests; this does not claim a correct solution was supplied. For games,
sample position/velocity/time and latent state according to the original
physics legality; root reachability must be certified only where original
task semantics depend on it. Unreachable legal starts are a broadened
initial distribution, not unchanged original-root trajectory.

## Requested prior-art audit (third reviewer, primary sources)

**General restart/branching and terminal suffix RL are strongly anticipated.
Do not present those ideas alone as new.** The closest works:

- [Reverse Curriculum Generation, Florensa et al. (2017)](https://proceedings.mlr.press/v78/florensa17a.html):
  resets around known goal and expands states by random actions,
  success-based frontier selection, no demonstration requirement.
  Direct relevance to sparse-reward game random starts.
- [Exploring Restart Distributions, Tavakoli et al. (2018/2020)](https://arxiv.org/html/1811.11298v3):
  mixture of original starts and archived states, including uniform
  restart, on-policy RL and original-start evaluation. Explicitly
  discusses changed optimal policy under limited capacity. Ordinary
  outcome-neutral snapshot reservoir already has substantial precedent.
- [Go-Exploit, Trudeau and Bowling (2023)](https://www.ifaamas.org/Proceedings/aamas2023/pdfs/p842.pdf):
  starts self-play from state archive, includes search-tree states, explores
  new deeper positions, improves sample efficiency in Connect Four/9x9 Go.
  AlphaZero policy/value targets differ from pure terminal GRPO.
- [Sample Efficient Deep RL via Local Planning (2023)](https://arxiv.org/abs/2301.12579):
  restarts from previously visited high-uncertainty states for exploration;
  not neutral-state sampling.
- [PrefixRL, Setlur et al. (2026)](https://arxiv.org/html/2601.18795v1):
  the most direct threat to the generic RLVR idea. Conditions fresh
  on-policy continuations on old successful self-generated prefixes,
  masks prefix gradients and optimizes terminal outcome. Reports
  back-generalization to unprefixed tasks even from training only on
  prefixed ones, novel learned strategies, compute-efficiency gains.
  Successful-prefix selection differs from generative neutral states
  and from including failed paths, but the broad mechanism is established.
- [ReST-RL, latest v4 (Nov 2026)](https://arxiv.org/html/2508.19576):
  reshapes GRPO trajectory distribution via reward-variance filtering and
  prefixes of high-reward self-generated anchors for coding; partial-only
  control improves both reported coding scores. Not strict binary
  root-only proof reward, and not neutral random state augmentation.
- [DeepSeek-Prover-V1.5, §3](https://arxiv.org/html/2408.08152v1):
  truncate/resume from native partial proofs for RMaxTS search. Do not
  assert its described RL training specifically uses random failed
  prefix resets; its search mechanism is nevertheless highly relevant.
- [Kimina-Prover team release, July 2025](https://huggingface.co/blog/project-numina/kimina-prover):
  closest to context enrichment: prepends random subsets of 1–3
  generated formal lemmas in RL inputs. Crucially it explicitly shapes
  reward for using those lemmas, with subsequent usefulness-based
  filtering/search. This is not our indifferent root-only sampler.
  Earlier [preview technical report](https://arxiv.org/abs/2504.11354)
  is a separate version; do not conflate. Their release also discusses
  randomized proof cuts from human-annotated solutions.
- [NanoProof, §3.5 (2026)](https://arxiv.org/html/2610.11605v1):
  random renaming and shuffling of hypotheses/goals in proof-edge replay.
  This is semantics-preserving representation augmentation, not adding
  new independently generated typed objects; training includes proof
  search/expert replay and supervised mix.
- [DS-Prover, §3.3](https://arxiv.org/html/2312.14188):
  creates further legal tactic states by decomposing multi-premise
  rewrite/simplification steps; supervised tactic generation, not pure
  binary root RL.
- [Prefix-GRPO (2607.19395)](https://arxiv.org/abs/2607.19395):
  teacher-prefix reset and online continuation, historical-prefix
  gradient updates. **Withdrawn Nov 6, 2026 due to evaluation error**;
  not empirical evidence of benefit.

Targeted searches did not identify a direct primary experiment on
independently, generically generated random verified **extra local
objects** or arbitrary native partial proof skeletons, for the same
original Lean root with no relevance selection and pure binary terminal
RLVR, followed by unaugmented held-out proving. This is not an exhaustive
novelty claim. The most promising distinguishing question, if the
mechanism is useful, is generated mathematical experiences beyond
successful-prefix replay. Mere use of random restarts, recursive archives,
proof prefix continuation or return-then-explore is insufficient.

## Design judgement

The cleanest high-risk next concept is a target-indifferent native typed
object/partial-state generator, not a useful-lemma recommender.
It can directly expand conditions the model experiences while the original
theorem remains fixed. It could also generate mostly useless states,
or make proofs harder. A cheap frozen screen of reward-access coverage
versus original starts and matched self-prefix resets would determine
whether this variant deserves training, with no author-selected helpful
contexts. Do not register or run until a precise hypothesis and budget
are chosen. The user's design rubric still holds; no use of extra fact
is rewarded. No experiment was run.

## User idea-dump, verbatim: slice-first then whole-task training

> you know what? I don't care. I really like my original idea, and we're going to do it, because I know that I can come up with better ideas than these papers.
>
> We're going to take real math proofs, and start proofs from slices of them rather than the full thing, and come up with a training method that works much better.
>
> In pinball, The **generation-60 switch produced a huge, delayed jump**. At the switch, those controllers won **7.2%** of full runs from the regular entrance. Forty generations later they were still at **7.5%**. Then they reached **21.1% at generation 150** and **56.2% at generation 200**. That last stretch took them from **216 to 575 wins out of 1,024 attempts** in just 50 generations. Over the same stretch, regular-only went from **26.4% to 24.3%**, and random-only from **8.6% to 9.1%**.
>
> Six of the eight switched controllers improved during that jump. One went from **9/128 to 97/128** wins, another from **26/128 to 123/128**, and a third from **21/128 to 115/128**. The gain held: the group was still at **56.6% at generation 250** and finished at **82.3% on fresh tests**, versus **49.4%** for regular-only and **10.1%** for random-only.
>
> What I find most interesting is that **at generation 150, regular-only was still ahead of the fixed switch**. Fifty generations later, the switched group was winning more than twice as often. The adaptive switch showed a similar surge, from **28.9% to 55.9%**. That supports the idea that early random-start experience can pay off *later*, once evolution specializes on the full run. These eight seeds leave open which skills transferred and whether 60 is the best time to switch. [Training curves](/Users/memoozdincer/Documents/hello123/game/runs/pinball-long-switch-01/switch-curves.png).
>
> Doing random first, then switching to full had a massive training efficiency difference. Dunno if that has been done for example in the papers, check.
>
> My hypothesis is that we can teach some insanely intractable capabilities sending them to mid-distribution, and then refine the crap out of that going full distribution.
>
> And EVEN CRAZIER if the model couldn't do the full solution at the start, that means we literally COULDN"T have trained it on full distribution beforehand.

> We'll just be aware of the papers, and try, as we develop the idea, to not get scooped.
>
> Also, partial solutions isn't the way I wanna go because I want mine to be applicable to problems that the model can't solve on its own yet too.

### Physical result readback

Read-only inspection of the separate pinball experiment directory
`/Users/memoozdincer/Documents/hello123/game/runs/pinball-long-switch-01`
authenticated the reported stage and final counts in its design, result,
and 8 per-seed fixed60 files. No simulation was rerun and this is not new
independent causal evidence. The 8 training seeds are the units, not 2,048
independent training replicates.

| Generation | Fixed60 full entrance wins / 1024 | Mean rate |
|---|---:|---:|
| 60 | 74 | 7.23% |
| 100 | 77 | 7.52% |
| 150 | 216 | 21.09% |
| 200 | 575 | 56.15% |
| 250 | 580 | 56.64% |

Fresh tests, 256 episodes per seed: fixed60 1685/2048 (82.28%),
regular 1011/2048 (49.37%), random 207/2048 (10.11%), adaptive
1446/2048 (70.61%). Fixed60 improves in 6/8 seeds from generation 150
to 200. Study script changes only reset sampling at generation 60 in
fixed arm; adaptive uses its predeclared training-rate growth criterion,
switches at 40–100. These are evolutionary selection results with
binary end reward; not evidence of the same effect under GRPO.

External operational source/artifact provenance (read-only):
- design.json b6ac23c74a96805bff28b71d88a35e36590dfea4992752248a51658cb171dc1d
- results.json ba32d09a822be81a01f8dd67c2184ce4ef2cde93179570023856f0c8862f021f
- study.py 41f2c898506195de6c0db95ee759909f34c1a7a4e1775dadcfd279630df4166b
- report.py 1e049f27d5f7688895c1c47a89c2096a3a523dffe5d6150b5d7cf0336d453d1e
- switch-curves.png 27fa750b98bee6453366f0e85558e6340003174b4df4f10dc156a60734269eb2

## Targeted schedule prior-art check

The user wants the idea developed on its merits, with awareness of prior
methods rather than letting precedent terminate the research. Relevant
papers do use reverse/annealed schedules; exact abrupt switching plus
delayed transfer in a native Lean state curriculum is not established
as new by this search.

- [R³, Xi et al., ICML 2024](https://proceedings.mlr.press/v235/xi24a.html):
  outcome-driven PPO starts close to the end of verified demonstrations,
  progressively moves backwards. Table 2 of paper compares staged vs
  mixed-stage: on GSM8K 44.67 ordinary RL, 47.69 staged, 50.49 R³ mixed;
  on SVAMP 57.30, 61.00, 64.40. Mean across eight tasks 61.48,62.81,65.62.
  Mixed-stage beats sequential stages on their panel; do not assume a
  fixed switch always preferable. No Lean-native state-only intervention.
- [PrefixRL §4.1](https://arxiv.org/html/2601.18795v1): training ONLY on
  prefixed tasks can improve no-prefix accuracy. Long prefixes delay
  transfer (up to 800 iterations reported); closely relevant to the
  latent-skills hypothesis. Their main practical method mixes fixed
  preselected prefix lengths/unprefixed tasks. Prefixes derived from
  successful model-generated traces, so that construction is not directly
  useful when no successful sample is available at all. Do not mistake
  this for an abrupt slice-only to root-only switch experiment.
- [AdaPrefix-GRPO §4.2](https://arxiv.org/html/2607.07674v1): three stages
  (calibrate, adapt prefix length towards ~50% success, anneal assistance
  to zero), reference solutions by default. Last ~20% decays cap to zero,
  all evaluation unprefixed. This is very close to slice-first then
  full, but gradual/adaptive and text-prefix conditioned, not abrupt
  schedule from native complete Lean states. Controls against fixed
  prefixes and standard RL. Calibration/difficulty probe excluded from
  reported training compute, so must not claim fully matched acquisition
  cost. Study reports gains on initially dead groups.
- [Prefix-RFT](https://arxiv.org/abs/2507.01679): cosine-decaying sampled
  expert prefix, hybrid imitation and RL; not pure terminal-only actor
  continuation.
- [Jump-Start RL, ICML 2023](https://proceedings.mlr.press/v202/uchendu23a/uchendu23a.pdf):
  guide policy takes earlier actions, exploration policy later; gradually
  shortens guide horizon. Not purely random distribution exposure.
- [SCOUT, 2607.26417](https://arxiv.org/html/2607.26417v1): trajectory-
  derived simulator scaffolds (fixed progress quantiles), random starts,
  global annealing and adaptive per-context curricula; unchanged sparse
  reward, held-out target starts. Some contexts benefit more from local
  pacing; randomized states not universally best. This supports the
  rationale and supplies a scheduling precedent, not exact Lean result.

## Reconciled next research direction (user steering)

The user explicitly wants to train on real mathematical states drawn
from genuine proofs, especially problems the model **cannot currently
solve**. Do not require or select successful model-generated full
solutions. Separate a mathematical state from a textual solution prefix:
a model trained on native proof state does not need to see the prior
proof text, let alone any suffix. If a verified independent proof exists
(e.g. human-authored real mathematics), its native nonterminal states
can be mechanically reconstructed as environment starts; archived proof
prefix serves as a hidden soundness certificate, not a supervised target.
The actor receives ordinary native state and only the root's terminal
correctness reward, identical to the full-start control. Thus the base
model need not have solved the theorem to gain experience from it.

This still presupposes a known environment-generated or independently
available legal state (e.g. real proof certificate). For a problem with
no known legal derivation to a useful intermediate state, the generative
legal-reset exploration idea is a distinct route, not solved by this
method. User's rejection of "partial solutions" could mean not providing
a textual trace or not requiring a model-originated successful trace;
do not conflate the two. The state-only design addresses both. If the
user means rejecting even independently established local contexts,
that remains to be refined.

### Proposed comparison, not a registered experiment

Hypothesis: RL on genuinely native mid-proof mathematical states bootstraps
skills or representations otherwise unavailable from the current root
distribution, and subsequent root-only RL consolidates them, possibly
with delayed improvement. This is a specifically staged, not merely
higher-suffix-accuracy finding.

- Same pinned initial prover, theorem train/test split, verifier,
  optimizer, prompts/state interface and compute accounting.
- A: root-only RL throughout; B: native-slice-only RL throughout;
  C: native-slice RL then abrupt full-root RL, continue same weights
  and optimizer (no unregistered restart). Optionally deterministic
  mixture/anneal as a later discriminating contrast only if motivated.
- A and C share original root dataset; B/C use every eligible nonterminal
  state of genuine independent proofs under a fixed mechanical sampling
  law. Mask all certificate/prefix tokens from policy credit. Actor
  never gets subsequent proof. Original root and all live goals required.
- At switch, branch the same learned slice checkpoint to continued
  slice and root phases to isolate specialization rather than baseline
  seed variation. Fix switch criterion before outcomes; track repeated
  root-only evaluations before and after switch, total actual resource
  budgets (including extraction/verification and input prefill).
- Training calibration: identify a fixed hard/root-no-positive stratum
  with independent frozen sampled evidence; use same strata in all arms,
  keep separate held-out theorem-family evaluation. Zero observed root
  successes signifies no sampled correctness contrast in those GRPO
  groups, not proof of mathematically zero success probability or absolute
  impossibility of training. Validate informative heterogeneous terminal
  outcomes from slices first, without tuning chosen states for results.
- Avoid importing the very theorem being proved as a library fact: if
  using real Mathlib proofs, restore appropriate predeclaration
  environment and audit dependencies/identity; don't make root trivial
  through leakage. No test theorem-derived training state.
- Primary criterion: faster and better root-only held-out learning at
  matched actual aggregate compute; not assisted completion or increased
  suffix success. Assess delayed transfer as learning-curve property,
  not assumed fact. No extra seed/scale solely for polish.

No experiment or model training is launched in this turn. User's new
direction supersedes the earlier preference for unsuccessful model-prefix
reservoirs only; broader state generation remains a candidate if known
reference states do not cover desired tasks.

## User idea-dump, verbatim: genuinely random mathematical states

> i'm just not happy with the prefix idea. i think the random start idea has a cleaner mapping to mathematics (or coding, or whatever verifiable method, or go (maybe like go, even) we just haven't thought of it...
>
> One idea I have is that human data may be limited. Perhaps the proofs we slice or prefix AREN'T quite like random noise, but truly random states would be. I mean, alphago zero beat alphago can be our motivation for that branch. That's just a branch though, our main brainstorm is "how do we induce random noise other than slicing random prefixes"

## New distinction: the task itself can be the state

The pinball analogy suggests treating formal mathematical sequents
`Γ ⊢ G` as the positions of the mathematical environment, not treating
positions exclusively as places along one known proof of G. In Go the
board is the state, and the objective (legal win) is stable across
different initial boards. In Lean a well-formed sequent is a position;
the analogous common objective is close the entire sampled sequent under
the same Lean rules. This makes random-state training possible without
knowing paths from particular original theorems, while preserving the
mathematical environment. It explicitly changes the distribution of root
theorem statements/contexts, not just the start state of each fixed
root. This is a distinct branch, not a claim about proving exactly the
same originally specified theorem under free extra hypotheses.

### Candidate 1: random constructive sequents (no supplied solution)

Sample genuinely independent well-typed mathematical objects/expressions
with a generic native grammar. One way to get solvable but not necessarily
easy states: generate a random proof-valued term t, infer and check its
type G under an independently generated context Γ, and **discard t from
the learner's observation**. Start the episode at Γ ⊢ G. The learner sees
only a new formal theorem/ordinary proof state, exactly as it would at an
ordinary start. It earns binary terminal reward only for a proof it
constructs itself; the generator's hidden witness certifies the generated
problem, not a supervision target and not a supplied intermediate step.
No human-written reference solution or learner-discovered full proof is
needed. A separate variant samples any well-formed sequent without a
known witness, including unprovable/trivial ones; if almost all give
zero reward, it will not support learning. Quantify this failure rather
than prescriptively selecting good reasoning.

Random grammar and context distributions define the environment's
exploration law; they are not uniform sampling of infinite math. Generic
type-directed term construction can still generate a degenerate collection
of easy equations/tautologies, so hide certificates, report diversity,
difficulty and terminal contrast, avoid goal-conditioned usefulness or
success filtering. No proof imitation, no intermediate score. This has
a direct analogy to a simulator sampling legal boards. Phase 2 can
switch to naturally occurring full hard theorems never solved by the
base; it need not share any target proofs with Phase 1. The empirical
question is broad transfer, not learning a particular hidden solution.

### Candidate 2: mathematical world randomization

Sample random types, expressions, variables, finite structures, equations
and constraints from a typed grammar. Generate a task by asking for
a relation between objects from the same generated world, possibly
guaranteed by a hidden construction (e.g. equivalent expressions
independently derived from a random latent term through legal rewrites).
The learner gets only the ordinary sequent, not the rewrite trace.
This can sample non-reference mathematical experiences directly rather
than perturbing someone's solution. However using a particular rewrite
generator or domain might privilege some reasoning and produce toy
problems; the generalization test must be on unrelated real mathematics.
Identical rules/terminal checker, new task-state distribution.

### Candidate 3: random native disturbance of a fixed goal

If exact identity of the original root G is essential even during
Phase 1, use generative legal partial-state constructions above instead:
random native refinements, independent typed local declarations, arbitrary
case splits, exact state constraints and all remaining obligations. No
reference prefix. Mathematical work supplied by a state-generator is
still disclosed and charged. No arbitrary unearned assumptions.
In coding an analogous final-state task can start from a randomly
perturbed repository with unchanged tests, no known solution; the agent
must actually solve the original task. In Go, arbitrary legal complete
board states with player-to-move and rule history can be sampled, with
normal win criterion; do not equate them to games reached from the
ordinary empty board if legality/history differ.

The user's AlphaGo/AlphaGo Zero analogy motivates replacing the human
trajectory distribution with environment-generated experiences;
it is not evidence that arbitrary random board starts was the reason
AlphaGo Zero improved. No novelty, feasibility or efficacy claim is made.
No experiment registered or run. Main brainstorm is state-noise generation,
not selecting a better prefix curriculum.
