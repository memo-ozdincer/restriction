import Lean

def revAcc : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, ys => revAcc xs (x::ys)

theorem root (xs : List Nat) : revAcc (revAcc xs []) [] = xs := by
  have h : ∀ (xs ys : List Nat), revAcc xs ys = xs.reverse ++ ys := by
    intro xs
    induction xs with
    | nil => intro ys; rfl
    | cons x xs ih =>
      intro ys
      simp [revAcc, ih, List.reverse_cons, List.append_assoc]
  simp [h]
#print axioms root
