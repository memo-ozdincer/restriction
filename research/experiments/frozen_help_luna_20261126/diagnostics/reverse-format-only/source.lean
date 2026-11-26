import Lean

def revAcc : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, ys => revAcc xs (x::ys)

noncomputable def obj (xs : List Nat) : (
  ∀ as bs : List Nat, revAcc as bs = as.reverse ++ bs
) := (
  by
    intro as
    induction as with
    | nil =>
        intro bs
        rfl
    | cons x xs ih =>
        intro bs
        rw [revAcc, ih, List.reverse_cons]
        simp [List.append_assoc]
)
#print axioms obj
