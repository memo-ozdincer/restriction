# C2 versus C3: what actually changes in the proofs?

September 12, 2026. Exploratory inspection of the finalized seed-42 pass@128
panel; no new sampling, training, verifier changes, or retries.

## Bottom line

C2 has broader syntactic coverage; C3's sampled correct distribution overlaps
more with the base model. The inspected C3-only recoveries do not establish
preservation of more intricate mathematics: the strongest base-frequency
examples include redundant arithmetic steps on already-easy problems.
The data do not justify marketing C3 as either better diversity or superior
capability retention. C5 reward rejection remains a separate uncompleted test.

## Distribution-level characterization

For each theorem, select the first 128 proposals in its finalized proof log.
Keep correct proposals, retaining multiplicity. A proposal overlaps base if
its theorem-specific signature or normalized exact-proof ID appears in C0's
128-proposal sample. Divide overlapping correct proposals by all correct
proposals in that condition. These are pooled proposal-weighted fractions,
not equal-theorem averages or a measure of distance to the entire base policy.

| Correct-proposal statistic | C1 GRPO | C2 unlikely | C3 blocking |
|---|---:|---:|---:|
| Observed base tactic-pattern overlap | 76.34% | 65.42% | 71.40% |
| Observed base exact-proof overlap | 14.36% | 5.87% | 9.28% |
| Mean generated tokens | 60.41 | 58.53 | 60.48 |
| Mean parsed tactic heads | 3.367 | 3.371 | 3.401 |

On the 276 theorems solved by both C2 and C3, the shortest sampled correct
proof is shorter in tokens for C2 on 132, C3 on 84, and tied on 60.
This compares an equal proposal budget, not an equal number of correct
proofs, and does not establish elegance or runtime efficiency.

C3 is descriptively closer to observed base support than C2, but C1 is closer
still. Therefore base similarity alone cannot be the benefit: it also occurs
in the method whose collapse motivated this project. Different sampling
success rates and theorem difficulty affect these pooled fractions.

September 20 follow-up: [equal-theorem weighting](BASE_OVERLAP_WEIGHTING.md)
on 275 common solved theorems preserves the ordering C1 > C3 > C2, for both
tactic and exact-proof overlap and separately on validation and test. C3's
tactic-overlap gap over C2 is 5.61 percentage points. Unequal correct-sample
weighting is not the sole explanation, but base overlap remains no demonstrated
benefit: ordinary GRPO scores higher still.

## Exclusive solves: both are singleton observations

All four conditions receive 128 attempts per theorem. C2 and C3 solve 277
each, with 276 common. Neither exclusive solve appears in C0 or C1's samples.
They are not examples of observed base-capability recovery.

### C2: `numbertheory_aoddbdiv4asqpbsqmod8eq1`

One correct proof, 158 generated tokens. It substitutes the multiple-of-four
witness, normalizes the expression, proves the odd number has remainder
1, 3, 5, or 7 modulo 8 using `omega`, then splits those cases and simplifies.
This is a recognizable elementary number-theoretic argument, expressed with
residue enumeration. It is not evidence for a C3-specific capability.

```lean
  cases' h₁ with k h₁
  rw [h₁] at *
  simp_all only [Int.ofNat_mul, Int.ofNat_succ]
  ring_nf
  have h₂ : a % 8 = 1 ∨ a % 8 = 3 ∨ a % 8 = 5 ∨ a % 8 = 7 := by
    cases' h₀ with k h₀
    omega
  rcases h₂ with (h₂ | h₂ | h₂ | h₂) <;> simp [h₂, pow_two, Int.mul_emod, Int.add_emod]
```

### C3: `aime_1983_p1`

One correct proof, 130 generated tokens. It establishes positivity of three
logarithms, clears denominators with logarithm identities, and closes by
linear arithmetic. This is compact and mathematically recognizable, but one
success versus zero cannot establish reliable specialization or superiority.

```lean
  rcases ht with ⟨hx, hy, hz⟩
  have log_pos : 0 < Real.log x := Real.log_pos (by norm_num [hx])
  have log_pos' : 0 < Real.log y := Real.log_pos (by norm_num [hy])
  have log_pos'' : 0 < Real.log z := Real.log_pos (by norm_num [hz])
  field_simp [*, log_mul, mul_assoc] at *
  linarith
```

## Repeated-base recoveries: deterministic inspection sample

To avoid choosing impressive-looking examples, take the top two theorem-mode
pairs per direction from the symmetric recovery artifact, requiring C0 count
>=4 and absence in C1 and the opposing exploration condition. Sort by descending
C0 count, descending recovering-condition count, then theorem name. Inspect
the shortest proof in each selected mode, plus each condition's shortest
correct proof for that theorem. This is a small purposive audit, not a random
sample or a semantic classification of the whole dataset.

| Recovered only by | Theorem | C0 / recovery count | What the recovered pattern adds |
|---|---|---:|---|
| C2 | `imo_1961_p1` | 11 / 2 | Three separate positive-square facts before `nlinarith` |
| C2 | `mathd_numbertheory_403` | 10 / 5 | A `simp only` step before `decide` |
| C3 | `mathd_numbertheory_85` | 10 / 1 | A `simp only` step before `norm_num` |
| C3 | `mathd_numbertheory_30` | 6 / 2 | Five explicit numeric remainder facts before `simp` |

For `imo_1961_p1`, C1/C3 already have a 94-token proof using positive/nonnegative
squares and `nlinarith`; the recovered C2-mode representative is 113 tokens.
The mathematics is not shown to be newly recovered.

For `mathd_numbertheory_403`, C1/C2/C3 all already have a five-token `decide`
proof. Recovering `simp; decide` is not a recovered ability to solve it.

For `mathd_numbertheory_85`, C1/C2/C3 have six-token `simp` proofs; C2 also
has a five-token `decide`. C3's recovered-mode example has 31 tokens.

For `mathd_numbertheory_30`, C3's recovered example has 148 tokens, explicitly
computing five consecutive remainders. Its own shortest correct proof has
18 tokens; C2 has a nine-token `exact (by decide)` proof. The longer derivation
might expose intermediate arithmetic, but is not evidence of superior
efficiency, elegance, or indispensable retained capability.

## Application implications

1. **Generic diversity:** the matched completed comparison favors C2.
2. **Preserving intricate base abilities:** not established; measured recovery
   can mean redundant syntax on an already-solved theorem. C3's closer base
   overlap is a distributional observation, not a downstream benefit.
3. **Persistent avoidance of a specified route:** the clearest mechanism
   distinction. C2 continually re-ranks likelihood, whereas the archive keeps
   identifying the same route after its probability falls. C5 could assign
   that route zero reward even when Lean verifies it. This only motivates an
   application where that route genuinely violates a known target constraint;
   our frozen tactic archive does not currently encode such a constraint.
4. **Cross-domain retention:** ProofNet validation remains a hypothesis test,
   not an established use case. It must compare C2 too, and must distinguish
   target-domain performance from finite-sample proof-pattern recovery.

If an explicit target-quality score is available, directly rewarding it is
a necessary baseline. Blocking has no demonstrated special advantage merely
because a desired proof is unlikely. The completed C3 evidence makes a generic
superiority claim less plausible, not more.

## Evidence and boundaries

### C5 restart readiness audit

The September 2 pause (D-112) explicitly requires a new user request before
restarting C5. No such restart was submitted in this audit. The preserved
retry-7 runner uses commit `a0f1235a97ba4e92b25c53c959c7a942e63ee82c`,
`reject_reward`, pristine base initialization, and 32 Lean workers. C2 used
commit `bc282d66c415f3857939449b045d55fd302f6414` and 64 Lean workers.
The launchers agree on seed 42, learning rate 1e-6, KL 0.10, two PPO epochs,
32 proposals per training theorem, and the 512-token response limit. A git
comparison of `ray_lean_trainer.py`, `proof_modes.py`, and `hard_blocking.py`
between those commits has no differences. This is a targeted check, not a
full dependency/environment equivalence audit.

The preserved dependent analysis compares C5 with C3 on training data only;
it does not automatically provide the requested C5-versus-C2 held-out result.
An authorized restart therefore needs a fresh, explicit C5/C2 comparison chain,
matched held-out inputs, and documented treatment of the 32-versus-64 worker
operational difference. Do not silently reuse the old analysis and call the
full comparison complete. Future submissions prefer `def-zhijing`.

Source proof-log paths and SHA-256 hashes are in
`results/symmetric_recovery_c0_c1_c2_c3_seed42_pass128.json` under `sources`.
The registered comparison is
`results/c2_unlikeliness_vs_c3_seed42_pass128.json`. Both files were validated
against finalized metrics, matched theorem panels, and 128-attempt accounting.
Proof snippets above are copied from correct logged generations, with only
the trailing Markdown fence removed; no fresh Lean verification was performed.
Token counts are recorded generation counts, not a retokenization of cleaned
snippets. Parser heads can include multiline lemma arguments and miss nested
tactics. Semantic interpretation here is a manual reading, not a new metric.
