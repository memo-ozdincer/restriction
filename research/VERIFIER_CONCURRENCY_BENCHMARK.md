# Authorized verifier concurrency diagnostic — September 14, 2026

The user approved this bounded operational benchmark, not another full C5 run.

Hypothesis: using 64 rather than 32 verifier workers reduces batch wall time
enough to justify a C5 feasibility test without introducing verdict changes,
more infrastructure failures, or unsafe memory pressure. C5 spent roughly
76% of logged step time in verification before timing out at step 571/604.

Freeze inputs before execution: complete 512-proposal batches at steps 100 and
550 from each finalized C2/C3 training log, including incorrect proofs. This
is 2,048 distinct saved proposals and 8,192 verification attempts total.
Use 32/64/64/32 for even-index panels and 64/32/32/64 for odd-index panels.
Input order is identical within each panel, with the original verifier code,
300-second timeout, 32 GiB per-process limit, and extra-text penalty unchanged.
Stage the same pinned verifier and compact-result patch on disk-backed /tmp.
An additional path-only patch resolves `lake` through the pinned `ELAN_HOME`,
since the submitted account's `/home/memoozd/.elan` does not exist. It does
not change Lean code, resource limits, or correctness decisions; both worker
conditions use the same patched runtime. The process HOME is not changed.
Use a full-node H100 allocation under def-zhijing for matching CPU/memory
resources; the GPUs are necessarily reserved but no model is loaded.

Save each pass before proceeding. Report latency, verdict/failure-class
disagreements, timeout counts, and sampled node MemAvailable (0.5-second
polling). The minimum available-memory statistic includes cache effects and
is not process RSS; it can miss shorter peaks. No result from this test is
a C5 proof-performance result. C5 has no saved proposal snapshot, so C2/C3
inputs are a proxy. Counterbalanced order reduces but does not remove cache
effects. Model-free execution does not establish training memory safety.

Decision: do not proceed automatically to full training. A consistent speed
benefit with unchanged verdicts and safe headroom motivates a separately
authorized model-loaded feasibility check. Verdict instability, infrastructure
failures, or mixed/slower runtime argues against adopting 64 workers without
further diagnosis. The benchmark is capped at two hours; incomplete passes
remain explicitly incomplete rather than being omitted from the result.

## September 21 resource-request audit

Read-only `scontrol show job 918556` confirms the live request is 96 CPUs,
770000 MiB node memory, four H100 GPUs, and two hours on compute_full_node;
the job remains pending for priority with zero runtime. GPUs are unused by
the benchmark itself. The full-node request preserves the target training
node's CPU/memory resources and isolation, rather than providing accelerator
compute for Lean.

The live `sinfo` partition inventory exposes no CPU-only partition on this
cluster. The H100 debug_full_node partition caps runs at one hour, below the
registered two-hour cap; ordinary debug permits two hours but does not itself
establish equivalent full-node isolation or faster scheduling. These checks
do not rule out another cluster or a scheduler-supported alternative, but
provide no verified drop-in CPU-only route here. No job was canceled,
resubmitted, or modified. A different machine would test verifier scaling on
that machine, not directly establish runtime margin on the training node.

## September 21 completed result

Slurm job `918556` completed successfully at 10:19 EDT in 19m36s. All sixteen
registered passes finished: four fixed 512-proposal panels, each replayed twice
with 32 workers and twice with 64 workers in counterbalanced order. Across the
four panels, mean pass time was 75.445 seconds at 32 workers and 54.486 seconds
at 64 workers, an aggregate 1.385x speedup. Panel speedups ranged from 1.303x
to 1.464x.

All repeated passes had identical verdicts and failure classes: zero
disagreements across the registered comparisons, with no parse failures or
timeouts. The lowest sampled `MemAvailable` value at 64 workers was 726,930,600
KiB, and the largest sampled decline from pass start was 32,382,152 KiB. These
node-level samples show ample headroom in the model-free replay but do not
establish memory safety with the training actor loaded.

The result supports 64 workers as a meaningful verifier-throughput improvement
on the target node class. It does not by itself prove that C5 will finish under
the 24-hour limit: C5 proofs may have a different latency distribution, full
training adds actor memory and contention, and a 1.385x verifier-only speedup
does not scale every part of the run. Per the registered decision rule, the
next justified step is a separately authorized model-loaded feasibility check,
not an automatic full C5 restart.

The tracked compact artifact is
`results/verifier_workers_918556_summary.json`. Full per-proof outputs and the
manifest remain at
`../runs/verifier-workers-benchmark-20260914-918556/results`; the raw Slurm log
is `../../slurm-verifier-workers32-64-918556.out`. SHA-256 digests are:

- compact source summary: `2f60555c35342520ec128d19696d0fef5bba1345c583d666f0734ba3724d848d`
- full manifest: `1abf98d54fda23a5a2ba8307ae763c05219c7f49885da8a65f9ac19a5f6bddf2`
- raw Slurm log: `a92a74e8d266aecc30430e94df9ef99447727a4b984218cf9858cf99f1b6d080`
