import Lean

def revAcc : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, ys => revAcc xs (x::ys)

noncomputable def obj (xs : List Nat) : (
  revAcc (revAcc xs []) [] = xs
) := (
  by
    have h : ∀ (xs ys : List Nat), revAcc (revAcc xs ys) [] = revAcc ys xs := by
      intro xs
      induction xs with
      | nil =>
          intro ys
          rfl
      | cons a xs ih =>
          intro ys
          simp only [revAcc]
          exact ih (a :: ys)
    simpa [revAcc] using h xs []
)
#print axioms obj
