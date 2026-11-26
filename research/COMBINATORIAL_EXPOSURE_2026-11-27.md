# Combinatorial optimization: derive exposure from solver bottlenecks

## User steering (verbatim)

> yes, I think B is an issue, a problem where where you start was never really the issue to begin with
>
> For problems where start positions aren't the thing we're optimizing, an issue is obviously choosing what is a thing to choose that keeps magic of rl with nature of problem.
>
> D - I think the generalize thing is like, the exploratory start or whatever you end up choosing as the experiment makes it more likely for you to have some grpo signal would never fnind.
>
> Lets send some subagents to question this thread. Perhaps one or two of them could also ask:
> "What are the leading algorithms and RL algorithms that learn how to do these problems right now?" and "if we look at these algorithms, which degree of freedom are they not being granted that --not necessarily change the long term solution-- but changes how fast it gets there through exploration or something because perhaps it doesn't have enough gradient at the start" thus making us scsale harder problems better

> degrees of freedom DERIVED from looking at the trajectories of sota or well accepted training methods

> or even identifying their bottlenecks, or seeing at what point they stop scaling etc

## Independent three-agent reviews

Focus on ordinary abstract combinatorial optimization. No actual trajectory
dataset was collected in this literature review; distinguish reported findings
from proposed experiments. No experiment registered or launched.

| Domain | Established mechanism and reported observation | Candidate freedom |
|---|---|---|
| TSP | [NICO-TSP](https://arxiv.org/html/2604.06940v1), Appendix E: all-zero group-relative gradients when warmup produces strong reference tours that none of the continuations improve; extra entropy and larger groups yield little improvement. Authors propose difficulty-conditioned references. [Learned 2-opt](https://proceedings.mlr.press/v129/costa20a/costa20a.pdf): fast initial improvement followed by slow refinement; random starts already standard. | Change which local search neighborhoods the model experiences, especially around plateau states with controlled quality. Wider neighborhoods and reference difficulty are prior art. Test retained ordinary-neighborhood learning and distinguish reset access from additional search compute. |
| Graph coloring | [ReLCol](https://arxiv.org/html/2304.04051) learns ordering with irreversible greedy assignment. [VColRL](https://www.cse.iitk.ac.in/users/amitangshu/5083_VColRL_Learn_to_solve_the.pdf) tests deferral and rollback; combined changes improve quality, not isolated causal evidence. [Variable Space Search](https://doi.org/10.1016/j.dam.2008.03.022) switches between complete/conflicting and legal/incomplete colorings. | Allow intermediate commitments to be revisited or omitted, then remove permission. Well established as a solver mechanism; question is retained learning after withdrawal. |
| Job-shop scheduling | [L2S](https://proceedings.iclr.cc/paper_files/paper/2024/file/c75abb33341363ee874a71f81dc45a3a-Paper-Conference.pdf), section 4.1: N5 move restriction can yield absorbing states with no eligible moves and dummy actions for remaining horizon. [Larger neighborhoods](https://arxiv.org/abs/2109.02843) established. | Expose states accessible through broader legal rearrangements, then train ordinary actions. Determine if policy learns to avoid traps. If goal is unreachable under root action rules, no curriculum can change that. |
| Exact cover | [Algorithm X](https://arxiv.org/abs/cs/0011047) selects residual constraints, commits rows, backtracks when no compatible row remains. Learned variable ordering has precedent. | Audit where branching becomes excessive or commitments become irreversible; compare temporary revisions or alternative commitment orders. |
| Reversible circuits | Existing frozen results: Terra 0/4 root and uniform, 3/4 near goal. Distinct reset states, not same-state GRPO groups. [DeepCubeA](https://www.nature.com/articles/s42256-019-0070-z) and [Reverse Curriculum Generation](https://proceedings.mlr.press/v78/florensa17a.html) directly motivate goal-centered exposure. | Measure same-state reward variation by exact distance shell on 3 bits. No distance or witness supplied to policy. |

## Critical points

For binary success probability p, independent groups of size G have mixed
reward probability 1-p^G-(1-p)^G. Both unanimous failure and unanimous success
provide no reward variance. Group by the same start, not mixed start difficulty.
Measure actual completion and mixed-group yield per total compute.
[DAPO](https://arxiv.org/abs/2503.14476) dynamic sampling already targets
zero-variance groups but does not guarantee reward access on an unsolved task.
NICO-TSP is especially direct evidence of the kind of bottleneck the user
wants to study; its proposed reference-difficulty extension overlaps.

Reversible circuits have an exact residual equivalence: for state S and goal
T, the remaining word must implement T composed with inverse(S).
Consequently uniform resets are equivalent to uniform residual synthesis
tasks. Near-goal random walks are easy residual tasks. A controlled
representation comparison can distinguish reset exposure from related-task
curriculum. Fixed-target success addresses optimization efficiency; stronger
generalization claims require held-out tasks or states.

## Proposed methodology

Before deciding intervention, collect accepted algorithm trajectories across
problem difficulty, including complete action sequences, objective dynamics,
first plateaus, repeated patterns, commitments, remaining budget and success.
Identify which states cannot be improved under available transitions and
which merely lack sampled useful continuations. Fork recorded stalled states
at matched horizon/quality to diagnose whether alternative legal experience
changes completion probability. Offline oracle only for diagnosis; no
oracle action labels in training. Preserve original terminal objective and
verify unassisted performance after withdrawing any additional freedom.
Distinguish changing reset distribution from changing transition rules.
Compare against the established stronger search mechanism itself and
ordinary RL at matched compute. Do not manufacture a weak baseline.

Leading hypothesis: inadequate access to informative terminal reward can
limit RL scaling; targeted expansion of experience can create it. Whether
the resulting learning persists after withdrawing assistance is open.
