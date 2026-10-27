# Evidence audit and first mechanism

2026-10-26. This is a design and data-availability audit, not a new model result.
The latest user request opens a new research program; historical C0–C5 recipes
and their claim boundaries remain frozen.

## What the completed evidence says

- The latest matched comparison favors C2 soft unlikeliness over C3 frozen
  zero-advantage blocking: held-out correct tactic signatures 12,006 versus
  10,444; expected signatures at 16 correct draws 10.9667 versus 10.1568; both
  solve 277 of 467 theorems at pass@128. See `CAPABILITY_RETENTION.md` and
  `results/c2_unlikeliness_vs_c3_seed42_pass128.json`.
- C1 and C3 differ in optimizer settings, and their matched no-exploration
  control remains incomplete. C3-over-C1 differences cannot isolate blocking.
- Recovered tactic signatures include redundant elementary proof steps.
  `C2_C3_PROOF_CHARACTERISTICS.md` and `BASE_OVERLAP_WEIGHTING.md` support an
  observed-distribution distinction, not newly acquired mathematical methods.
- C5 reward rejection has no eligible final result. Its October diagnostic
  reached step 20 but failed its throughput screen. Restarting another full
  C5 run is not the highest-value first action for the new objective.
- All-correct prompt admission explains a real implementation difference but
  is not unique to hard blocking; admission-aware soft weighting also creates
  gradient signal. See `SATURATED_PROMPT_MECHANISM.md`.

The proposal's strongest unresolved question is therefore execution competence:
does allocating learning opportunities to weak procedures make those procedures
more reliable, and does that reliability transfer after the allocation aid is
removed?

## First priority: reserve practice for weak procedures

Use verified incomplete proof prefixes as explicit continuation contexts, with
bounded practice allocated across routes rather than determined entirely by
their current sampling prevalence. Normalize rewards inside each continuation
task. The operating-system correspondence is scheduling service for jobs that
would otherwise starve: a job is a theorem/route context, service is verified
rollouts plus optimizer work, and completion quality is conditional Lean
success. Neural parameter sharing breaks the independent-job analogy; allocated
practice can interfere with other procedures and need not produce progress.

The immediate hypothesis is that weak but feasible continuations acquire higher
held-out conditional correctness than a prevalence-driven allocation under the
same proposal and optimization budgets. Compare the same supplied contexts in
both arms. Training only one arm with hints would confound scheduling with
extra information. Ordinary unconditioned inference and transfer to held-out
compositions must improve before calling the result a broader capability gain.
Prefix-following is not itself evidence of semantic strategy adherence.

A practical first panel can use training-only C0 verified proofs, choose a short
incomplete structural start and retain the complete proof as a feasibility
witness. A fresh frozen-base continuation screen can identify partial execution
competence. Split by theorem before training and report conditional evaluation
separately from ordinary no-prefix evaluation. No held-out result may select the
training routes. A deterministic route label is an operational label until
Lean state or dependency checks establish its meaning.

The initial scaffold does not implement a new optimizer or prove a new paradigm.
It makes selection and conditional execution separately manipulable, allowing a
decisive experiment that the present output-blocking machinery cannot express.

## Second priority, conditional on the first result

Build a persistent frontier of verified partial proof states and move practice
back toward earlier states as continuations become reliable. The correspondence
to Bellman backup/backward mastery is a frontier of solvable continuations,
not a novelty reward on finished strings. The high-value test is whether
mastering prerequisites unlocks held-out compositions and improves learning
speed on new theorem families. Frozen-model resetting, equal-data supervised
practice, and prefix-only evaluation distinguish elicitation, imitation, and
new reusable execution. Do not start with a broad automated state search before
the smaller continuation-learning gate establishes a usable signal.

Defer prevalence-cap sweeps, another pass@128 campaign on the same panel,
additional C3 seeds, and full C5 restarts without a new discriminating question.

## Available data and implementation seams

Base model: `../models/base`, lineage revision
`e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`. C1/C3 exported models are
`../models/c1-final` and `../models/c3-final`. C2 training artifacts remain in
`../runs/c2-unlikeliness-2-full-20260909-seed42-bc282d6-h100-workers64`.

The four complete C0 training proof shards and their hashes are recorded in
`../runs/c0-base-20260804-seed42-complete/validation.json`; replace its historical
`/scratch/memoozd/rl/restriction/runs` root with the current bundle's `../runs`.
Use first 32 proposals per theorem, excluding documented padding. A descriptive
availability scan found 5,167 training theorems with a correct multiline proof
starting with `have`, `refine`, `rcases`, `constructor`, `apply`, `by_contra`,
`cases`, `induction`, or `by_cases`; 1,781 have at least two such first heads.
Correct-proof counts by first head were respectively 17,399; 10,762; 766;
4,736; 2,865; 222; 1,658; 1,443; 122. These are textual candidates, not a
validated count of distinct strategies or incomplete Lean states. The first
physical line sometimes opens a syntactic construct, so blindly truncating it
is insufficient for a verified-state archive.

`verl/lean/prompts.py::prompt_fn_deepseek` already accepts `history` and appends
it after the model's begin-of-sentence marker. The trainer currently omits it.
The new optional `proof_prefix` dataset field can enter at
`RayLeanTrainer._generate_and_verify_full_proofs`: the actor receives it as
prompt context; the verifier receives prefix plus generated suffix; only suffix
response tensors enter PPO. Each continuation has a distinct group identity.
Store exact prefix, suffix, conditioning hash, and prompt-token cost in proof
telemetry. Missing or empty prefixes retain the old execution path.

Two important limits:

1. `_format_model_input` historically left-truncates prompts. Continuation
   tasks must fail on overlength input so the proof start and theorem cannot
   silently change. Freeze the same prompt limit for matched arms.
2. The current verifier wrapper ignores `src_context` and uses fixed imports.
   Custom declarations must be part of `theorem_statement` or require a new,
   explicitly registered context-aware path. Preserve historical verifier
   behavior. Legacy theorem-level metrics also pool multiple route rows;
   conditional results require grouping by the recorded conditioning identity.

`../verifier/DeepSeek-Prover-V1.5/prover/lean/verifier.py` supports `tactics` and
`allTactics` metadata for later partial-state extraction without modifying
correctness acceptance. ProofNet has 185 validation and 186 test examples,
but its local port has known formalization/import caveats. It should not be
treated as ready merely because the file exists.

## Implemented scaffold and validation

The optional prefix path is now implemented in the trainer and
`verl/lean/proof_prefix.py`. It leaves generated response tensors unchanged,
reconstructs full proofs only for verification/logging, separates continuation
group identities, and rejects silent prefix-prompt truncation. Pilot rows log
`pilot_row_id`, `pilot_split`, and `pilot_padding`, including unconditioned root
rows. Sample-only padding is explicitly marked and counted; pilot training
refuses batches requiring duplicated tasks. Legacy paths retain their previous
padding behavior.

Bundle preflight passed. Seven tests execute the production trainer methods
with a simulated actor and verifier, covering suffix-only tensor attribution,
full-proof verification, context/provenance, absent/empty-prefix equivalence,
independent advantage normalization, prompt overflow, and pilot padding.
The five existing saturated-prompt admission tests also pass. These are CPU
logic checks, not a GPU training or Lean-prefix feasibility result. The full
project suite is left to the coordinated integration check after all changes.
