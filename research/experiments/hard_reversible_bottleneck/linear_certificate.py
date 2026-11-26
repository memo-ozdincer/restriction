"""Offline exact depth-9 selection for a CNOT-only matrix problem."""
import json,random,time
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent
N=5
ACTIONS=[(i,j) for i in range(N) for j in range(N) if i!=j]
ROOT=tuple(1<<i for i in range(N))
HORIZON=9


def move(s,action):
    i,j=ACTIONS[action]
    return tuple(s[k]^s[j] if k==i else s[k] for k in range(N))


def bfs(s,m):
    d={s:0};layer=[s]
    for k in range(m):
        new=[]
        for x in layer:
            for a in range(len(ACTIONS)):
                y=move(x,a)
                if y not in d:d[y]=k+1;new.append(y)
        layer=new
    return d,layer


def main():
    root_depth,_=bfs(ROOT,4)
    rng=random.Random(20261128)
    for candidate in range(100):
        actions=[rng.randrange(len(ACTIONS)) for _ in range(HORIZON)]
        target=ROOT
        for a in actions:target=move(target,a)
        goal_depth,goal_last=bfs(target,4)
        if all(s not in root_depth for s in goal_depth):break
    else:raise RuntimeError("no exact candidate")
    edges=defaultdict(set);first=set();last=set()
    for tail in goal_last:
        for a in range(len(ACTIONS)):
            tip=move(tail,a)
            if root_depth.get(tip)==4:
                edges[tip].add((a,tail));first.add(tip);last.add(tail)
    assert first
    for d in range(4,0,-1):
        prev=set()
        for tip in first:
            for a in range(len(ACTIONS)):
                s=move(tip,a)
                if root_depth.get(s)==d-1:edges[s].add((a,tip));prev.add(s)
        first=prev
    assert first=={ROOT}
    for d in range(4,0,-1):
        nxt=set()
        for s in last:
            for a in range(len(ACTIONS)):
                tip=move(s,a)
                if goal_depth.get(tip)==d-1:edges[s].add((a,tip));nxt.add(tip)
        last=nxt
    assert last=={target}
    layers=[];counts={ROOT:1}
    for d in range(HORIZON):
        following=defaultdict(int);layer=[]
        for s,count in sorted(counts.items()):
            links=sorted(edges[s])
            layer.append(dict(state=s,links=links))
            for a,dst in links:following[dst]+=count
        layers.append(layer);counts=following
    assert list(counts)==[target]
    result=dict(target=target,horizon=HORIZON,candidate=candidate,root_depth4=len(root_depth),goal_depth4=len(goal_depth),
                path_count=counts[target],uniform_root_probability=counts[target]/len(ACTIONS)**HORIZON)
    (HERE/"linear_task.json").write_text(json.dumps(result,indent=2))
    (HERE/"linear_dag.json").write_text(json.dumps(layers,separators=(',',':')))
    print(result,[len(l) for l in layers])
if __name__=='__main__':main()
