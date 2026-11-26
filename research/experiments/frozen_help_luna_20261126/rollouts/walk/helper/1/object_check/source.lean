import Lean

def walk : Nat → Int → Int → Int × Int
  | 0, a, b => (a,b)
  | n+1, a, b => walk n (a+2) (b+1)

noncomputable def obj (n : Nat) (a b : Int) : (
  (walk n a b).1 - 2 * (walk n a b).2 = a - 2 * b ∧ b ≤ (walk n a b).2
) := (
  by
    induction n with
    | zero => simp [walk]
    | succ n ih =>
        simpa only [walk] using ih (a := a + 2) (b := b + 1)
)
#print axioms obj
