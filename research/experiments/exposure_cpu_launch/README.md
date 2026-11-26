# Joint CPU panel following magic-of-RL review

Registered before full runs. The user explicitly requested independent
critiques and authorized dispatch after refinement. The original panels
test gradient access in severe sparse-reward tasks. The common-prefix
panels test a distinct hypothesis: environmental expansion improves
learning even after ordinary RL has already progressed. The fork is a
fixed 30% checkpoint, with identical weights, optimizer moments, and
training RNG verified by hash; exposed 30–60%, restoration final 40%.
If ordinary learning has not progressed at the fork, that seed tests
bootstrap rather than the stronger claim. No selection of successful
seeds or promising states for training. Report all runs, actual reward
variance, gradient/update counts where logged, and native final task
results. Rank-nine visits and verified path hashes are passive diagnostics.

All three reviewers agreed on this distinction. Specific refinements:
TSP/Flip add common-prefix arms; Sokoban adds a medium root selected
by mechanical exact random-hit probability [.002,.01] (same board,
goal, horizon), with all-legal resets; matrix adds late-switch and
rank/path audits. Reversible retains its predeclared 11-arm resource
test. The tiny nonsparse tensor toy is intentionally excluded for lack
of a relevant gradient-starvation hypothesis. The substantive matrix
experiment remains in the panel.

Use the existing registered default budgets (see each experiment README).
TSP/Flip scratch and common panels run sequentially with 64 workers each;
Sokoban 32, matrix16, reversible44 concurrently. At most 156 workers,
one whole Trillium CPU node. No GPU. Match allocated action budgets,
record actual candidate cost, no claim of identical arithmetic.
The purpose of the full panel is to distinguish different mechanisms,
not replicate a known outcome for statistical significance.

All 13 existing/new unit tests passed locally, independently reviewed
implementations smoke-tested. Repo sources are pinned to the submitted
snapshot; exact checksums stored on remote. Follow Trillium quickstart.

## Submission

Job 2939388, account def-zhijing, debug partition, 192 CPUs on tri0078.
Remote directory /scratch/memoozd/rrl/exposure-panel-20261127-555b110.
Submitted source snapshot 555b110 (tracked experiment files only;
other sessions' unrelated untracked files excluded). All 21 remote
SHA256 checks passed. Slurm verified RUNNING at 2026-11-26 14:00:50
cluster-local reported time; 55-minute limit. Scheduler warning only
recommended a shorter requested time. Monitor this job, do not resubmit.

## Completed results

Slurm job 2939388 completed with exit code 0 in 75 seconds, all 192 CPUs.
Retrieved 220 individual learning records: 64 scratch TSP/Flip, 64 common
prefix TSP/Flip, 32 Sokoban, 44 reversible, 16 matrix. The 32 Sokoban and
44 reversible directories also contain metadata manifests. All 16 TSP/Flip
common prefix hashes matched across same-domain, same-seed arms; all four
medium Sokoban forks and four matrix late-switch forks matched. Final
Sokoban independent replay counts agree with sampled hits. The runner's
native replay assertions completed for all domains. Archived scheduler
and application logs are in results/. An additional SSH status check
after retrieval was denied authentication; prior live sacct completion
and retrieved artifacts already establish job completion.

| Domain | Ordinary | Persistent expanded | Exposure then ordinary |
|---|---:|---:|---:|
| Hard Sokoban, uniform legal | 0/1024 | 0/1024 | 0/1024 |
| Hard Sokoban, solvable reset | 0/1024 | 994/1024 | 91/1024 |
| Medium Sokoban, legal after common prefix | 1022/1024 | 986/1024 | 1022/1024 |
| Flip, uniform, scratch | 1009/1024 | 30/1024 | 616/1024 |
| Flip, goal-local, scratch | 1009/1024 | 3/1024 | 13/1024 |
| Flip, uniform, common prefix | 1009/1024 | 41/1024 | 984/1024 |
| Flip, goal-local, common prefix | 1009/1024 | 10/1024 | 363/1024 |
| TSP scratch (mean length, lower better) | 5.54412 | 5.56080 | 5.55497 |
| TSP common prefix (mean length) | 5.54412 | 5.55188 | 5.54964 |
| Matrix (root rank≤7 within cap8) | 5/512 | 3/512 | 6/512 |

Matrix late switch: 7/512 (per seed 1,3,3,0 versus ordinary 2,1,2,0).
All four ordinary prefixes already had training hits (6,4,1,3).
Late switch evaluated fewer actual candidates (21.19M vs 27.40M);
persistent cap9 earned only one training success despite extensive
rank-nine visitation. Early and late switches each earned exactly one
success involving rank9, so no strong evidence of acquired strategy.
The 2- and 1-success differences are exploratory, cannot establish a real
advantage. TSP mean costs do not improve; common switch has 52 optimum
hits vs 38 ordinary, but aggregate mean worse and same eight seeds.
All 44 reversible runs have 0/512 final ordinary hits each, including
temporarily extended budgets. Resource access does not suffice.

Most substantive new positive result: *persistent solvable-state Sokoban*
generalizes to the original hard root despite no ordinary training success.
It earns 994/1024 final unassisted successes, versus 91/1024 for early
switch and zero for uniform-all-legal/reset arms. This reset distribution
uses offline solvability filtering, so it is not indifferent uniform
sampling of the complete legal state space. The result is a learning
effect, not pure pinball-style delayed switch superiority. Medium Sokoban
ordinary policies already score 233–246/256 at the common fork and
saturate; persistent legal exposure slightly degrades. Flip root learns
strongly and exposure frequently damages it. No compelling falsification
of the user's 'ordinary wins when it can progress' conjecture in this
panel. Further work needs a genuinely hard task with ordinary progress
and headroom, stronger independent strategy probes and computational
matching, not more seeds for the same near-ceiling controls.
