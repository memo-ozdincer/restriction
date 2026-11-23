import Mathlib
open BigOperators Finset
set_option maxRecDepth 8192
set_option maxHeartbeats 2000000

theorem workbook_collision (B : Finset ℕ) (hB : B.card = 42)
    (hI : B ⊆ Icc 1 2142) :
    ∃ X Y : Finset ℕ, X ⊆ B ∧ Y ⊆ B ∧ X.Nonempty ∧ Y.Nonempty ∧ Disjoint X Y ∧
      (∑ x in X, x) = ∑ y in Y, y ∧ (∑ x in X, x^2) = ∑ y in Y, y^2 := by
  classical
  let w := fun x : ℕ => x*(2142-x)
  let key := fun U : Finset ℕ => (∑ x in U, x, ∑ x in U, w x)
  let box : Finset (ℕ × ℕ) := range (42*2142+1) ×ˢ range (42*1147041+1)
  have size : box.card < B.powerset.card := by
    simp only [box, card_product, card_range, card_powerset, hB]
    norm_num
  have fits (U) (hu : U ∈ B.powerset) : key U ∈ box := by
    have sub := mem_powerset.mp hu
    have hc : U.card ≤ 42 := hB ▸ card_le_card sub
    have b1 (x) (hx : x ∈ U) : x ≤ 2142 := (mem_Icc.mp (hI (sub hx))).2
    have b2 (x) (hx : x ∈ U) : w x ≤ 1147041 := by
      change x * (2142-x) ≤ 1147041
      zify [b1 x hx]
      nlinarith [sq_nonneg ((x:ℤ)-1071)]
    rw [show box = range (42*2142+1) ×ˢ range (42*1147041+1) from rfl, Finset.mem_product]
    dsimp only [key]
    constructor
    · apply mem_range.mpr
      have hh := sum_le_sum b1
      simp at hh
      omega
    · apply mem_range.mpr
      have hh := sum_le_sum b2
      simp at hh
      omega
  clear_value box
  obtain ⟨U,hU,V,hV,hne,heq⟩ := exists_ne_map_eq_of_card_lt_of_maps_to (s := B.powerset) (t := box) (f := key) size fits
  have he1 := congrArg Prod.fst heq
  have he2 := congrArg Prod.snd heq
  change (∑ x in U, x) = ∑ x in V, x at he1
  change (∑ x in U, w x) = ∑ x in V, w x at he2
  have idsum (T : Finset ℕ) (hs : T ⊆ B) :
      (∑ x in T, w x) + (∑ x in T, x^2) = (∑ x in T, x)*2142 := by
    rw [← sum_add_distrib, sum_mul]
    apply sum_congr rfl
    intro x hx
    have hh := Nat.sub_add_cancel (mem_Icc.mp (hI (hs hx))).2
    dsimp [w]
    nlinarith
  have su := mem_powerset.mp hU
  have sv := mem_powerset.mp hV
  have hsq : (∑ x in U, x^2) = ∑ x in V, x^2 := by
    have h := idsum U su
    rw [he1,he2] at h
    exact Nat.add_left_cancel (h.trans (idsum V sv).symm)
  have diff (f : ℕ → ℕ) (e : U.sum f = V.sum f) : (U \ V).sum f = (V \ U).sum f := by
    have a := sum_union (disjoint_sdiff_inter U V) (f := f)
    have b := sum_union (disjoint_sdiff_inter V U) (f := f)
    rw [sdiff_union_inter] at a b
    rw [inter_comm V U] at b
    exact Nat.add_right_cancel (a.symm.trans (e.trans b))
  have eq1 := diff id he1
  have eq2 := diff (fun x => x^2) hsq
  have both : (U \ V).Nonempty ∧ (V \ U).Nonempty := by
    have aux (T : Finset ℕ) (ht : T ⊆ B) : T.sum id = 0 ↔ T = ∅ := by
      constructor
      · intro h
        apply eq_empty_iff_forall_not_mem.mpr
        intro x hx
        have hh := single_le_sum (f := id) (fun i _ => Nat.zero_le i) hx
        have hp := (mem_Icc.mp (hI (ht hx))).1
        change x ≤ T.sum id at hh
        rw [h] at hh
        omega
      · rintro rfl; simp
    have zero : U \ V = ∅ ↔ V \ U = ∅ := by
      rw [← aux _ (Subset.trans sdiff_subset su), ← aux _ (Subset.trans sdiff_subset sv), eq1]
    by_contra h
    simp only [nonempty_iff_ne_empty, not_and_or, not_not] at h
    have uv : U \ V = ∅ := h.elim (fun x => x) zero.mpr
    have vu := zero.mp uv
    exact hne (Subset.antisymm (sdiff_eq_empty_iff_subset.mp uv) (sdiff_eq_empty_iff_subset.mp vu))
  exact ⟨_, _, Subset.trans sdiff_subset su, Subset.trans sdiff_subset sv,
    both.1, both.2, disjoint_left.mpr (fun x hx hy => (mem_sdiff.mp hx).2 (mem_sdiff.mp hy).1), eq1, eq2⟩

#print axioms workbook_collision

theorem nonempty_workbook_witnesses (A : Finset ℕ) (hA : A ⊆ Icc 1 (51*42))
    (ha : A.card = 50*42) :
    ∃ X Y : Finset ℕ, X ⊆ Icc 1 (51*42) ∧ Y ⊆ Icc 1 (51*42) ∧
      X.Nonempty ∧ Y.Nonempty ∧ Disjoint X Y ∧ Disjoint X A ∧ Disjoint Y A ∧
      (∑ x in X, x) = ∑ y in Y, y ∧ (∑ x in X, x^2) = ∑ y in Y, y^2 := by
  let B := Icc 1 (51*42) \ A
  have hc : B.card = 42 := by
    rw [show B = Icc 1 (51*42) \ A from rfl, card_sdiff hA, ha, Nat.card_Icc]
  obtain ⟨X,Y,hx,hy,nx,ny,disj,s1,s2⟩ := workbook_collision B hc sdiff_subset
  exact ⟨X,Y,Subset.trans hx sdiff_subset,Subset.trans hy sdiff_subset,nx,ny,disj,
    disjoint_left.mpr (fun z hz => (mem_sdiff.mp (hx hz)).2),
    disjoint_left.mpr (fun z hz => (mem_sdiff.mp (hy hz)).2),s1,s2⟩

#print axioms nonempty_workbook_witnesses
