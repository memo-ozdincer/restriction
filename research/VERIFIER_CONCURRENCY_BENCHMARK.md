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
