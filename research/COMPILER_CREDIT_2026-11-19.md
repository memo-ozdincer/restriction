# Compiler source maps as a training-credit mechanism

## The result we want to see

From an empty proof root, the trained model writes a complete proof on a fresh
recursive state machine: it preserves the needed invariant and constructs the
final witness. No external theorem library, scope repair or linker is available
at evaluation. The same model trained on the same complete demonstrations with
ordinary full-proof likelihood does not reliably produce those proofs.

The intervention borrows source maps and dependency tracking from compilers.
We already know exactly which state-binding edit repairs the invariant and which
component connection closes a witness proof. Can assigning learning credit to
those small spans teach the missing operations better than spreading it across
the whole verified program? This is a new, off-policy distillation experiment,
not another seed or depth sweep, and not a claim that masked likelihood is novel.
It must earn a useful empirical distinction before any larger paradigm claim.

## Evidence and interpretation boundaries

D-132 found a causal scope-binding defect, but its two-schema broad repair gate
failed. D-134 found useful prerequisite consumers in only one schema. D-137
established four explicitly connected witness proofs, with human-specified
connections and existing model procedure bodies. Those earlier outcomes remain
unchanged. This test uses the new complete component compositions as a distinct
data source; it does not claim that earlier gates passed.

D-138's fixed-search trace reaches the needed invariant and final hypothesis.
The pinned Backtrack.run checks zero remaining fuel before an empty goal list;
four applications therefore require an additional closure call. This explains
why that particular depth-four attempt is not evidence of a deep representation
defect. We do not tune its depth or use it as the new training mechanism.

The masks are compiler provenance, not a proof that every selected token is
causally necessary. The scope-variable ablations support the binding span;
the witness connection and constructor spans are supplied component boundaries.
The original mathematical statements and the connection template are
human-specified. All three training arms receive identical correct programs.

## Fixed data and arms

Eight training demonstrations: the first repaired invariant for each of four
original variants, plus four self-contained witness proofs assembled from those
invariants and original sample `base/witness_2/15`. Convert external theorems to
local `have` declarations and include all proof bodies in the completion. Kernel
check every resulting full root. No evaluation proof is used in training.

Three adapters start from identical pristine base weights and LoRA initialization:

- `full`: mean negative log likelihood over every completion token.
- `mapped`: mean negative log likelihood over source-mapped binding spans;
  for witness proofs also the constructor body and final connection statement.
- `rotated`: the same number of supervised completion tokens per example as
  mapped, cyclically shifted by half that completion's token count. Report overlap.

All arms see the same eight examples in the same fixed order for ten epochs,
80 optimizer steps. Same rank-8/alpha-16 q/v LoRA, float32 base and adapters,
learning rate 1e-4, AdamW, zero weight decay, gradient clipping at one, no dropout.
Use the existing adapter initialization seed 20261120. Each arm adds coefficient
0.02 times mean squared change in demonstration-token log probability from the
frozen base across the entire completion. This is an off-policy reference anchor,
not an exactly integrated KL penalty or policy-gradient update. Retokenization
is appropriate for supervised demonstrations; these are not on-policy samples.

The rotated control matches supervised-token counts and sequence compute; full
likelihood has more supervised tokens but the same data/steps. Normalize each
masked likelihood by its own selected-token count. Save token IDs, character
spans, token masks, overlap, per-step losses, reference checks and final adapters.
Verify saved-adapter reload and unchanged disabled-adapter reference probes.

## Fresh evaluation, frozen before any model outputs

Eight fresh transitions, each with invariant, nonzero and witness roots: two
new constant-shear coefficient pairs, two reverse-order shears, two shears with
time-dependent coefficients, and two shear-plus-rotation updates. Thus 24 roots
and four transition classes. They are related algebraic state-machine tasks,
not four independent scientific domains. First validate positive authoring
witnesses, empty prefixes and invalid controls; keep authoring witnesses out of
all model/training inputs. Add the existing 20 local tasks as retention checks.

Evaluate base plus all three final adapters, 16 samples on each of 44 tasks:
2,816 proposals, 512 response-token capacity, temperature/top-p one, top-k zero.
Seed 20261124 plus deterministic task hash, identical across arms. No external
helper declarations or repairs in the prompt or verifier. The model must include
any intermediate lemmas itself. Preserve exact output tokens and all verdicts.

The distinctive outcome requires mapped to achieve at least 4/16 on two fresh
nonzero/witness roots spanning two transition classes, with base/full/rotated
each at most 1/16 on those roots; at least ten percentage points composition
accuracy advantage over both trained controls; retention no more than five
points below base; and every verdict resolved. A full-likelihood tie supports
ordinary distillation, not special compiler credit. No checkpoint selection,
new seeds, evaluation-based mask edits or depth changes.

## Execution

Do not train unless all eight demonstrations, 24 authoring witnesses, 32 empty
prefix checks and invalid control resolve as intended, and token/source-map
checks pass. Use a single bounded two-hour H100 keeper under def-zhijing, manual
SSH controller, automatic release, isolated PEFT 0.10.0 overlay. Freeze execution
source and panel hashes before submission. Archive every result and small adapter
on GitHub with downloaded checksum verification. The broad goal remains active.
