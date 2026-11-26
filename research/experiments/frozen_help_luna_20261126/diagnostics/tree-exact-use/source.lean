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
  have help0 : (
    treeAcc (mirror t) [] = (flatten t).reverse
  ) := (
    by
      have h : ∀ t acc, treeAcc (mirror t) acc = (flatten t).reverse ++ acc := by
        intro t
        induction t with
        | leaf x =>
            intro acc
            simp [treeAcc, mirror, flatten]
        | fork l r ihl ihr =>
            intro acc
            simp only [mirror, treeAcc, ihl, ihr, flatten]
            simp [List.reverse_append, List.append_assoc]
      simpa using h t []
  )
  exact help0
#print axioms root
