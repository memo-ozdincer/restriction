# Initiating the local-lemma strategy does not unlock reliable execution

> Interface qualification (November 24): the standalone C1 experiments used a
> leading BOS marker and omitted C1's trained proof-boundary BOS. Recorded counts
> remain valid under those prompts; they do not establish native-interface
> capability limits. See the [confirmed audit and controlled comparison](../../PROMPT_BOUNDARY_2026-11-24.md).

The transport-trained model rarely begins the taught local-lemma proof. Supplying
that beginning still does not yield reliable success: the best new-target cells
are **1/16**, and an unseen local-lemma name yields zero throughout. **The
registered conditional-correctness gate fails.** A selection-only intervention
is not supported by this evidence.

| Task/sign | C1 natural | C1 trained name | C1 unseen name | Transport natural | Transport trained name | Transport unseen name |
|---|---:|---:|---:|---:|---:|---:|
| arbitrary function/-1 | 0 | 0 | 0 | 0 | 0 | 0 |
| arbitrary function/+1 | 0 | 0 | 0 | 0 | 0 | 0 |
| renamed arbitrary function/-1 | 0 | 0 | 0 | 1 | 1† | 0 |
| renamed arbitrary function/+1 | 0 | 0 | 0 | 0 | 1 | 0 |
| original/-1 diagnostic | 0 | 0† | 0 | 0 | 0 | 0 |
| original/+1 diagnostic | 3 | 3 | 3† | 10 | 4 | 5 |

Each cell contains 16 proposals. Natural cells reuse 192 saved responses from
the exact checkpoints and tasks; they are not newly generated replicates.
The two supplied starts are `  have source_contract :` and `  have auxiliary :`.
They provide a syntax/strategy cue, not a proposition, constructor or proof.
They change the information available, so these are assisted continuations,
not improved unassisted model pass rates. † One new response times out at the
fixed 60-second verifier limit in each marked cell and remains unresolved.

There are three new parse failures, all transport: one arbitrary-function/-1
with the trained name, and one renamed/-1 under each supplied name. The reused
natural bank also contains its previously recorded arbitrary-function/+1 parse
failure. All remain in denominators. Even resolving every timeout as a success
cannot satisfy the registered thresholds.

## Inspectable successful continuations

The transport adapter has one accepted new-target proof for each renamed sign:
[negative](transport-renamed_-1-trained-8.lean) and
[positive](transport-renamed_1-trained-15.lean). Each repeats the entire target
proposition after `have source_contract :`, builds a direct universal formula,
proves it with ring normalization, and closes the original goal with `aesop`.
The local proposition equals the target after whitespace removal; the
[inspection record](novel-proof-inspection.json) records this exact comparison.

These are valid proofs for arbitrary coefficient functions. They are not
examples of reconstructing the trained general source law and specializing it
to a new target. Prefix-conditioned correctness alone would not establish
that mechanism, even if it were more frequent.

## Subsequent token-boundary qualification

The [native-interface audit](../prompt_boundary_20261124/README.md) found that
unchanged C1 normally generates an invisible BOS before its visible proof in
this standalone format. The supplied starts omit that boundary, and the trained
adapter was also optimized without it. The recorded head likelihoods below are
for the exact no-intervening-BOS token sequences, not the probability of seeing
the visible strategy after an optional generated BOS. A native-format comparison
is needed before attributing this diagnostic to a selector/executor limitation.

## Initiation probability and execution are separate failures here

The exact six-token trained start has probability approximately 3.38e-10 to
1.31e-8 under the transport adapter across these prompts. Training increased
its probability substantially relative to C1, but the sequence remains rare.
The four-token unseen start is also rare. These are teacher-forced probabilities
of specific token sequences, not estimates of the mass of an entire reasoning
strategy; alternate wording and whitespace are not summed.

Supplying the rare start bypasses its sampling probability. Conditional success
nevertheless remains sparse, including zero on the original negative training
target. Thus this experiment does not justify assuming that a competent reusable
procedure is merely waiting for a better selector. Do not respond by tuning
prefixes or extending the same adapter's training on this evidence.

## Execution, accounting and recovery

The [frozen protocol](../../CONTRACT_ENTRY_2026-11-24.md) records the decision,
claim boundaries and current primary research motivations. No training occurs.
The exact saved transport adapter from job 1400174 is reloaded; all recorded
demonstration probability probes match exactly. C1 parent hashes match the prior
experiment. Float32, TF32 disabled and PEFT 0.10.0 remain fixed.

All 384 new continuations and 368 unique Lean checks reconstruct in the independent
audit. Three verdicts remain unresolved despite the integrity audit passing.
The six-token trained and four-token unseen starts count against the original
768-token response budget. Supplied tokens total 1,920 across proposals; new
generated tokens total 82,603 (C1 30,388; transport 52,215). The unchanged prior
natural responses are explicitly distinguished from these new costs.

Frozen source is `e3e0dcb`; the only untracked file at launch was the separate
archive writer, which is not used in execution. Job 1400389 runs on an H100 at
trig0042 under def-zhijing. Its successful batch releases the keeper allocation
after 22m05s. No GPU remains allocated.

The recovery archive includes all new raw evidence, the exact reused transport
adapter, previous natural response banks and verifier records needed by this
audit. Bulk parent weights are excluded. The [GitHub release](https://github.com/memo-ozdincer/restriction/releases/tag/contract-entry-2026-11-24)
contains the complete archive. A fresh download verifies all 109 members; see
[the receipt](publication.json). Archive SHA-256:
`b1985f387a7980bda1c233605e25a0e785402b69a6577d162c90faa909b86e68`.
