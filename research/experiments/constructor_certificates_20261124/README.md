# The failed constructors contain algorithm errors, not just proof errors

A fixed certificate generator recovers **zero valid functions among 221 supported
proposals** from the original and feedback screens. Three of 224 proposals remain
unclassified: one unsupported direct-witness form and two original parse failures.
This is not a claim about the semantics of those three outputs.

| Family | Saved proposals | Extracted unchanged functions | Verified functions |
|---|---:|---:|---:|
| Quadratic composition | 112 | 112 | 0 |
| Bezout transport | 112 | 109 | 0 |

The independent audit reconstructs source offsets and exact function bytes,
complete certificate sources, input hashes, all proposal mappings and counts.
There are 17 unique Lean checks including four reference/zero-function controls.
All controls have the expected result, no judgments are unresolved, and symbolic
contract residuals agree with Lean acceptance in every supported case.

The [frozen protocol](../../CONSTRUCTOR_CERTIFICATES_2026-11-24.md) forbids edits
to the sampled functions and candidate-specific certificate changes. It was
committed before replay at 7350ccc. The fixed template uses introductions,
simplification and ring normalization. Existing whole-proof outcomes stay zero;
this audit is a separate compiler-assisted diagnostic, not another model run.

This removes proof-certificate generation as the sole explanation for the failures
of the 221 supported functions. It does not establish that every possible proof
interface or program-learning method fails. A future mechanism must change program
construction itself rather than simply reformat these same candidate proofs.
No program repair, new model sampling, parameter update, or GPU allocation was
performed. No training follows the failed two-family support criterion.

## Verified recovery

The [feedback release](https://github.com/memo-ozdincer/restriction/releases/tag/constructor-feedback-2026-11-24) now also contains
`certificate-audit-20261124.tar.gz` and `certificate-inventory.json`. All
16 downloaded archive members match their hashes, including both full input
response banks, exact functions, all sources/verdicts, frozen execution and auditor.
The 233,842-byte archive SHA-256 is
`370f34e876e943e33be1e3973657556596cbcceb4dd82fcbbca2f75d21c15c9d`. See [receipt](publication.json).
Extract relative to the restored `restriction-rl` bundle.

[Timing](timing.json) records 79.7 seconds between source-archive creation
and result writing, including extraction/startup; it is an artifact-based elapsed
interval, not a direct command timer. Four verification workers were used.
