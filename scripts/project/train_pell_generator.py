"""Reuse matched Pell training with complete bounded-generator demonstrations."""
import argparse
from pathlib import Path
import train_pell_construction as engine

UNITS={2:(3,2),3:(2,1),5:(9,4),7:(8,3),11:(10,3),13:(649,180)}


def task(d,level):
    a,b=UNITS[d];assert a*a-d*b*b==1
    x,y=a,b
    for _ in range(level-1):
        lower=x;x,y=a*x+d*b*y,b*x+a*y
    upper=2*a*lower
    assert x*x-d*y*y==1 and lower<x<=upper
    statement=(f'-- A verified starting solution is ({a}, {b}).\n'
        f'theorem target : ∃ x y : ℤ, x^2 - {d}*y^2 = 1 ∧ {lower} < x ∧ x ≤ {upper} := by\n')
    literal=f'  use {x}, {y}\n  norm_num'
    program=(f'  let step (p : ℤ × ℤ) : ℤ × ℤ :=\n'
        f'    if {lower} < p.1 then p else ({a}*p.1+{d}*{b}*p.2, {b}*p.1+{a}*p.2)\n'
        f'  let q := Nat.rec (motive := fun _ => ℤ × ℤ) (({a}, {b}) : ℤ × ℤ) (fun _ p => step p) 8\n'
        '  use q.1, q.2\n  norm_num [q, step] <;> decide')
    return dict(id=f'generator-d{d}-level{level}-plain',statement=statement,answer=[x,y],
        literal=literal,expression=program,discriminant=d,level=level,lower=lower,upper=upper)


def panel():
    train=[task(d,n) for d in [2,3,5,7] for n in [2,3]]
    test=[task(d,n) for d in [11,13] for n in [2,4,6]]+[task(d,6) for d in [3,7]]
    return train,test


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['prepare','run','verify'])
    p.add_argument('bundle',type=Path);p.add_argument('out',type=Path)
    p.add_argument('--arm',choices=['base','literal','expression'])
    a=p.parse_args();engine.panel=panel
    if a.mode=='run':
        original=engine.runtime.sample
        def sample(model,tok,prompt,seed,max_tokens,traces):
            assert max_tokens==256
            return original(model,tok,prompt,seed,512,traces)
        engine.runtime.sample=sample
    {'prepare':engine.prepare,'run':engine.run,'verify':engine.verify}[a.mode](a)


if __name__=='__main__':main()
