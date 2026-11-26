"""Offline task selection and exact shortest-path DAG; never used for updates."""
import json, random, sys, time
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reversible_initial"))
from environment import gate_library, gate_permutation, execute, verify

N=4
GATES=gate_library(N)
TRANS=[bytes(gate_permutation(N,g))+bytes(range(16,256)) for g in GATES]
ROOT=bytes(range(16))
HORIZON=10


def bfs(root, depth):
    distance={root:0}
    layer=[root]
    for k in range(depth):
        new=[]
        for state in layer:
            for gate in TRANS:
                nxt=state.translate(gate)
                if nxt not in distance:
                    distance[nxt]=k+1
                    new.append(nxt)
        layer=new
    return distance, layer


def main():
    t=time.monotonic()
    root_depth, root_last=bfs(ROOT,5)
    rng=random.Random(20261128)
    for candidate in range(50):
        actions=[rng.randrange(len(GATES)) for _ in range(HORIZON)]
        target=bytes(execute(N,[GATES[a] for a in actions]))
        goal_depth, goal_last=bfs(target,4)
        intersect=[root_depth[s]+d for s,d in goal_depth.items() if s in root_depth]
        if not intersect:
            break
    else:
        raise RuntimeError("no certified candidate")
    assert verify(N,target,[GATES[a] for a in actions],HORIZON)['reward']
    # An edge from layer 5 of root to layer 4 of goal closes a length-ten path.
    edges=defaultdict(set)
    first=set()
    last=set()
    for tail in goal_last:
        for a,gate in enumerate(TRANS):
            tip=tail.translate(gate)
            if root_depth.get(tip) == 5:
                edges[tip].add((a,tail))
                first.add(tip)
                last.add(tail)
    assert first
    # Each generator is an involution. Trace only shortest legal links.
    frontier=first
    for d in range(5,0,-1):
        prev=set()
        for tip in frontier:
            for a,gate in enumerate(TRANS):
                state=tip.translate(gate)
                if root_depth.get(state)==d-1:
                    edges[state].add((a,tip))
                    prev.add(state)
        frontier=prev
    assert frontier=={ROOT}
    frontier=last
    for d in range(4,0,-1):
        nxt=set()
        for state in frontier:
            for a,gate in enumerate(TRANS):
                tip=state.translate(gate)
                if goal_depth.get(tip)==d-1:
                    edges[state].add((a,tip))
                    nxt.add(tip)
        frontier=nxt
    assert frontier=={target}
    # Stable layer order and exact sequence counts.
    paths={ROOT:1}
    layers=[]
    for d in range(HORIZON):
        layer=[]
        following=defaultdict(int)
        for state,count in sorted(paths.items()):
            links=sorted(edges[state])
            layer.append(dict(state=list(state),links=[[a,list(nxt)] for a,nxt in links]))
            for a,nxt in links:
                following[nxt]+=count
        layers.append(layer)
        paths=following
    assert list(paths)==[target]
    uniform=paths[target]/len(GATES)**HORIZON
    payload=dict(target=list(target),width=16,horizon=HORIZON,
                 candidate_index=candidate,seed=20261128,root_bfs5=len(root_depth),
                 target_bfs4=len(goal_depth),verified_shortest_count=paths[target],
                 uniform_root_probability=uniform,setup_seconds=time.monotonic()-t)
    (HERE/"task.json").write_text(json.dumps(payload,indent=2))
    (HERE/"dag.json").write_text(json.dumps(layers,separators=(",",":")))
    print(payload)
    print("DAG layer counts",[len(l) for l in layers])

if __name__=='__main__':main()
