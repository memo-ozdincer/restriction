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
  have h : ∀ (t : Tree) (acc : List Nat), treeAcc t acc = flatten t ++ acc := by
    intro t
    induction t with
    | leaf x => intro acc; rfl
    | fork l r ihl ihr =>
      intro acc
      simp [treeAcc, ihl, ihr, flatten, List.append_assoc]
  have h2 : ∀ t, flatten (mirror t) = (flatten t).reverse := by
    intro t
    induction t with
    | leaf x => rfl
    | fork l r ihl ihr =>
      simp [mirror, flatten, ihl, ihr, List.reverse_append]
  simp [h, h2]
#print axioms root
