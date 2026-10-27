# Checked procedure transfer: a falsifiable next experiment

October 26, 2026. Prospective design; **no new model result**. This does not
modify the frozen prefix screen, its gate, or its pending training comparison.
Preparation below is CPU-only. The next training experiment remains conditional
on an informative execution-repair result and a separate frozen training bank.
The original 64-theorem diagnostic remains the preregistered primary panel; this
new stress probe cannot replace it after results arrive.

## Decision

Test whether a model learns to **produce and consume typed intermediate facts
across an unseen dependency graph**, with all procedure scaffolds removed at
evaluation. The intervention is backward movement of a verified competence
frontier, with service reserved for weak prerequisite procedures. It is not
token entropy, more tactic strings, an ensemble, or additional inference search.

The high-upside claim is that externally checked state transitions can organize
learning around prerequisites, then compile the result into one policy capable
of composing them. The immediate test is deliberately much smaller than that
claim. It must beat learning from exactly the same proof information through
ordinary replay/SFT, and must improve statement-only completion on compositions
that were never in training. Otherwise it has not established a new mechanism.

An arbitrary conjunction of known theorems is a poor test: solving each side
independently does not require a new interface. Here intermediate witnesses,
side conditions, induction hypotheses, and arithmetic normal forms are consumed
downstream. The final obligation cannot be discharged by appending two complete
proof texts. A short generic Lean proof is still a valid success; do not impose
artificial tactic bans to force our intended route.

## What the local implementation really supports

The pinned runtime is Lean `v4.9.0-rc1`. The REPL's
`REPL/Lean/InfoTree.lean::tactics` constructs snapshots from **mctxBefore and
goalsBefore**; `REPL/Main.lean::tactics` exposes those as `proofState` handles.
Do not call a returned snapshot the state after that tactic. A persistent REPL
accepts `{"proofState": id, "tactic": text}` and returns the next handle and
goals. It also supports pickle/unpickle of proof snapshots. IDs are local to
that REPL session; the integers are not persistent semantic identifiers.

The existing Python `verify_lean4_file` starts a fresh subprocess for each call
and drops the command response's `env`. Its `allTactics=True` output is useful
for extraction, but passing one of those IDs to a later invocation cannot
resume the old process. A separate persistent recorder, or deterministic replay
of the exact source and prefix, is required. This is a new instrument, not a
silent modification of historical verifier acceptance.

Full state includes ordered goals, local declarations and let values, local
instances, universe parameters, metavariable assignments, and the environment.
Pretty-printed goals omit part of this state. Their hashes are useful debugging
keys, never evidence of semantic identity. Preserve source bytes, byte spans,
toolchain/environment hashes, and replay artifacts alongside readable states.

The current production wrapper ignores `src_context` and uses fixed imports.
The frozen tasks therefore put their definitions in `theorem_statement` and
leave `src_context` empty. Model and verifier receive identical definitions.
The authored witness compilation uses the same Mathlib/Aesop imports; final
model evaluation must still use the unchanged production correctness path.

Inspection of train-archive examples reinforces why textual heads are weak:
`lean_workbook_plus_78497` starts `induction a using Real.ind_mk` to prove
`a * 0 = 0`; `lean_workbook_plus_57637` uses induction on `Fin n` for a real
triangle inequality; `lean_workbook_plus_26494` extracts interval bounds before
nonlinear arithmetic. These share or differ in tactic names without defining
a common semantic procedure. No screen outcomes or held-out model scores were
used to choose this design. Previously selected diagnostic witnesses are not
sources for new training.

## A contract that Lean can actually check

A procedure record contains an initiation predicate, a typed output interface,
an explicit frame, and a closed certificate:

1. **Input:** a telescope `Γ` of bound variables, types, local instances and
   allowed assumptions, plus an elaborated proposition `P Γ`. Preserve binder
   dependencies and universe constraints. Never recover binders with regexes.
2. **Output:** `Q Γ`, or a dependent package `∃ w : T Γ, Q Γ w`. The procedure
   proves `∀ Γ, P Γ → Q Γ` (or the dependent package). This is its completion
   condition. An option label or a tactic-head prefix is not a contract.
3. **Frame:** goals and assumptions outside the selected obligation remain
   available, with no new axioms, admitted obligations, or unresolved
   metavariables. At first support single focused goals and closed lemma
   certificates; reject complicated shared-metavariable cuts rather than
   guessing that they are independent.
4. **Composition:** if the next procedure requires `R Γ w`, certify the adapter
   `∀ Γ w, Q Γ w → R Γ w` in Lean. A textual resemblance between `Q` and `R`
   does not authorize an edge. Any nontrivial adapter is itself a costed,
   trained procedure. Definitional equality must be checked by Lean.
5. **Certificate:** re-elaborate in the pinned environment, kernel-check the
   complete theorem, audit its constants/axioms against the allowlist, and
   reject `sorryAx` and fresh untrusted axioms. A replay that returns no goals
   is insufficient without the final closed proof check.

Initially extract only `have` subproofs and explicit lemma-sized obligations
whose entire local context can be abstracted into a closed telescope. Record
free-variable use in the elaborated term to verify a declared dependency edge.
This establishes dependence of the recorded witness, **not necessity of that
route for every possible proof**. Changed local names must not change a
contract; changed local types or values must. Validate at least these two
cases, an incompatible adapter, a missing side condition, a shared-metavariable
cut, and a replay under the wrong environment before any training.

Three starting contract schemas are concrete:

| Procedure | Initiation condition | Checked product consumed downstream |
| --- | --- | --- |
| Integer update normalization | Four integer registers and two shear coefficients | Updated determinant equals previous determinant |
| Generalized induction | Step map plus a checked invariant-preservation obligation | Invariant for every finite iteration and arbitrary initial registers |
| Positive rational update | `x ≥ 0`, positive coefficient | Updated argument is nonnegative, all actual division denominators are nonzero, and the rational step identity |

Nonzero and Bezout extraction consume the determinant produced by the second
procedure; recursive rational proofs consume positivity before instantiating
their induction hypothesis. These are different obligations even when both
implementations end in `ring`.

## Frozen transfer instrument prepared before results

`scripts/project/prepare_procedure_transfer.py` deterministically writes a
16-task panel, a separate witness file, a combined Lean witness check, and a
manifest. It does not read model outputs, generate samples, train, or overwrite
an existing directory. These artifacts are evaluation-only; do not convert
them to train rows. Names `pt_00`–`pt_15` carry no procedure hint.

| Root task schema | Count | Dependency withheld from training |
| --- | ---: | --- |
| Iterate two noncommuting integer row updates; establish determinant conservation | 4 | Concrete update normalization inside generalized induction |
| Same updates; establish a nonzero first row from a nonzero initial determinant | 4 | Discover the invariant and use it in the contradiction |
| Same updates; construct integer Bezout coefficients from initial determinant one | 4 | Discover the invariant, carry register dependencies through iteration, produce witnesses |
| Iterate `x ↦ x/(1+k*x)`; prove the closed form for all `n`, assuming only `x ≥ 0` | 4 | Domain preservation enables the generalized induction hypothesis; denominator conditions enable normalization |

Integer coefficients are fixed to `(2,3), (3,2), (2,5), (5,2)`; rational
coefficients are `2,3,5,7`. The second row update consumes the first row's new
value. Both induction families are tail recursive, so fixing the initial
registers before induction gives an unusably weak hypothesis. In the nonzero
and Bezout tasks the root statement does not supply the invariant.

The four numerical variants per schema are correlated replication of a
template, not four independent discoveries. There are two domains and four
target schemas. Report all task outcomes and macro averages by schema/domain;
do not bootstrap 16 rows and claim broad theorem-family generalization. This
is a synthetic dependency-composition test, not a claim of novel mathematics
or pretrained-data absence. A trained model may already know these algorithms.

Training may include individual contracts and **different** small compositions
with different state representations: one-step shear identities, generic
predicate induction over a supplied invariant-preserving function, scalar
affine recurrence induction, determinant-to-witness extraction with the
determinant already supplied, and standalone rational identities with all
denominator premises supplied. Training must exclude these sixteen roots,
their full witnesses, their instantiated multi-edge dependency graphs, and
any paraphrased/renamed equivalent of them. Parameter changes alone do not make
a training example safe. A hand-reviewed graph-level exclusion ledger is a
precondition for launch.

No adaptive task replacement is permitted after model outcomes. If the base
solves everything, the panel is saturated and cannot establish new capability.
If all methods fail, inspect training-only contract execution and report the
floor. Neither outcome licenses silently replacing tasks while retaining the
same prospective claim. New natural-theorem transfer would require a new,
separately frozen family panel; the present random64 diagnostic is not it.

## The intervention and the comparisons

First construct a small **training-only** DAG bank of checked contracts from
registered train proofs and the allowed atomic schemas above. Freeze its
source, certificates, adapters, eligible predecessor states, and all available
demonstrations before optimization. Training graph roots are distinct from the
transfer panel. The current prefix screen cannot establish this bank for free.

The first frontier experiment should compare:

* **Frontier RL:** 30% of proposals practice bank roots, 70% practice checked
  prerequisite frontiers. Start at the final unsolved contract in each training
  graph. A node advances to its predecessor only after two consecutive
  16-attempt training groups each achieve at least 12 successes. Reserve equal
  quotas across active contract schemas; retain 20% of frontier allocation for
  previously mastered nodes. If a retained node falls below 8/16, reactivate it.
* **Uniform-state RL:** exactly the same bank, demonstrations, root fraction,
  available states, certificates, and update rule; sample intermediate states
  uniformly rather than moving a mastery frontier. It receives all information
  available to the intervention. This is the primary mechanism comparison.
* **Same-information SFT/replay:** pristine base trained on the complete same
  bank and verified successful training continuations, including those exposed
  by frontier RL. Match optimized response-token budget as closely as possible;
  report tokens and steps separately. This baseline is allowed to see the
  frontier's useful discoveries. Charge their collection cost to the comparison;
  do not describe zero-cost recycled demonstrations as a compute saving.
* **Frozen base with retrieval:** same bank and deterministic retrieval rule,
  fixed before transfer evaluation, alongside the frozen base without retrieval.
  Charge demonstration tokens, retrieval work, generated tokens, and all Lean
  calls. Its role is to reveal information/elicitation sufficiency; retrieval
  success is not learning. No held-out witnesses are in its index.

Use one final policy per training arm, same initialization, ordinary Lean binary
correctness, suffix-only loss when a start is supplied, and identical optimizer,
KL and sampling settings. No hard blocking or learned judge. Start with a
32,768-proposal cap per RL arm, including mastery checks and maintenance draws.
Do not mix this comparison into the currently registered root-versus-prefix
pilot: it answers a different question. Training-bank size and exact allocation
integer rounding must be fixed before launch, after the bank exists.

SFT cannot generally be simultaneously matched on proposals, successful target
tokens, optimizer steps and total collection cost. Publish the full cost vector;
make claims only at the matched boundary. A result that requires much more
information or work is still measurable, but it is not an isolated scheduling
benefit. Do not save unsuccessful proposals out of compute accounting.

## Measurement and decisive outcomes

Freeze the final checkpoint rule to the proposal cap or a preregistered training
failure condition. Never choose a checkpoint using this transfer panel. Evaluate
the frozen base, final RL arms and SFT at 32 fresh independent continuations per
task: **512 proposals per policy**. Use temperature 1, top-p 1, top-k disabled,
512 generated tokens, identical prompt limits, and the unchanged Lean verifier.
The exact authored witness need not fit a model's chosen proof style; token
feasibility is checked before inference and reported.

The primary root test supplies only imports, definitions and theorem statement.
No prefix, state dump, contract names, hint, witness, procedure selector, external
memory, retrieval, search feedback, or model routing is allowed. The evaluation
runner must assert empty `proof_prefix` and an empty retrieval payload. One
policy emits one ordinary full proof per independent attempt. All valid routes
count, including an unexpectedly short library solution.

Report:

1. **Root competence:** schema/domain-balanced per-attempt correctness, paired
   differences to uniform RL and SFT, and empirical pass@8/pass@32. Pass@8 can
   be estimated from 32 draws as `1-C(32-c,8)/C(32,8)` with appropriate edge
   cases. Also disclose number of tasks with any success; this is not pass@1.
2. **Interface execution:** separate atomic held-out instantiations, same
   supplied Lean states across policies; fraction producing the required typed
   output, adapter success, and end-to-end proof success. Freeze these atomic
   instances in the training-bank manifest before model inference. They must
   not be silently supplied to the primary root evaluation.
3. **Composition gap:** root error despite successful execution of each relevant
   atomic contract, reported per schema. Do not multiply marginal atomic
   accuracies into a causal prediction: their errors and state distributions
   are dependent. The question is whether root ability improves while atomic
   ability remains comparable.
4. **Audited use:** on a fixed subset selected by task ID before inference,
   replay complete proofs and identify typed interfaces/dependencies. Report
   bypass routes too. Absence of our intended intermediate lemma does not make
   a correct solution incorrect; it limits the mechanism attribution.
5. **Costs and failures:** every proposal, generated/supplied token, accepted
   optimizer token/group, verifier call, timeout, checkpoint failure and elapsed
   wall time; include retained-node maintenance and state extraction.

For this small instrument, a material signal is at least a ten-point root
per-attempt improvement over **both** same-information uniform RL and SFT,
positive improvement in both domains, and newly solved tasks in at least two
target schemas. These are exploration decision rules, not significance claims.
Report uncertainty and all correlated task outcomes without adding seeds just
to sharpen a favorable interval. Strong supplied-state execution with no root
gain remains conditional procedure repair. Root gains on this panel support
synthetic compositional transfer only; they do not establish a revolutionary
general training paradigm.

**Kill or redirect the relevant mechanism claim.** Matching uniform-state RL
would remove the claimed benefit of mastery scheduling. Matching SFT given all
frontier-discovered successes would remove the claimed need for its RL update;
the separate acquisition question is described below. Redirect the composition
claim if retrieval alone explains the practical gain, mastered atomic contracts
do not reduce the composition gap, different names or harmless local-context
additions destroy the effect, full-proof checking disagrees with contract
checking, or admission/token-budget differences explain the improvement. A training-only atom failure
is a signal/optimization failure; a root failure with mastered atoms is the
stronger falsification of the proposed compositional mechanism. Distinguish them.

### Independent critique: creation is separate from execution

A checked contract certifies extensional compatibility. It does not establish
that a neural policy has acquired a reusable internal option. Oracle starts can
make execution reliable while leaving invariant invention, variable
generalization, and selection of useful intermediate statements untouched. A
positive prefix screen therefore does not justify a large scheduling framework
by itself. The small recorder and closed-certificate instruments below address
measurement validity; they are not evidence for this learning hypothesis.

There are also two distinct claims about frontier training. If SFT receives
frontier-discovered successes and matches its root gains, that challenges the
need for the RL update, but does not by itself falsify frontier-guided **data
acquisition**. A later acquisition claim would need a separately registered
comparison against base/uniform-collected successes at the same total
collection budget. No extra arm or budget is silently added to the current
pilot. Report information, collection work, and optimization work separately.

If mastered atoms fail to transfer to roots, the next discriminating instrument
is a **producer–consumer crossover**, not another prefix quota sweep:

1. Before any of its model outcomes, freeze a separate two-domain interface
   panel using training-owned atomic schemas and new graph/representation
   combinations. Exclude every frozen sixteen-task root and witness, including
   renamed equivalents. Its IDs, source lineage, graph splits, and atomic
   mastery checks require a reviewed manifest before launch.
2. A producer receives a transition definition and admissible initial states,
   without the downstream target. It proposes a closed invariant or summary
   and supplies initialization/preservation proofs. Lean checks the exact
   interface and proofs. Valid but uninformative summaries remain eligible;
   usefulness is assessed downstream rather than by an oracle filter.
3. Feed each **same checked artifact** separately to frozen-base and trained
   consumers on two withheld downstream obligations. Cross base/trained
   producers with base/trained consumers. Pass only a normalized closed
   interface and its certified lemma; remove the producer's reasoning text.
   Each proposal is paired by ID; invalid, rejected, or irrelevant producer
   outputs count in end-to-end failure/cost accounting. No best-of selection
   using the held-out target is permitted.
4. Separately authored oracle interfaces localize execution failure. These
   reference interfaces belong only to this new diagnostic panel; they never
   enter the statement-only primary sixteen-task evaluation or training.
   Fix proposal counts, selection, and certificate-cost limits in the new
   manifest before any model execution, rather than choosing them from results.
5. Report producer validity, downstream usefulness, and complete end-to-end
   success. Improvement from trained-producer artifacts even for the frozen
   consumer, across new graphs/representations, would support portable interface
   creation. Gains only for trained consumers supplied oracle interfaces support
   conditional execution. Good oracle execution plus poor self-produced
   interfaces and unchanged roots would reject automatic composition as the
   explanation.

This diagnostic deliberately exposes an interface so that its contribution
can be measured. It is not evidence that an unassisted single policy transfers;
the separate statement-only root evaluation remains necessary. A possible
redirect is learning to synthesize useful certified intermediate abstractions,
with downstream credit across several consumers, rather than redistributing
practice among fixed starts. This is a prospective hypothesis, not a novelty
claim or authorization to train before the new bank and controls exist.

## Concrete prepared next step and remaining gates

Prepare the frozen panel, without any model execution:

```bash
python3 scripts/project/prepare_procedure_transfer.py \
  --output ../runs/procedure-transfer-panel-20261026

PYTHONPATH="$PWD" ../environment/venv/bin/python \
  scripts/project/materialize_procedure_transfer.py \
  --panel ../runs/procedure-transfer-panel-20261026 --model ../models/base
```

The generator refuses an existing directory. The dated directory already
exists from this preparation; use a new audit directory only to reproduce the
same hashes. Do not interpret re-running it as permission to train on its rows.

The CPU observation instruments now demonstrate persistent replay of a newly
authored `have` proof and separate closed theorem/adapter certification, with
name invariance, incompatible-interface rejection, and production-wrapper
agreement for the atomic shear. They do not automatically extract arbitrary
closed contracts from saved states; all unproved cuts remain unsupported.
There is no frozen disjoint contract-training bank or atomic evaluation panel
yet. Only after those artifacts and the prefix-pilot evidence are reviewed is
the frontier training comparison runnable. No GPU job was launched for this design.

Validation/provenance details are recorded below after the fixed witnesses and
prompt lengths have been checked. Existing screen artifacts are untouched.

### Completed authoring validation

The panel and exact model inputs were frozen before reading any new GPU-screen
result. Compact evidence is `results/procedure_transfer_panel_20261026.json`;
the artifacts are in `../runs/procedure-transfer-panel-20261026`.

* All 16 authored witnesses compiled together with pinned `lake env lean`:
  exit code 0. The remaining messages are unused-variable/sequence-focus lints,
  `ring_nf` suggestions and preexisting local package-change notices. This was
  one CPU process, no model generation. Compilation is a feasibility check;
  a final model evaluation still requires the production verifier.
* Exact model prompts are frozen separately in `model_inputs.jsonl`, SHA-256
  `1fc859633af94c280d702f6050c5cd08446a2b9530e43647d4a0240838a7cb51`.
  The input-only `root_eval.parquet` SHA-256 is
  `adec52d6186692c35623feee4a9eca29028b630521c6c4b27586755d65faa2f2`.
  Its materializer never opens witness files, checks the statement hashes,
  reconstructs each exact prompt after parquet readback, rejects prompt
  overflow, and asserts test splits, unique IDs and empty prefixes. Witness
  text and dependency-graph labels are absent from the exported input columns.
* Prompts contain 144–245 tokens. Authored witnesses, including the closing
  fence, contain 150–282 response tokens. Both fit the frozen 512-token limits.
  The tokenizer is the pinned local DeepSeek-Prover-V1.5-SFT tokenizer.
* Original manifest SHA-256:
  `83ad8c87e356768e550839cc742a62c171558e312fbb92226caceaba6b01c15d`.
  Its pre-validation status text remains immutable; the compact evidence file
  records the subsequent successful Lean and token audits.
* Before freezing, three scratch two-theorem authoring checks failed: first
  the Real recursion required `noncomputable`; second rational normalization
  left `True ∨ x = 0`; third explicit denominator facts still left the same
  propositional remainder. Marking the definition noncomputable and adding
  final `simp` resolved those errors. The fourth check compiled the entire
  fixed panel. These are developer proof repairs, not model trials or task
  selection by model performance; no claims about model success follow.

Portable-path project preflight passed. The default preflight initially used a
stale historical Python path; supplying the actual bundle `RESTRICTION_VENV`
resolved that configuration issue. No training source, pinned screen, model
checkpoint, scheduler job or historical protocol was changed by this work.

### Independent production validation and witness erratum

The original combined compilation was insufficient to establish production
acceptance. The first individual production-wrapper check accepted all twelve
integer witnesses but rejected all four rational witnesses. Raw diagnosis found
three name-ambiguity errors per rational proof: production's `open Nat` exposes
`Nat.ne_of_gt` alongside the root theorem. The authoring header had no namespace
opens. This was an actual elaboration failure, not a timeout or warning filter.

The original frozen directory, task statements, and input-only parquet remain
byte-identical. The separately published
`research/instrument_snapshots/procedure_transfer_witness_erratum_20261026.jsonl`
qualifies exactly three `ne_of_gt` calls per rational witness as
`_root_.ne_of_gt`. The checker authenticates original statement/witness hashes
and rejects any broader edit. These repaired witnesses are evaluation-only;
they are never supplied to the model. Each has 222 response tokens, within the
unchanged 512-token limit.

A second complete production-wrapper check accepts all sixteen witnesses and
the independently authored atomic shear, and rejects a `sorry` control.
Accounting is 18 initial checks + 5 raw diagnostic checks + 18 final checks =
41 Lean calls, including failures. The first wrapper run took 204.16 seconds
including verifier staging; the final reused-stage run took 79.68 seconds.
The production verifier was not changed. Its process-name timeout monitor was
avoided during other long-lived sessions, and both wrapper invocations had a
1,200-second outer process-group deadline.

Compact outcomes, hashes, exact run locations, and source snapshots are linked
from `results/procedure_transfer_production_check_20261026.json`. The complete
project test run now passes 196 tests. This repairs an instrument-validity gap;
it supplies no evidence of model learning, transfer, or a new paradigm.
