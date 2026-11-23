"""Construct nonempty disjoint equal-moment subsets inside a supplied 42-element complement."""
from itertools import combinations
import json
import random

LIMIT = 51*42


def key(values):
    return sum(values),sum(x*(LIMIT+1-x)//2 for x in values)


def recover(available):
    if len(set(available)) != 42 or not all(1<=x<=LIMIT for x in available):
        raise ValueError('Expected 42 distinct entries from the workbook interval')
    seen = {}
    tested = 0
    for size in range(1,43):
        for values in combinations(sorted(available),size):
            signature = key(values)
            tested += 1
            if signature in seen:
                old = set(seen[signature])
                left,right = sorted(old-set(values)),sorted(set(values)-old)
                assert left and right and set(left).isdisjoint(right)
                assert set(left+right)<=set(available)
                assert sum(left)==sum(right) and sum(x*x for x in left)==sum(x*x for x in right)
                return dict(left=left,right=right,subsets_examined=tested)
            seen[signature]=values
    raise AssertionError('Pigeonhole bound violated')


if __name__=='__main__':
    bound = (42*LIMIT+1)*(42*max(key([x])[1] for x in range(1,LIMIT+1))+1)
    assert bound < 2**42
    rng = random.Random(20261123)
    panels = {'first_42':list(range(1,43)), 'last_42':list(range(LIMIT-41,LIMIT+1)),
              'spaced':list(range(51,LIMIT+1,51)), 'seeded':sorted(rng.sample(range(1,LIMIT+1),42))}
    print(json.dumps(dict(subsets=2**42,key_bound=bound,panels={name:dict(available=b,**recover(b))
                     for name,b in panels.items()}),indent=2))
