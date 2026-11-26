"""Enumerate every one-step reset and exact short terminal path counts."""
from functools import lru_cache
import json
from pathlib import Path
from environment import apply,moves,cost
ROOT=Path(__file__).parent

def main():
    task=json.loads((ROOT/'instance.json').read_text())
    root=tuple(task['plateau']); matrix=task['matrix']; limit=task['threshold']
    operators=moves(len(root))
    @lru_cache(maxsize=None)
    def length(tour):return cost(matrix,tour)
    @lru_cache(maxsize=None)
    def count(tour,depth):
        if not depth:return int(length(tour)<=limit)
        return sum(count(apply(tour,m),depth-1) for m in operators)
    records=[]
    for move in operators:
        tour=apply(root,move)
        records.append({'move':move,'cost':length(tour),'successful_sequences_by_length':[count(tour,d) for d in range(1,4)]})
    (ROOT/'neighborhood_audit.json').write_text(json.dumps(records,indent=2))
    print('mean kick three-step success count',sum(r['successful_sequences_by_length'][2] for r in records)/len(records),'max',max(r['successful_sequences_by_length'][2] for r in records))
if __name__=='__main__':main()
