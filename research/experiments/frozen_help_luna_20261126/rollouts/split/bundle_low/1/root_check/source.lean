import Lean

def splitPairs : List Nat → List Nat × List Nat
  | [] => ([], [])
  | [x] => ([x], [])
  | x::y::xs => (x::(splitPairs xs).1, y::(splitPairs xs).2)
def weave : List Nat → List Nat → List Nat
  | [], ys => ys
  | x::xs, [] => x::xs
  | x::xs, y::ys => x::y::weave xs ys

theorem root (xs : List Nat) : weave (splitPairs xs).1 (splitPairs xs).2 = xs := by
  induction xs using List.rec with
  | nil => rfl
  | @cons x xs ih =>
    cases xs with
    | nil => rfl
    | cons y ys =>
      simp [splitPairs, weave, ih]
#print axioms root
