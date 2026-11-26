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
