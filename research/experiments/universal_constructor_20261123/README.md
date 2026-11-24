# Universal constructor screen: no verified program

> Interface qualification (November 24): the standalone C1 experiments used a
> leading BOS marker and omitted C1's trained proof-boundary BOS. Recorded counts
> remain valid under those prompts; they do not establish native-interface
> capability limits. See the [confirmed audit and controlled comparison](../../PROMPT_BOUNDARY_2026-11-24.md).

Unchanged C1 generated 128 implementations of two authored universal contracts.
None verified. The proposed reward-support gate fails; no training follows from
this screen. This is evidence about access to correct constructors at this
budget, not proof that the model can never synthesize one.

| Contract | Accepted | Parse errors | Unresolved |
|---|---:|---:|---:|
| Quadratic norm composition | 0/64 | 0 | 0 |
| Bezout coefficient transport | 0/64 | 0 | 0 |

The independent audit reconstructs all 128 edges, seeds, complete sources and
verdicts: 64 unique Lean checks, four validated reference/zero-function fixtures,
6,986 generated tokens and 26,880 supplied prompt tokens. The frozen protocol is
[here](../../UNIVERSAL_CONSTRUCTOR_2026-11-23.md).

The most frequent exact quadratic response, repeated seven times, proposes
`(a*x - d*b*y, a*y + b*x)`: the first-coordinate sign is wrong for the supplied
norm contract. The most frequent exact Bezout response, repeated 17 times,
returns `(u,v)` unchanged despite the row operations. These are specific examples,
not a classification of every failure. Full responses and occurrence IDs are in
[common-failures.json](common-failures.json). No repair or additional sampling
was used to alter the outcome.

Both reference implementations were withheld from prompts. The model did receive
human-written types, laws and boundary conditions; success would not have meant
that it discovered these specifications. No weights were updated, and no executable
witness was extracted. This does not rescue any previous negative learning result.

Frozen execution: f6dce83. Job 1399519 used one H100 on trig0011 under def-zhijing,
with a 30-minute limit. It completed and released its allocation after 5m27s;
the batch step exited zero. The source snapshot, every tokenized response, all
verdicts and parent identity are retained for publication. The failed support gate
rules out immediately applying sparse binary RL on these two contracts.

## Verified GitHub recovery

[The release](https://github.com/memo-ozdincer/restriction/releases/tag/universal-constructor-2026-11-23) contains all raw proposals, judgments,
source and allocation records. All 40 members were downloaded and verified.
Archive size: 247,321 bytes; SHA-256:
`52aef0c3fa689d828ddfb7c6e55ce97d3cc3e3be5d84e5dc6f5ceb8202566f95`. See [receipt](publication.json) and
[member inventory](archive-inventory.json). Extract into the restored
`restriction-rl` bundle. No new model weights were produced.
