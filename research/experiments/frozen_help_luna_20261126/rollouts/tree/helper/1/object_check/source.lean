import Lean

inductive Tree where
  | leaf : Nat → Tree
  | fork : Tree → Tree → Tree

def flatten : Tree → List Nat
  | .leaf x => [x]
  | .fork l r => flatten l ++ flatten r

def mirror : Tree → Tree
  | .leaf x => .leaf x
  | .fork l r => .fork (mirror r) (mirror l)

def treeAcc : Tree → List Nat → List Nat
  | .leaf x, acc => x::acc
  | .fork l r, acc => treeAcc l (treeAcc r acc)

noncomputable def obj (t : Tree) : (
  ∀ t : Tree, treeAcc (mirror t) [] = (flatten t).reverse
) := (
  by
    intro t
    induction t with
    | leaf x => rfl
    | fork l r ihl ihr =>
        simp [mirror, treeAcc, flatten, List.reverse_append, ihl, ihr]
)
#print axioms obj
