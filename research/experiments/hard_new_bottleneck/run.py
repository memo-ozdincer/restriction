"""Native 8-puzzle reset experiment with sampled Bellman backups."""
from pathlib import Path
import sys
import json
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sliding_initial"))
from environment import GOAL, MOVES, distances, neighbors, verify

HORIZON = 29
BATCH = 256
STEPS = 1000
EPSILON = .2
INF = HORIZON + 1
ROOT = (2,0,7,5,1,4,3,6,8)
MODES = ("root", "goal", "goal-switch", "uniform", "uniform-switch",
         "rootwalk", "rootwalk-switch")
SEEDS = range(42,46)


def make_env():
    depth = distances()
    assert depth[ROOT] == HORIZON and len(depth) == 181440
    states = list(depth)
    index = {s:i for i,s in enumerate(states)}
    trans = np.full((len(states),4), -1, dtype=np.int32)
    actions = list(MOVES)
    for i,s in enumerate(states):
        for a,t in neighbors(s):
            trans[i,actions.index(a)] = index[t]
    # Each row has a list of legal actions, padded for uniform choice via masks.
    legal = trans >= 0
    return states, trans, legal, index[ROOT], index[GOAL], np.array([depth[s] for s in states])


def uniform_actions(legal, rng):
    return np.where(legal, rng.random(legal.shape), -1).argmax(axis=1)


def reset(mode, rng, env):
    states, trans, legal, root, goal, depth = env
    if mode=="root":
        return np.full(BATCH,root,dtype=np.int32), 0
    if mode=="uniform":
        # index 0 is the goal from BFS enumeration.
        assert goal == 0
        return rng.integers(1,len(states),size=BATCH,dtype=np.int32), 0
    center = goal if mode=="goal" else root
    radii = rng.integers(1,HORIZON+1 if mode=="goal" else 5,size=BATCH)
    s=np.full(BATCH,center,dtype=np.int32)
    count=0
    for i in range(int(radii.max())):
        active=i<radii
        a=uniform_actions(legal[s],rng)
        s=np.where(active,trans[s,a],s)
        count+=int(active.sum())
    while np.any(s==goal):
        invalid = s==goal
        a=uniform_actions(legal[s[invalid]],rng)
        s[invalid]=trans[s[invalid],a]
        count+=int(invalid.sum())
    return s,count


def rollout(env,q,value,s,rng,learn=False,epsilon=0,audit_all=False):
    states,trans,legal,root,goal,depth=env
    starts=s.copy()
    alive=s!=goal
    hist=[]
    actions_taken=0
    for h in range(HORIZON,0,-1):
        available=legal[s]
        costs=q[s]
        best=np.min(np.where(available,costs,INF),axis=1)
        exploit=(best<=h)&(rng.random(len(s))>=epsilon)
        options=available & ((costs==best[:,None]) | ~exploit[:,None])
        action=uniform_actions(options,rng)
        nxt=trans[s,action]
        if learn: hist.append((s.copy(),action,nxt,alive.copy()))
        else: hist.append(action.copy())
        actions_taken+=int(alive.sum())
        s=np.where(alive,nxt,s)
        alive &= s!=goal
    if learn:
        for old,a,succ,active in reversed(hist):
            proposed=np.minimum(value[succ]+1,INF)
            np.minimum.at(q,(old[active],a[active]),proposed[active])
            np.minimum.at(value,old[active],proposed[active])
        return int((~alive).sum()),actions_taken
    wins=np.where(~alive)[0]
    examples=[]
    for k in (wins if audit_all else wins[:5]):
        path=[]
        board=starts[k]
        for a in hist:
            if board==goal: break
            path.append(list(MOVES)[int(a[k])])
            board=trans[board,a[k]]
        assert verify(states[starts[k]],path,HORIZON)["reward"]
        examples.append(path)
    return len(wins),examples


def train(env,mode,seed,audit_all=False):
    states,trans,legal,root,goal,depth=env
    q=np.full((len(states),4),INF,dtype=np.uint8)
    value=np.full(len(states),INF,dtype=np.uint8)
    value[goal]=0
    reset_rng=np.random.default_rng(seed+100)
    policy_rng=np.random.default_rng(seed+200)
    eval_rng=np.random.default_rng(seed+300)
    total_hits=total_actions=total_resets=0
    first_hit=first_root=None
    records=[]
    for step in range(STEPS+1):
        if step%100==0 or step==600:
            hits,examples=rollout(env,q,value,np.full(512,root),eval_rng)
            if hits and first_root is None: first_root=step
            records.append(dict(step=step,root_hits=hits,root_trials=512,train_hits=total_hits,
                                active_actions=total_actions,reset_actions=total_resets,
                                learned_states=int((value<INF).sum()),
                                known_root_cost=int(value[root]), examples=examples[:1]))
        if step==STEPS:break
        kind=mode.split("-")[0]
        if mode.endswith("-switch") and step>=600: kind="root"
        start,reset_cost=reset(kind,reset_rng,env)
        wins,actions=rollout(env,q,value,start,policy_rng,learn=True,epsilon=EPSILON)
        total_hits+=wins
        total_actions+=actions
        total_resets+=reset_cost
        if wins and first_hit is None:first_hit=step+1
    # Audit every learned value against exact distances, without training feedback.
    assert np.all((value==INF)|(value>=depth))
    hits,examples=rollout(env,q,value,np.full(512,root),np.random.default_rng(seed+400),audit_all=audit_all)
    return dict(mode=mode,seed=seed,records=records,first_train_hit=first_hit,
                first_root_eval=first_root,independent_root_hits=hits,
                independent_root_trials=512,independent_paths=examples[:5],
                **(dict(verified_paths=len(examples),unique_verified_paths=len(set(map(tuple,examples)))) if audit_all else {}))


if __name__=="__main__":
    env=make_env()
    path=Path(__file__).with_name("results.json")
    rows=[]
    for seed in SEEDS:
        for mode in MODES:
            now=time.monotonic()
            r=train(env,mode,seed)
            r["seconds"]=time.monotonic()-now
            rows.append(r)
            path.write_text(json.dumps(dict(root=ROOT,horizon=HORIZON,steps=STEPS,batch=BATCH,runs=rows),indent=2))
            print(mode,seed,r["first_train_hit"],r["independent_root_hits"],r["records"][-1]["known_root_cost"],flush=True)
