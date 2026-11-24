# Separate sampled programs from their proof certificates

Expected useful result: an already sampled, unchanged function satisfies a whole
universal contract, but its accompanying proof failed. A fixed certificate
generator could then expose a valid program that whole-proof binary reward hid.
This would motivate separating program learning from certificate construction.

Both prior screens returned zero accepted complete proofs: 128 original and 96
feedback-conditioned proposals. Their mode examples contain wrong algorithms,
but those examples do not classify every output. Before discarding all outputs
as a source of programs, audit the full saved banks without new sampling.

Extract only a single directly supplied existential witness of the form
`fun binders => (polynomial, polynomial)` at the start of `use`, `refine` or
`exact`. Require the correct arity, ordinary untyped binders, and arithmetic
consisting only of names, integers, addition, subtraction, multiplication and
nonnegative powers through four. Do not normalize or edit the extracted Lean
text. Unsupported/ambiguous syntax and original parse errors remain unclassified,
not algorithmically wrong. Report all 224 proposals and every exclusion.

For each supported function, independently expand all contract residuals with
symbolic algebra. Then place the exact original function in a fixed Lean proof
template using introductions, simplification and ring normalization. Both are
diagnostics; Lean remains the correctness authority. Check every unique extracted
function, including those with nonzero residuals, and preserve complete sources.
The two reference implementations and zero-function controls must also receive
the same certificate process. No operator repair, sign search, free-variable
substitution or candidate-specific proof adjustment is permitted.

Save exact source offsets, function bytes, input hashes, symbolic residuals,
full certificate sources and Lean judgments. Any semantic/Lean disagreement or
unresolved judgment prevents a complete interpretation until diagnosed. Count
the original whole-proof result separately from compiler-assisted acceptance.

Finding at least one compiled valid model function in each family would establish
support for a separate prospective learning comparison, not pass the earlier
whole-proof or feedback criteria. A one-family result stays one-family. If no
supported function is correct, certificate generation does not repair this
observed bottleneck. Do not add program repairs or broaden the parser after seeing
outcomes and present the result as this frozen diagnostic.

This is an inspected-bank CPU audit, not a learned capability gain or new model
experiment. The certificate generator and authored contracts contribute external
computation and information. No GPU is needed. Publish code and protocol before
replay, then preserve all artifacts and the decision.
