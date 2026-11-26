import Lean

def revAcc : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, ys => revAcc xs (x::ys)

noncomputable def obj (xs : List Nat) : (
  ∀ xs : List Nat, revAcc (revAcc xs []) [] = xs
) := (
  by
    intro xs
    induction xs with
    | nil => rfl
    | cons x xs ih =>
        simp [revAcc, ih]
)
#print axioms obj
