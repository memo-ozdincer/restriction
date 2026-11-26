import Lean

def revAcc : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, ys => revAcc xs (x::ys)

theorem root (xs : List Nat) : revAcc (revAcc xs []) [] = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
      simp [revAcc, ih]
#print axioms root
