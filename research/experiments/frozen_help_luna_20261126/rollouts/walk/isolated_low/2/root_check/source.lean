import Lean

def walk : Nat → Int → Int → Int × Int
  | 0, a, b => (a,b)
  | n+1, a, b => walk n (a+2) (b+1)

theorem root (n : Nat) (a b : Int) : (walk n a b).1 - 2 * (walk n a b).2 = a - 2*b ∧ b ≤ (walk n a b).2 := by
  induction n generalizing a b with
  | zero => simp [walk]
  | succ n ih =>
      simpa [walk, sub_eq_add_neg, add_assoc, add_comm, add_left_comm] using
        (ih (a + 2) (b + 1))
#print axioms root
