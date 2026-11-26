import Lean

def revAcc : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, ys => revAcc xs (x::ys)

theorem root (xs : List Nat) : revAcc (revAcc xs []) [] = xs := by
  have help0 : (
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
  rw [help0, help0]
   simp
#print axioms root
