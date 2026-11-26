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

theorem root (t : Tree) : treeAcc (mirror t) [] = (flatten t).reverse := by
  induction t with
  | leaf x => rfl
  | fork l r ihl ihr =>
    simp [mirror, treeAcc, flatten, ihl, ihr, List.reverse_append]
#print axioms root
