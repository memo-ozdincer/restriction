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
  treeAcc (mirror t) [] = (flatten t).reverse
) := (
  by
    have h : ∀ (u : Tree) (acc : List Nat), treeAcc (mirror u) acc = (flatten u).reverse ++ acc := by
      intro u acc
      induction u with
      | leaf x => simp [treeAcc, mirror, flatten]
      | fork l r ihl ihr =>
          simp [treeAcc, mirror, flatten, ihl, ihr, List.reverse_append, List.append_assoc]
    exact h t []
)
#print axioms obj
