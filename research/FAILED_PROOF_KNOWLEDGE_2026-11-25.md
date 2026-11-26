# Recoverable mathematical work in failed proof attempts

User-designated new research direction, November 25. Distinguish original-target
localized repair (same theorem and nearly unchanged proof), changed-target
hindsight, valid subproofs in failures, and multi-attempt composition.

## Retrospective first screen (registered before calculation)

Hypothesis: some rejected proofs in ordinary existing benchmark rollouts have an
independently sampled accepted sibling differing by only one literal proof line.
The fraction of rejected attempts with such a sibling may change after RL.
This is a high-precision candidate discovery proxy for localized recoverability,
not a new Lean repair experiment or an estimate of every repairable failure.

Use the four finalized archived pass@128 banks C0/C1/C2/C3, first 128 proposals per
theorem as in the original evaluation, 467 theorem identities, 128 physical
padding rows excluded per bank. Require identical theorem statement and context
for a pair, original failure_class lean_rejected, accepted correct sibling in
the same bank, and literal splitlines(keepends=True) equality outside exactly one
deleted, inserted, or replaced nonblank line; replacement requires two nonblank
different lines. No whitespace normalization. Exclude identical contradictory
bodies and record them. Count attempts, distinct failed bodies, and affected
theorems; do not count pairs as independent observations. Report separately by
edit category. A single line can contain substantial mathematics: inspect
examples and do not treat all as scope-only or trivial. Sibling availability itself
depends on success rate and sampling diversity; this descriptive comparison
cannot attribute causality to training or measure repair probability absent a
fixed repair operator. No new model generations or Lean checks.

## Next decision

If concrete same-target pairs exist across conditions, freeze a general repair
operator on training-only examples and evaluate on disjoint held-out roots with
unchanged Lean and matched edit budgets. Do not tune on this benchmark screen.

## Initial internal result

All four official raw pass@128 logs were recovered from the November 18 GitHub
release's large-proof-records archive (SHA-256
46db2e0c1954b4a9095c43b294106bee55b29bba175beda1fd214a7d61aaa76b).
Each extracted log matches its tracked member hash. 239,104 registered proposals
were screened; counts agree with the historical correctness totals.

| Condition | Resolved Lean rejections | Matched failures | Rate | Distinct matched failed bodies | Theorems with match |
|---|---:|---:|---:|---:|---:|
| C0 pristine SFT | 33,594 | 1,144 | 3.41% | 1,114 | 219 |
| C1 GRPO | 29,745 | 786 | 2.64% | 590 | 159 |
| C2 unlikely reward | 31,424 | 671 | 2.14% | 655 | 195 |
| C3 hard exclusion | 30,951 | 807 | 2.61% | 756 | 197 |

All rates are fractions of resolved Lean rejections, not all generated attempts.
No identical contradictory bodies were found. Categories overlap, and some
proofs are short enough that one changed line represents most of the argument.
Consequently these are observed local-edit neighbors, not confirmed retained
mathematical strategy counts. Examples and both proposal IDs are preserved in
[screen output](experiments/failed_proof_corpus_20261125/sibling-screen.json).
C0 has the highest observed match rate. C1 has a marked reduction in affected
roots and distinct failed bodies; C3 and C2 recover more affected roots than C1,
but not the base. This is not a causal training or fixed-repair comparison.

Earlier evidence:
- [Scope repair](CAUSAL_STATE_REPAIR_RESULT_2026-11-19.md): 43 original-target
  repairs out of 64 invariant attempts; all 172 omission controls rejected;
  four variants of one schema, not four independent families.
- [Repaired prerequisite library](REPAIRED_LIBRARY_RESULT_2026-11-19.md):
  27 new dependent nonzero proofs, all 54 removal/irrelevance controls reject.
  This is reuse of repaired knowledge, not an additional direct repair count.
- [Verified hindsight](experiments/hindsight_contracts_20261124/README.md):
  46 failed C1 outputs accepted unchanged under a different sign contract.
  Different target, not direct repair; do not pool with scope repair rates.
- [Failed joins](FAILED_EXPERIENCE_JOIN_2026-11-24.md): frozen protocol,
  no recorded result yet.

## Related work (initial targeted search)

- [Baldur, First et al., 2023](https://arxiv.org/abs/2303.04910): Isabelle
  whole-proof repair with prior failed proof and diagnostic, trained with
  human correct proofs as targets. Shows useful repair context, not
  necessarily byte-preservation or causal scope interventions.
- [APOLLO, Ospanov et al., 2025](https://arxiv.org/abs/2505.05758):
  exceptionally close direct precedent for retaining valid proof structure
  and isolating bad sublemmas, using syntax repair, automation and LLM
  completion. Its agentic pipeline is not our desired raw single-model dataset.
- [APRIL, Wang et al., 2026](https://arxiv.org/abs/2602.02990): 260,000
  systematically generated faulty proof/diagnostic/repair tuples. Important
  repair-training baseline; induced failures are not ordinary model rollout
  failures, so use separately.
- [Repair, Retry, and the Cost of Hindsight, Li and Li, 2026](https://arxiv.org/abs/2610.22698):
  controlled DeepSeek-Prover-V2-7B and Qwen3.6-27B study finds predecessor
  exposure can hurt and no clear gain over instruction-only resampling at
  matched budget. Distinguish an objectively repairable trajectory from a
  model's ability to self-repair. Exclude 27B from the initial corpus.
- [BlueprintRepair](https://arxiv.org/abs/2607.28110): typed local edits to
  failed proof graphs; related, but a different representation.

General proof repair is established prior art; the promising open question
is the incidence and taxonomy of objectively localized recoverability in
natural failed attempts, changes across training interventions, and whether
credit based on the recoverable work improves unassisted learning. This search
does not establish novelty of any broad claim.

## Downloaded external data

Six revision-pinned Hugging Face datasets are local under
artifacts/failed-proof-corpora; [inventory](experiments/failed_proof_corpus_20261125/external-inventory.json)
records source URLs, sizes, SHA-256, and declared license. Missing license is
not treated as permission to redistribute. Raw datasets are excluded from Git.

| Dataset | Rows | Publisher verdicts / provenance |
|---|---:|---|
| [DeepSeek V1.5-RL sampling](https://huggingface.co/datasets/autores/DSP1.5RL-minif2f-sampling_4) | 1,952 | 1,025 failures; full statements, proof code, structured verifier result; 4 samples per 488 roots |
| [DeepSeek V2-7B traces](https://huggingface.co/datasets/kobyjl/mini_f2f_traces) | 3,940 | 2,404 invalid, 1,536 valid; explicit 7B model, prompts, trace and grade; curated/adaptive sampling |
| [Kimina 1.5B](https://huggingface.co/datasets/Slim205/math_res_Kimina-Prover-Preview-Distill-1.5B_32_100) | 3,200 | 3,192 zero labels, 8 ones; raw model output and prompt, 100 distinct prompts |
| [DeepSeek V1.5-SFT](https://huggingface.co/datasets/Slim205/math_res_DeepSeek-Prover-V1.5-SFT_32_100) | 1,600 | 1,567 zero labels, 33 ones; 50 distinct prompts, not 100 as filename implies |
| [Kimina raw outputs](https://huggingface.co/datasets/ahyxie/kimina-minif2f-outputs) | 3,968 | 31 roots x128; no verdict or explicit model revision/size in rows |
| [Goedel raw outputs](https://huggingface.co/datasets/ahyxie/goedel-minif2f-outputs) | 3,968 | same 31 roots x128; no verdict or explicit revision/size in rows |

Total 18,628 raw rows; 8,188 reported negative/zero labels among the four
labeled datasets. No cross-corpus deduplication or fresh Lean verification.
First prioritize autores and kobyjl; Slim205 is useful for a small-model domain
contrast after verifying environment and prompt provenance. The ahyxie banks
are provisional until model identity, exact theorem statements, and verification
are recovered. Do not assume a zero label means a resolved Lean rejection.
The raw output files and local internal archive use about 818 MB together.

Additional leads not downloaded: [LyonWang00/formal-theorem-prover](https://github.com/LyonWang00/formal-theorem-prover)
has historical 7B SFT/GRPO eval summaries but no full attempt banks in the
inspected tracked tree; its SFT and RL timeouts differ.
[NuminaMath LEAN proof artifacts](https://huggingface.co/datasets/iiis-lean/NuminaMath-LEAN-Proof-Artifacts)
has large proof-tree archives; postpone until model provenance and no-agent
selection are clear. [Goedel Lean-workbook-proofs](https://huggingface.co/datasets/Goedel-LM/Lean-workbook-proofs)
exposes proof-only data, not the complete failed-attempt pool.
