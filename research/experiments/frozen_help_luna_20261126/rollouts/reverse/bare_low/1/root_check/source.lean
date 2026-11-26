import Lean

def revAcc : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, ys => revAcc xs (x::ys)

theorem root (xs : List Nat) : revAcc (revAcc xs []) [] = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
      change revAcc (revAcc xs [x]) [] = x :: xs
      -- Generalize the accumulator property, proved below by induction on the list.
      have h : ∀ ys, revAcc (revAcc xs ys) [] = revAcc xs ys := by
        intro ys
        induction xs generalizing ys with
        | nil => rfl
        | cons a as ih' =>
            change revAcc (revAcc as (a :: ys)) [] = revAcc as (a :: ys)
            exact ih' (a :: ys)
      simpa [revAcc] using h []
#print axioms root
