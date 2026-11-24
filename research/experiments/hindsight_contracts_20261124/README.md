# Verified hindsight learning: a limited scaled-law gain, original targets unsolved

Forty-six originally failed proofs verify unchanged under an inferred nearby
contract. Training on eight of those proofs makes the familiar relabeled law
reliable: replay reaches 16/16, compared with unchanged C1 at 1/16. Context contrast
reaches 11/16 there and produces three verified proofs for the unseen coefficient
2*d, where both controls score zero. **Every original-sign target remains 0/16**.
Both the registered target and retention criteria fail.

| Specification/sign | C1 | Hindsight replay | Context contrast |
|---|---:|---:|---:|
| original/-1 | 0/16 | 0/16 | 0/16 |
| original/1 | 1/16 | 16/16 | 11/16 |
| renamed/-1 | 0/16 | 0/16 | 0/16 |
| renamed/1 | 0/16 | 0/16 | 0/16 |
| scaled/-1 | 0/16 | 0/16 | 0/16 |
| scaled/1 | 0/16 | 0/16 | 3/16 |
| nonlinear/-1 | 0/16 | 0/16 | 0/16 |
| nonlinear/1 | 0/16 | 0/16 | 0/16 |

Sign -1 is the desired norm x²-d*y². Sign +1 is the inferred norm x²+d*y².
The original +1 prompt is positive training context; the original -1 prompt is
negative training context. Neither is a held-out specification. Renamed, scaled
and nonlinear variants are distinct from updates but close mathematical relatives,
not cross-domain transfer. The coefficient variants use 2*d and d²+1.

## Actual sampled construction

[Sample 6](scaled-positive-sample-6.lean) returns
`fun d a b x y => (a*x - (2*d)*b*y, a*y + b*x)` and supplies a complete proof using
ring normalization and aesop. Lean checks the norm-product law for every integer
input and both basis laws. Samples 10 and 13 also verify; all three are preserved.
This is an unassisted sampled function under the altered specification. The
3/16 result is a secondary observation and does not replace the failed primary
criterion or erase the drop from replay's 16/16 to contrast's 11/16 retention.

## What was learned and checked

The [mining report](mining/README.md) and [frozen protocol](../../HINDSIGHT_CONTRACTS_2026-11-24.md)
record the selection. Both adapters receive the same eight distinct complete
model responses in the same order for 32 steps. Positive responses are verified
under the inferred +1 goal and invalid under the original -1 goal. No successful
-1 response enters an update. The signed quadratic family is human-specified;
this is not unrestricted law discovery. HER and contrastive instruction relabeling
are established prior art, explicitly cited in the protocol.

Both arms include the negative-context reference anchor and forward passes; only
the contrast loss differs. The contrast objective lowers the selected response
probability in the wrong context. That measured loss effect did not produce a
correct original-sign construction. It must not be substituted for target success.
This is offline learning on final ordinary-GRPO C1, separate from the historical
pristine-SFT/C3 experiments and their unchanged gates.

The independent audit passes: all 384 proposals, 261 unique evaluation judgments,
32 allocated-node fixture checks, exact prompt/response tokenization, training
selection/order, seed assignments, reference invariance and saved adapter hashes.
There are no parse errors or unresolved evaluation judgments. Separate preparation
used 30 mining checks and 32 CPU fixture checks. Sequential and joint gradients
agree within 6e-8 in the preflight; repeated negative forward means agree exactly
throughout both training runs. Saved tensors match live adapter tensors exactly.

## Execution and next decision

Frozen execution: ea6abac. Job 1399987 ran on one H100 on trig0025 under def-zhijing
for 12m10s. Its batch step completed with exit code zero; the keeper allocation
was released. Both small adapters and every proposal are preserved. Bulk C1 parent
weights and optimizer state are excluded; the exact parent file hashes are tracked.

This establishes usable verified hindsight data and a narrow scaled-law result,
not the hoped-for target construction without positive demonstrations. Do not
extend epochs or seeds to polish it. The next mechanism must explain how to
construct the missing program, rather than assume that context discrimination
alone creates it. No revolutionary-paradigm claim is supported.

## Verified GitHub recovery

[The release](https://github.com/memo-ozdincer/restriction/releases/tag/hindsight-contracts-2026-11-24) includes both actual adapters, all training
tokens/reference probabilities/metrics, all 384 proposals and Lean verdicts, the
mining inputs and certificates, both source snapshots and allocation records.
All 101 downloaded archive members match their hashes. Archive size:
29,676,292 bytes; SHA-256:
`da2afea37ea8e9e5ec1f0d2f03e726833acdbaee4e5bbf47b9d6563809df96aa`. See [receipt](publication.json)
and [member inventory](archive-inventory.json).

Extract into the restored `restriction-rl` bundle. Adapters live under
`runs/hindsight-training-20261124-1399987/experiment/{replay,contrast}/adapter`.
They require the final C1 parent identified by [file hashes](parent-model-identity.json),
float32 with TF32 disabled, and PEFT 0.10.0. Bulk parent weights and optimizer
state are excluded; these are final adapters, not optimizer-resume checkpoints.
