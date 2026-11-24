# A confirmed interface error, zero constructor rescues, and a hidden training-boundary change

The standalone C1 drivers used a leading begin-of-sentence marker and omitted
the marker at the proof boundary. Historical C1 training does the reverse.
The CPU audit reconstructs **all 128 saved training prompts exactly** from the
historical format: no leading BOS, final token 100000. This is an implementation
error in the standalone research interface, not evidence of model incapacity.

Correcting it did not rescue the four tested constructor tasks. All 256 new
responses fail verification, with no parse errors or unresolved judgments.

| Task | Neither marker | Leading only, legacy | Trailing only, native | Both |
|---|---:|---:|---:|---:|
| universal quadratic composition | 0/16 | 0/16 | 0/16 | 0/16 |
| Bezout transport | 0/16 | 0/16 | 0/16 | 0/16 |
| arbitrary coefficient function, negative sign | 0/16 | 0/16 | 0/16 | 0/16 |
| arbitrary coefficient function, positive sign | 0/16 | 0/16 | 0/16 | 0/16 |

The predeclared large-correction-effect gate fails. The independent audit
reconstructs all 256 proposals, 87 unique evaluation checks and eight fixture
checks. Model weights, all non-marker prompt text, seeds, generated-token cap,
sampling parameters, Lean verifier and axiom policy are held fixed. Native
and legacy each contain exactly one supplied BOS token. No training occurs.

## What the raw tokens reveal

When the prompt omits the proof-boundary marker, C1 generates it itself before
any visible proof text: **128/128** in the neither/legacy formats. With the
boundary supplied, none of the 128 native/both responses generates BOS.
`skip_special_tokens=True` removes that generated token from displayed proof text.
Thus ordinary sampling often supplies the missing boundary even though a
teacher-forced visible-text continuation does not.

The [token analysis](boundary-token-analysis.json) also checks the preceding
closure-learning banks:

| Earlier arm | Responses beginning with generated BOS | Total |
|---|---:|---:|
| unchanged C1 | 160 | 160 |
| hindsight adapter | 0 | 160 |
| executable adapter | 0 | 160 |
| transport adapter | 0 | 160 |

All 24 corresponding training response records omit BOS. Those adapters were
therefore trained to emit visible proof text directly under a context where
their parent normally first emitted a protocol token. Their prompt/response
tokenization is internally consistent—there is no discovered off-by-one loss
index—but their adaptation changes the parent's boundary behavior. This is a
measured confound, not proof that it caused every failed transfer result.

On the quadratic task, the canonical immediate `  use fun` prefix has probability
about 5.40e-8 under legacy formatting versus 0.150 under native formatting. This
does **not** mean the visible strategy was absent in legacy sampling: it can
occur after the generated BOS. Exact token-sequence probabilities must not be
treated as total strategy probabilities. The earlier supplied-prefix diagnostic
also omitted this boundary and needs a native-interface counterpart before its
outcome can support a broad selector/executor interpretation.

## Scope and forward correction

Historical trainer-based C1/C3 results used their recorded native interface and
are unchanged. Standalone proof correctness counts remain valid for the exact
recorded inputs. Eleven recent report entry points now carry an interface
qualification; their original raw banks and released archives are preserved.
CPU certificate/transport proofs still establish their mathematical statements.
This discovery changes how strongly we can interpret the model/learning results.

The explicit [interface helper](../../../scripts/project/proof_prompt_interface.py)
constructs markers deliberately and disables implicit tokenizer insertion. New
C1 work must authenticate native token IDs; other modes must be named
interventions. Closed historical scripts remain reproducible rather than silently
claiming that old data used corrected code. The next useful comparison is native
adaptation with an authenticated boundary, not a claim that formatting is a
revolutionary paradigm or that the current zero-success tasks have been solved.

## Provenance and execution

The [protocol](../../PROMPT_BOUNDARY_2026-11-24.md) froze the marker comparison
before generation. [Native training audit](interface-audit/audit.json): producing
commit `5ced4c3`, saved final batch SHA-256
`5c5df6b8d7ebafede7bcbfb54a8bf40ca9c71ce3caef12856a5114bbfaec2ec1`.
All 128 full prompts match, not merely their last tokens. All eight recent
transport training token arrays match joint encoding but differ from native.

Frozen GPU source `30cd4dd`; job 1400589, def-zhijing, H100 at trig0024.
The successful batch releases the keeper after 9m23s. No GPU remains allocated.
Generated tokens: neither 3,044; legacy 2,881; native 3,146; both 2,767, totaling
11,838. The raw output tokens, including generated BOS, remain in the archive.

The recovery archive includes new raw evidence, original training tensors and
configuration, frozen source, tokenizer files, and the prior banks needed to
reproduce the boundary-token analysis. Model weights are excluded. A publication
receipt will record fresh-download and every-member verification after upload.
