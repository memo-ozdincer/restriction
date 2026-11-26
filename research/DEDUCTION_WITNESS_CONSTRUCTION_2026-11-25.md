# Deduction versus witness construction

User-designated research direction, November 25, 2026. Independent of the
failed-proof recoverability direction. No new training or sampling is authorized
by this initial retrospective screen.

## Four-step program

1. Read actual internal model attempts, identify sharply interpretable examples,
   and build an evolving classification.
2. Compare the same formal statements across pristine SFT (C0), ordinary GRPO
   (C1), Rewarding-the-Unlikely (C2), and hard exclusion (C3). Where matched
   deduction/witness formulations do not exist, distinguish same-statement
   comparisons from prospective matched-formulation experiments.
3. Review primary research on existential proof search, witness generation,
   constructive proof, mathematical task reformulation, and RLVR.
4. Prioritize actual external model rollouts, including failures, with statements,
   model/checkpoint, verifier labels and accessible records.

## Prospective retrospective-screen hypothesis

Explicit witness-selection failures and post-selection proof-completion failures
are separable in archived attempts. RL may change their prevalence differently
from nonexistential theorem proving. A first descriptive screen will compare
top-level existential statements and other statements in the matched 467-root
pass@128 banks, inspecting actual successes and failures; this is a lexical
screen, not a causal contrast, since theorem difficulty and automation differ.
Do not treat aggregate differences as proof of the phenomenon. Preserve
unclassified attempts and identify concrete examples of numeric, symbolic,
set-valued, and implicit/generated witnesses, along with deduction-only
examples. No new model proposals, no learned judge, no modification to archived
verdicts. Inspect exact statement and proof text before expanding the taxonomy.

## Working classification (revise from proof evidence)

The label **deduction versus witness construction** names the research direction,
not a dichotomy of everything in mathematics. A proof of an existential claim is
also a deduction; a universal proof can contain existential subgoals, or demand
a symbolic certificate for a contradiction. Classify the **operation** rather
than just the outer connective.

| Operation | Observable question | Evidence / counterexample |
|---|---|---|
| Deduction given a certificate | Can the model establish P(w) with w fixed? | Right triangle substituted witness; determinant contradiction |
| Numeric witness selection | Can it choose concrete numbers satisfying P? | Right triangle, Pell |
| Symbolic witness synthesis | Can it map given inputs to valid expressions? | Factorial square, Bézout coefficients |
| Structural/function synthesis | Can it construct a set, function, or algorithm with a universal contract? | Empty sets, IMO 1993 P5 |
| Witness extraction/transport | Can it instantiate or transform existing evidence? | Determinant/Bézout, Pell coordinate map |
| Post-selection closure | Once a valid witness appears, can it prove its constraints? | Factorial square, mod-8 counterexample |
| Admissibility/specification | Does an accepted witness actually satisfy the intended form? | Workbook shortcuts and ECP circular witnesses |

These tags overlap. A witness may be generated explicitly, inferred by tactics,
extracted from an existing existential hypothesis, or established classically.
A tuple constructor may introduce a conjunction rather than a witness.
`use` may occur inside an otherwise nonexistential theorem. The distinction
between proposing a candidate, certifying it mathematically, and emitting valid
Lean is essential.

A clean future paired formulation uses the **same** predicate P(X,Y), context X,
and ordinary verifier: (A) prove P(X,w(X)) for a supplied admissible expression;
(B) construct Y and prove P(X,Y). A third diagnostic supplies w only after
sampling, retains the proof tail, and verifies independently. Compare both
versions on the same pre/post-RL checkpoints under matched generation budgets,
with explicit candidate type and admissibility rules. This changes availability
of the solution by design; it isolates verification versus selection, not two
logically identical statements or a causal measure of general intelligence.
Use training examples for instrument development and freeze independently
selected held-out examples for new evaluation; do not derive a new training
blocklist from test outputs.

## Step 1 — strongest internal examples

### A. Literal witness is the bottleneck: right triangle

[Original experiment](experiments/numeric_witness_blocking_20261123/README.md).
Require positive ordered natural numbers a,b with a²+b²=65². Sample 0 from the
recursive-GRPO actor:

```lean
  use 11, 60
  norm_num
```

Rejected: 11²+60²=3721, not 4225. Sample 3 likewise uses 15,64 and
`decide`. All 16 original attempts failed. Replacing **only** the witness
expressions with any of (16,63), (25,60), (33,56), (39,52) gave 64/64 verified
proofs; substituting (1,2) gave 0/16. The tactic tails are unchanged. This is the
sharpest selection-versus-certification evidence. The valid choices were supplied
externally, and no matched pre-RL draw bank exists for this exact intervention.
Source: discovery/samples.json, repair/results.json and full source/verdict pairs.

### B. Given invariant, deduction but not symbolic witness construction

[Repaired-library result](REPAIRED_LIBRARY_RESULT_2026-11-19.md). Given output
matrix entries x,y,z,w and xw−yz=ad−bc, nonzero input determinant implies
x≠0 or y≠0. One actual base continuation is:

```lean
  contrapose h
  simp_all
```

27/128 linked nonzero attempts accepted; both bare and reflexive-fact arms
0/128. All accepted continuations fail both dependency controls. With the
same determinant invariant and input determinant 1, the witness task asks for
u,v such that ux+vy=1; u=w,v=−z works, yet linked samples are 0/128.
This is symbolic selection, not literal arithmetic. The fact was authored and
the proof scope repaired externally; the goals are different consequences,
not logically equivalent reformulations. See the four full proof chains in
[repaired_library_20261119](experiments/repaired_library_20261119/).

### C. Correct witness but failed closure: factorial square

Archived MiniF2F root `amc12b_2020_p6`: for n≥9 prove that
((n+2)!−(n+1)!)/n! is a square of a natural number. Expanding the factorials
gives (n+1)². Actual C1 failed proof:

```lean
  use (n + 2 - 1)
  norm_num
  ring_nf
  field_simp [h₀]
  ring_nf
  norm_cast
```

A C1 success uses the same witness, but a different tail:

```lean
  use (n + 2 - 1)
  norm_num [Nat.factorial_succ, Nat.mul_sub_left_distrib, Nat.add_sub_cancel, Nat.factorial_succ]
  field_simp
  ring_nf
```

A C0 failed proposal instead chooses (n+2−1)(n+1−1), i.e. n(n+1).
This demonstrates both selection and closure failures within *one* statement.
No fresh Lean judgments: acceptance is the original recorded outcome.

### D. Nonexistential statement with constructive subproblem: mod-8

The held-out `numbertheory_notequiv2i2jasqbsqdiv8` is a negated universal claim.
To refute it, one can choose (2,0), where both entries are even but the squared
sum is 4 and hence not divisible by 8. C0 and C3 find accepted proofs; C1
generates mathematically valid counterexample pairs in 64/128 archived attempts
but accepts 0/128. C3's scan detects such pairs in 57/128 and accepts 4/128
(C0 1/128; C2 3/128 overall). The scan is limited to recognizable literal
pairs and is not a measure of semantic reasoning. Source:
[recursive blocking diagnosis](experiments/recursive_blocking_20261123/README.md).
This shows why outer existential syntax cannot define the whole phenomenon.

### E. Changing coordinate exposes a familiar witness

[Matched Pell coordinate screen](experiments/pell_coordinates_20261123/README.md).
After forbidden |x|=1,5, the goal asks for a new integer solution to x²−6y²=1.
C1 direct and callable-menu prompts yield 0/16 each. Forcing forward coordinates
yields 6/16, all selecting (5,2) and decoding to (49,20); inverse coordinates
0/16. One actual inverse sample starts `use 5, 2; norm_num` (two lines).
Reflecting only its second coordinate repairs 10/16 inverse attempts and destroys
all six forward successes, with negating both as a control. This is a
representation-sensitive witness choice, not new model discovery. The historical
C1 prompting discrepancy qualifies all these standalone results.

### F. Witness correctness depends on statement design

Workbook `lean_workbook_plus_6203` accepts `use 1, 0; norm_num` and
`use 17, 0; norm_num` because the outer disjunction permits the first clause
alone. Another workbook theorem permits both empty sets; 116/128 original
proposals passed and all 29 distinct accepted bodies use empty sets. Strengthened
nonempty statement rejected all 36 distinct replayed bodies. These are not
failures of Lean; they are examples of specification shortcuts and why a
mechanistically meaningful witness class needs admissibility.
[Actual GRPO witness panel](experiments/grpo_witness_panel_20261123/panel.json);
[empty-set replay](experiments/witness_blocking_20261123/README.md).

## Step 2 — effect of pre/post-RL on identical formulations

### Matched supplied-invariant pair, existing base and GRPO runs

The prior [local-context materialization study](INTERFACE_MATERIALIZATION_RESULT_2026-11-19.md)
gives the closest already-completed pre/post comparison on a matched
deduction/witness family. Both share the authored quadratic invariant. Same
formal targets, 32 samples per local-context cell:

| Task | C0 | C1 |
|---|---:|---:|
| quadratic2 nonzero | 1/32 (8 unresolved) | 1/32 |
| quadratic2 Bézout | 0/32 | 0/32 |
| quadratic3 nonzero | 0/32 | 0/32 |
| quadratic3 Bézout | 0/32 | 0/32 |

Both global invariant conditions and all earlier bare conditions score zero.
This is a floor-limited null comparison, **not evidence that RL preserves or
worsens the gap**. The higher-success repaired-library panel was only run with
the pristine base. It has no matched C1 cell. A prospective matched higher-signal
evaluation would therefore be informative, but needs validated native prompts,
unchanged Lean and actual checkpoints. The local Mac preflight cannot execute
the pinned GPU workflow; no new sampling was done.

### Registered archival screen, exact same 467 statements

All four original pass@128 member hashes authenticate against the recovery
inventory; 467 theorem statement/context identities match exactly across
models. Use 59,776 registered proposals per model, excluding 128 physical
padding rows each. No freshness, prompt, reward, or verifier change. The lexical
screen conservatively separates outer ∃ / ∃!, nested ∃, and other conclusions.
No semantic claim about the latter being deduction-only.

| Category | Roots | C0 accepted | C1 accepted | C2 accepted | C3 accepted |
|---|---:|---:|---:|---:|---:|
| Outer existential | 9 | 86/1152 | 105/1152 | 119/1152 | 102/1152 |
| Nested existential | 5 | 1/640 | 0/640 | 3/640 | 7/640 |
| Other | 453 | 25223/57984 | 29067/57984 | 27515/57984 | 27891/57984 |

Only two outer-existential roots are solved by every model: factorial square and
`amc12a_2002_p6` (trivial valid p=0 or p=1). All seven remaining roots have no
observed verified sample under any model. Outer-∃ gains are therefore driven by
within-root improvement, not new solved roots. Other-statement accuracy also
increases under C1. The contrast does not measure a deduction-construction gap
because theorem difficulty and opportunity are not matched across categories.

For the factorial square root, conservatively count only first recognizable
candidate lines exactly equal to `use (n + 1)` or `use (n + 2 - 1)`.
All other syntax stays unclassified, not labelled wrong; those include successes.

| Policy | Known-correct exact candidate forms | Accepted among these | All accepted |
|---|---:|---:|---:|
| C0 | 43/128 | 9/43 | 11/128 |
| C1 | 58/128 | 29/58 | 29/128 |
| C2 | 54/128 | 27/54 | 28/128 |
| C3 | 35/128 | 19/35 | 23/128 |

Ordinary GRPO both samples these particular correct expressions more frequently
and closes them more often; C3 closes them more often despite lower observed
frequency. This is a narrow lexical conditional comparison, not a matched
intervention on witness choice, and C1/C3 optimizer settings differ. The
counts support a two-component lens rather than any claim that RL necessarily
reduces witness competence.

Another same-statement example, IMO 1993 P5, requires a strictly increasing
function f with f(1)=2 and f(f(n))=f(n)+n. All four arms fail 128/128. Actual
C0 selects f(n)=n+1; C1 selects f(n)=2n. Neither meets the functional equation
in general. More explicit constructor syntax is not necessarily better
construction: outer-∃ attempts containing use/existsi/exact/refine tuple syntax
number 1045, 1111, 1116, 1120 respectively across C0/C1/C2/C3 (lexical proxy,
not proof-state-level witness frequency).

[Full per-root counts](experiments/deduction_witness_20261125/screen-summary.json),
[all 7,168 original attempts on 14 diagnostic roots](experiments/deduction_witness_20261125/selected-attempts.json.gz).
All proposal IDs and original labels retained. Screen source:
`scripts/project/screen_deduction_witness.py`; no new model or verifier calls.

## Step 3 — closest primary studies

1. Sun et al., [Formally Solving Answer-Construction Problems in Lean (LPAR 2026)](https://www.floc-conference.org/publications/paper/NnrB/open).
   **Most direct precedent.** Separates unknown answer synthesis from proving a
   specification after substituting the answer. Introduces admissibility rules
   to exclude circular or inappropriate witnesses, distinguishes find-any from
   find-all tasks, and compares general and prover LLMs with ECP. Reports 17/346
   PutnamBench and 18/75 MathArena tasks solved with admissible answers/proofs.
   Not a controlled SFT-vs-RL change on identical model lineage. Its 2025
   [ConstructiveBench preprint](https://arxiv.org/abs/2505.18492) uses a broader
   competition corpus; do not conflate its metrics with the revised LPAR panel.
2. Yang et al., [Construction-Verification: A Benchmark for Applied Mathematics
   in Lean 4](https://arxiv.org/html/2602.01291v1), AMBER. Separates explicit
   evaluation, algorithm design, representation transformation and theorem
   proving. General reasoning models outperform specialized provers on the
   constructive tasks; authors suggest tactical overfitting and instruction
   following. Appendix E discusses an actual Kimina scope/tactic error. This
   supports an alternative explanation to mathematical weakness: proof-format
   specialization. It does not establish the causal effect of RL alone.
3. Li et al., [Learning to Disprove](https://arxiv.org/html/2603.19514v2),
   October 14 revision. Treats producing counterexamples and verifying them
   formally as distinct operations; multi-reward expert iteration and
   hypothesis-removal synthesis. Their corrected appendix distinguishes errors
   in prior reported cases from corrected specifications. Directly relevant
   to symbolic/numeric counterexample witnesses, not general find-any synthesis.
4. Yue et al., [Does Reinforcement Learning Really Incentivize Reasoning
   Capacity in LLMs Beyond the Base Model?](https://arxiv.org/abs/2504.13837).
   Compares matched model families using large pass@k; reports distributional
   concentration after RL. Relevant to our sampling-based comparisons but not
   a witness-specific taxonomy or direct evidence of the proposed gap.
5. Pham et al., [TheoremBench](https://arxiv.org/abs/2606.09450). Premised and
   plain theorem variants measure dependencies and use of explicit intermediate
   facts. Relevant for the supplied-invariant control; not an answer-construction
   guarantee.

Prior art exists. A distinct scientific question remains: does matched RL
change witness selection, admissibility, and conditional proof completion
differently on the same families, and does that generalize across domains?

## Step 4 — external actual rollouts, not just reference answers

| Priority | Corpus | What can actually be read |
|---|---|---|
| 1 | [ECP LPAR artifacts](https://github.com/sunjia72/ecp-lpar/tree/55f1d730825e8d537eebc72487f375a460deee6b/output_artifact_eval) | Direct proposer and proof generation records, accepted and inadmissible outputs, solver history. Three compact files fetched and inspected (below). |
| 2 | [Public DeepSeek V1.5-RL four-sample bank](https://huggingface.co/datasets/autores/DSP1.5RL-minif2f-sampling_4) | 1,952 statement/proof/verifier rows; 14 selected roots (56 public rows) match our formal statements. Local pinned parquet, exact status counts saved. |
| 3 | [EPFL-LARA evaluation benchmark](https://huggingface.co/datasets/EPFL-LARA/lean-evaluation-benchmark) | 68,932 source/verifier-labelled rows from three independent provers on MiniF2F plus ProofNet. Provides cross-domain candidates, not a pre/post pair. Local pinned parquet inspected. |
| 4 | [MiniF2F traces](https://huggingface.co/datasets/kobyjl/mini_f2f_traces) | 3,940 grade-labelled DeepSeek-V2-7B traces with informal and Lean proof text. Local file inspected. |
| 5 | [World model SFT](https://huggingface.co/datasets/VladShash/WM8-SFT-minif2f-1) / [GRPO](https://huggingface.co/datasets/VladShash/WM8-GRPO-minif2f-1) | Both 488-root raw banks, 32 maximum attempts, headers/statements and generated Lean text; no verifier labels in these files. Useful for inspection, not accuracy claims without matching verified results. |
| 6 | [ConstructiveBench](https://huggingface.co/datasets/sunjia72/ConstructiveBench), AMBER and PutnamBench | Good prospective tasks but prioritize the above already generated trajectories. |

ECP example: Goedel-Prover-V2-32B output `putnam_1962_a5_g21_corr1_g0_corr2_g0`
proposes the *original sum* as the requested answer function. Its proof uses
reflexivity. Lean accepts it but the authors' admissibility check rejects it.
This shows a new category: **valid proof, non-answer**. It is not a false
mathematical witness; the intended closed-form construction is missing.
The full downloaded output sits at
`artifacts/failed-proof-corpora/ecp-lpar/inadmissible_proofs.jsonl`.
The exact output may be read [in the pinned source](https://github.com/sunjia72/ecp-lpar/blob/55f1d730825e8d537eebc72487f375a460deee6b/output_artifact_eval/putnam_llm_baseline_Goedel-Prover-V2-32B/inadmissible_proofs.jsonl).

Public V1.5-RL examples inspected: factorial square 3/4 accepted, again uses
the correct n+1 witness and explains the cancellation; IMO 1993 P5 0/4, including
a sample proposing n+1 and incorrectly simplifying 2n+1 to n+2. The latter is
a concrete independent instance of bad function selection coupled with invalid
deduction. The public bank uses different generation and verification settings;
its four samples cannot fit a causal comparison against our 128-sample banks.

All external files except the new ECP logs reuse the pinned prior download
inventories in [failed_proof_corpus_20261125](experiments/failed_proof_corpus_20261125/).
The ECP inventory records exact paths, sizes and checksums. Raw external files
remain local and independently downloadable; no claim they are backed up here.

### External cross-domain proof inspection

Four actual Pythagoras-Prover-4B ProofNet outputs were inspected in the pinned
EPFL-LARA parquet (Lean v4.15.0).

- `exercise_1_11a`, samples 0 and 2: polar decomposition of complex z into a
  real magnitude r and unit complex w. Both choose (0,1) for zero and
  (|z|,z/|z|) otherwise. Sample 0 passes, sample 2 has a Lean error.
  Hence valid symbolic witness expressions do not ensure a formal proof.
- `exercise_2_3_2`, samples 2 and 3: given a,b in a group, find g such that
  ba=gabg⁻¹. Sample 2 chooses a⁻¹, sample 3 chooses b. Both are mathematically
  valid, but only sample 3 passes the recorded verifier. This is an independent
  abstract-algebra example of post-selection closure difficulty, not evidence
  that a⁻¹ is the wrong witness.

Both pairs are actual same-model, same-statement examples. They are not
matched pre/post training comparisons, nor fresh rechecks. The exact selected
run/sample/candidate IDs, source checksums and labels are in
[proofnet-example-identities.json](experiments/deduction_witness_20261125/proofnet-example-identities.json);
source remains in the pinned local parquet. Caution: the public corpus
reuses some ProofNet names for different theorem statements (e.g. exercise_2_29
has different goals in different records); never join by name alone.

## User clarification: exactly two categories, matched pre/post-RL contrast

The research classification is now strictly **deduction** versus **witness
construction**. Selection, closure, transport and admissibility in the earlier
working notes are diagnostics within these two categories, not additional
categories. The requested evidence is a four-cell comparison, ideally on the
same mathematical facts across the same model lineage before/after RL.

Recovered the actual 256 local-invariant oracle attempts (two recurrence
variants × two tasks × two checkpoints × 32). The release archive SHA-256 and
all 38 member hashes authenticate against the tracked inventory. Within each
task the original prompt is byte-identical across pre/post-RL. Exact
completions, original verifier judgments, IDs, and prompts are in
[paired-local-invariant.json](experiments/deduction_witness_20261125/paired-local-invariant.json).
No fresh inference or verifier calls.

For x²−2y²=1, the deduction task is x≠0 and the witness task asks for integers
u,v with ux+vy=1. Correct witness (x,−2y). Among the 32 witness attempts per
checkpoint, exactly the same wrong continuation `use (orbit n).1, (orbit n).2`
followed by `linarith` appears 20 times pre-RL and 23 times post-RL.
Deduction accepts 1/32 at both stages (eight pre-RL timeouts); witness
construction accepts 0/32 at both stages. The second recurrence variant has
zero successes in all four cells. This is exactly matched but floor-limited;
there is no established post-RL directional change in the gap.

Public search did not identify an independent released bank with matched
deduction/witness formulations, verified outcomes and known pre/post RL
lineage. ECP provides construction/verification logs without a matched RL
lineage; public V1.5-RL and WM8 banks do not provide the paired task design
and the WM8 raw files lack verdicts. Do not combine unrelated corpus scores
to pretend a controlled contrast. Future examples should be delivered in
chat, not opened in the browser, per user preference.
