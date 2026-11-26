"""Terminal-only sorting-network training under controlled freedoms."""
from collections import deque
from pathlib import Path
import argparse
import json
import sys
import time
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sorting_initial"))
from environment import identity, goal, step, verify, unresolved

N = 6
GATES = [(i, i+1) for i in range(N-1)] + [(0,3),(1,4),(2,5)]
A = len(GATES)
H = 12
SLOTS = 1536
STEPS = 300
SEEDS = range(42, 50)


def graph():
    root = identity(N)
    states, index = [root], {root:0}
    for s in states:
        for a in GATES:
            t = step(N,s,a)
            if t not in index:
                index[t] = len(states)
                states.append(t)
    transitions = np.array([[index[step(N,s,a)] for a in GATES] for s in states], dtype=np.int32)
    target = index[goal(N)]
    reverse = [[] for _ in states]
    for i, row in enumerate(transitions):
        for j in row:
            reverse[j].append(i)
    depth = np.full(len(states), -1, dtype=np.int32)
    depth[target] = 0
    queue = deque([target])
    while queue:
        j = queue.popleft()
        for i in reverse[j]:
            if depth[i] < 0:
                depth[i] = depth[j] + 1
                queue.append(i)
    assert depth[0] == H and min(depth) >= 0
    # sorted rows are always invariant, so omit the constant features.
    rows = [i for i in range(1<<N) if not (goal(N) >> i) & 1]
    feat = np.array([[(s >> i)&1 for i in rows] for s in states], dtype=np.float32)
    equiv = np.flatnonzero(depth == depth[0])
    return transitions, feat, target, depth, states, equiv


def sample_starts(mode, size, rng, env):
    trans, _, target, _, states, equiv = env
    if mode == "root":
        return np.zeros(size, np.int32), 0, 0
    if mode == "uniform":
        draws = rng.integers(0,len(states)-1,size=size,dtype=np.int32)
        return draws + (draws>=target), 0, 0
    if mode == "equal":
        return rng.choice(equiv,size=size),0,0
    if mode == "mixed":
        # An independent fair coin chooses the radius family per episode.
        short_mask=rng.random(size)<.5
        out=np.empty(size,dtype=np.int32)
        total=rejects=0
        for mask,source in ((short_mask,"short"),(~short_mask,"wide")):
            if mask.any():
                out[mask],cost,rejected=sample_starts(source,int(mask.sum()),rng,env)
                total+=cost;rejects+=rejected
        return out,total,rejects
    maximum = {"tiny":2,"short":4,"radius6":6,"radius8":8,"medium":12,"long":24,"wide":36}[mode]
    # Random walk lengths are sampled without inspecting states; exclude
    # already-solved starts, count rejection and all reset transitions.
    out = np.full(size,target,dtype=np.int32)
    total=rejects=0
    while np.any(out==target):
        mask=out==target
        lengths=rng.integers(1,maximum+1,size=int(mask.sum()))
        x=np.zeros(len(lengths),dtype=np.int32)
        for t in range(maximum):
            active=t<lengths
            if active.any():
                x[active]=trans[x[active],rng.integers(A,size=int(active.sum()))]
        total+=int(lengths.sum())
        rejects+=int((x==target).sum())
        out[mask]=x
    return out,total,rejects


def rollout(weights, starts, horizon, env, rng, macro=False, gradient=False, trace=False):
    trans,feat,target,_,_,_=env
    states=starts.copy()
    alive=states!=target
    active_count=calls=0
    history=[]
    trajectory=[]
    width=2 if macro else 1
    for t in range(0,horizon,width):
        x=feat[states]
        logits=x@weights
        p=np.exp(logits-logits.max(axis=1,keepdims=True))
        p/=p.sum(axis=1,keepdims=True)
        cumulative=np.cumsum(p,axis=1)
        calls+=len(states)
        for k in range(min(width,horizon-t)):
            choice=np.minimum((rng.random(len(states))[:,None]>cumulative).sum(axis=1),A-1)
            if gradient:
                history.append((x,p,choice,alive.copy()))
            if trace:
                trajectory.append(choice.copy())
            active_count+=int(alive.sum())
            states=np.where(alive,trans[states,choice],states)
            alive &= states!=target
    reward=(~alive).astype(np.float32)
    result=dict(hits=int(reward.sum()),actions=active_count,policy_calls=calls)
    if trace:
        result.update(terminal=states,trajectory=np.array(trajectory).T)
    if gradient:
        advantage=reward-reward.mean()
        grad=np.zeros_like(weights)
        for x,p,choice,active in history:
            score=-p.copy()
            score[np.arange(len(choice)),choice]+=1
            score *= (advantage*active)[:,None]
            grad+=x.T@score/len(starts)
        result["gradient"]=grad
    return result


def train(mode, seed, env, steps=STEPS):
    # mode = source / horizon / action-chunk / switch
    source,horizon,macro,switch=mode
    rng=np.random.default_rng(seed)
    sampler_rng=np.random.default_rng(seed+20000)
    eval_rng=np.random.default_rng(seed+10000)
    weights=rng.normal(0,.02,(env[1].shape[1],A)).astype(np.float32)
    m=np.zeros_like(weights);v=np.zeros_like(weights)
    records=[]
    stats=dict(train_hits=0,train_rollouts=0,train_actions=0,train_policy_calls=0,
               reset_actions=0,reset_rejected=0,train_action_slots=0)
    start_time=time.monotonic()
    for i in range(steps+1):
        if i%30==0 or i==steps:
            result=rollout(weights,np.zeros(512,dtype=np.int32),H,env,eval_rng)
            records.append(dict(step=i,root_hits=result["hits"],root_trials=512,**stats))
        if i==steps:break
        active_mode=("root",H,False) if switch and i>=int(steps*.3) else (source,horizon,macro)
        src,h,mc=active_mode
        size=SLOTS//h
        starts,reset_actions,rejects=sample_starts(src,size,sampler_rng,env)
        result=rollout(weights,starts,h,env,rng,mc,True)
        stats["train_hits"]+=result["hits"]
        stats["train_rollouts"]+=size
        stats["train_actions"]+=result["actions"]
        stats["train_policy_calls"]+=result["policy_calls"]
        stats["reset_actions"]+=reset_actions
        stats["reset_rejected"]+=rejects
        stats["train_action_slots"]+=size*h
        grad=result["gradient"]
        m=.9*m+.1*grad;v=.999*v+.001*grad*grad
        weights += .01*(m/(1-.9**(i+1)))/(np.sqrt(v/(1-.999**(i+1)))+1e-8)
    # Recheck fresh root-winning sequences with independent scalar replay.
    result=rollout(weights,np.zeros(512,dtype=np.int32),H,env,np.random.default_rng(seed+30000),trace=True)
    successes={}
    for terminal,trajectory in zip(result["terminal"],result["trajectory"]):
        actions=[GATES[a] for a in trajectory]
        checked=verify(N,actions,H)
        assert checked["reward"]==(terminal==env[2])
        if checked["reward"]:
            key=tuple(map(int,trajectory))
            successes[key]=successes.get(key,0)+1
    assert sum(successes.values())==result["hits"]
    return dict(mode=mode,seed=seed,records=records,seconds=time.monotonic()-start_time,
                independent_root_hits=result["hits"],independent_root_trials=512,
                successful_paths=[dict(actions=p,count=c) for p,c in successes.items()])


def calibration(env):
    trans,_,target,depth,states,equiv=env
    result=dict(states=len(states),goal=int(target),root_distance=int(depth[0]),
                equal_distance_count=len(equiv),depth_counts=np.bincount(depth).tolist())
    by_h={}
    for horizon in (12,24,48):
        p=np.eye(1,len(states),target).ravel()
        for _ in range(horizon):
            p=p[trans].mean(axis=1)
            p[target]=1
        cells={}
        for source in ("root","short","medium","long","wide","uniform","equal"):
            # Compute walk distributions exactly; reject terminal.
            if source=="root":
                prob=np.eye(1,len(states),0).ravel()
            elif source=="uniform":
                prob=np.ones(len(states));prob[target]=0;prob/=prob.sum()
            elif source=="equal":
                prob=np.zeros(len(states));prob[equiv]=1/len(equiv)
            else:
                maxlen={"short":4,"medium":12,"long":24,"wide":36}[source]
                x=np.eye(1,len(states),0).ravel();prob=np.zeros(len(states))
                for _ in range(maxlen):
                    x=np.bincount(trans.ravel(),weights=np.repeat(x/A,A),minlength=len(states))
                    prob+=x/maxlen
                prob[target]=0;prob/=prob.sum()
            cells[source]=dict(success=float(prob@p),mean_distance=float(prob@depth),
                               support=int((prob>0).sum()))
        by_h[horizon]=cells
    result["horizons"]=by_h
    return result


def modes():
    yield ("root",12,False,False)
    for source in ("short","medium","long","wide","uniform","equal"):
        for switch in (False,True):
            yield (source,12,False,switch)
    for horizon in (24,48):
        for switch in (False,True):
            yield ("root",horizon,False,switch)
    for switch in (False,True):
        yield ("medium",24,False,switch)
        yield ("root",12,True,switch)
        yield ("medium",12,True,switch)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--steps",type=int,default=STEPS)
    parser.add_argument("--seeds",type=int,nargs="+",default=list(SEEDS))
    parser.add_argument("--out",type=Path,default=Path(__file__).with_name("results.json"))
    args=parser.parse_args()
    env=graph()
    results=dict(calibration=calibration(env),runs=[])
    print("Calibration",json.dumps(results["calibration"]),flush=True)
    for mode in modes():
        if mode[0]=="equal" and len(env[-1])==1:continue
        for seed in args.seeds:
            run=train(mode,seed,env,args.steps)
            results["runs"].append(run)
            args.out.write_text(json.dumps(results,indent=2))
            print(mode,seed,run["records"][-1]["root_hits"],run["independent_root_hits"],flush=True)
