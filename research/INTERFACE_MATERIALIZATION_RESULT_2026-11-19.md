# One sampled proof procedure works in both recurrence worlds

The exact successful GRPO continuation from the quadratic2 nonzero target also
proves the quadratic3 nonzero target, unchanged. It fails with the irrelevant
lemma in both worlds. This is a concrete example of verified procedure reuse:
fresh GRPO sampling had found no quadratic3 proof in 128 bare attempts, 32
global-invariant attempts, or 32 local-invariant attempts. The transported proof
uses the appropriate **human-authored invariant** supplied through the same
local hypothesis `h`; the model did not discover that invariant.

The generated continuation, with no cleanup or editing, is:

```lean
  intro heq
  simp only [heq, mul_zero, zero_mul, sub_zero, zero_add, zero_pow two_ne_zero] at h
  nlinarith
```

The provided prefix is `have h := reusable_fact n`. Complete standalone Lean
files, including the authored invariants and target definitions, are
`experiments/interface_materialization_20261119/grpo-success.lean` and
`experiments/interface_materialization_20261119/grpo-transported-success.lean`.
Exact suffix/source hashes and all transport verdicts are preserved alongside.

## Full sampling result

| Target | Base global invariant | Base local invariant | GRPO global invariant | GRPO local invariant |
|---|---:|---:|---:|---:|
| quadratic2 nonzero | 0/32 | 1/32, 8 timeouts | 0/32 | 1/32 |
| quadratic2 Bezout | 0/32 | 0/32 | 0/32 | 0/32 |
| quadratic3 nonzero | 0/32 | 0/32 | 0/32 | 0/32 |
| quadratic3 Bezout | 0/32 | 0/32 | 0/32 | 0/32 |

Both models scored 0/32 in every local-irrelevant cell. Both earlier bare models
scored 0/128 on each target. The follow-up generated all 512 planned proposals:
two accepted, five parser rejections, 507 physical Lean calls, eight 60-second
timeouts, and no missing verdicts. All eight timeouts were in the base
quadratic2/nonzero/oracle cell; they remain unresolved, not counted as
mathematically invalid. GRPO had no verifier system errors. The independent
audit checks every frozen request field, sample ID, checked-source hash, and
accepted theorem's axiom audit. It passed for all 512 samples.

**The prespecified sampling threshold was not met.** It required at least 4/32
local-invariant successes on an eligible target, with no verifier errors and
at most 1/32 local-irrelevant successes. The clean GRPO result is 1/32; the base
cell is additionally incomplete as a mathematical judgment because of timeouts.
These observations do not establish a causal improvement in success probability.
The local invocation is an extra supplied proof step, not a learned behavior.

## Exact-byte transport check

After seeing the two successes, register the specific hypothesis that both
unchanged suffixes work in both nonzero worlds with the true invariant and
fail with the irrelevant helper. Cross **both** successful suffixes with both
worlds and both helpers: eight CPU Lean calls, no new model samples or repairs.
Keep both sources' exact original-world code hashes unchanged.

| Suffix source | quadratic2 oracle | quadratic2 irrelevant | quadratic3 oracle | quadratic3 irrelevant |
|---|---|---|---|---|
| Base sample 29 | timeout | timeout | accepted | rejected |
| GRPO sample 31 | accepted | rejected | accepted | rejected |

Both first CPU checks timed out at the unchanged 60-second limit; they are
preserved without retry or relabeling. The complete GRPO crossover supplies the
concrete reusable artifact. Both worlds and targets were already inspected:
this is a post-hoc descriptive reuse result, **not held-out generalization**.
The two related recurrences do not establish cross-domain transfer or novel
mathematics. The supplied invariant remains essential to this demonstration.

## Cost, preservation, and decision

Job 1371859 used one H100 under def-zhijing for 11m19s, within its 30-minute
bound. The driver finished in about nine minutes, wrote terminal output, and
cancelled its own allocation. Scheduler accounting confirms GPU release. No
job remained in the user's queue at the terminal audit. There was no training.
Generation used 10,750 output tokens and 109,312 supplied tokens, counting
context separately per proposal. The eight transport checks are additional to
the 507 sampling checks and the six previously recorded preflight checks.

The raw follow-up archive contains 38 files / 833,560 uncompressed bytes, with
the exact source and protocol snapshots, all raw samples and verdicts, model
hashes, launch/accounting records, and transport evidence. Its per-file
inventory and GitHub download-verification receipt live in the experiment
directory. The original baseline/panel archive is a separate prerequisite.

Prioritize **learning reusable proof procedures with an explicit local-fact
interface** over more blind lemma proposals on this panel. This result supplies
one actual reusable procedure to inspect; it does not yet justify a larger
training campaign. The next substantive question is whether a model can learn
to produce and invoke such procedures on fresh, withheld task families, with
the human-authored oracle removed or separately controlled. Freeze that design
before further compute; do not turn this one success into repeated seed sweeps.
