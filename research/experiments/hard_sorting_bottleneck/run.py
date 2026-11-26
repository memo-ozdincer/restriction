"""Fixed adjacent comparator sorting-network bottleneck."""
from collections import deque
from pathlib import Path
import argparse, json, sys, time
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"sorting_initial"))
from environment import identity, goal, step, verify

def graph(n):
    gates=[(i,i+1) for i in range(n-1)]
    root=identity(n); states,index=[root],{root:0}; rows=[]
    for s in states:
        row=[]
        for a in gates:
            t=step(n,s,a)
            if t not in index:
                index[t]=len(states);states.append(t)
            row.append(index[t])
        rows.append(row)
    transitions=np.array(rows,np.int32)
    target=index[goal(n)]
    rev=[[] for _ in states]
    for i,row in enumerate(transitions):
        for j in row:rev[j].append(i)
    depth=np.full(len(states),-1,np.int32);depth[target]=0;q=deque([target])
    while q:
        j=q.popleft()
        for i in rev[j]:
            if depth[i]<0:depth[i]=depth[j]+1;q.append(i)
    assert depth[0]==n*(n-1)//2 and min(depth)>=0
    bits=[i for i in range(1<<n) if not (goal(n)>>i)&1]
    feat=np.array([[(s>>i)&1 for i in bits] for s in states],np.float32)
    return transitions,feat,target,depth,states,gates

def calibration(n,env):
    trans,_,target,depth,states,gates=env
    A=len(gates);h=int(depth[0])
    p=np.zeros(len(states));p[target]=1
    for _ in range(h):
        p=p[trans].mean(axis=1);p[target]=1
    out=dict(n=n,states=len(states),optimal=h,root_random_probability=float(p[0]))
    z=np.eye(1,len(states),0).ravel();mix=np.zeros_like(z)
    for i in range(1,25):
        z=np.bincount(trans.ravel(),weights=np.repeat(z/A,A),minlength=len(states))
        mix+=z
        if i in (4,6,8,12,18,24):
            v=mix.copy();v[target]=0;v/=v.sum()
            out[f"walk{i}"]=dict(probability=float(p@v),mean_distance=float(depth@v))
    return out


def reset(trans,target,size,radius,rng):
    if radius==0:return np.zeros(size,np.int32),0
    out=np.full(size,target,np.int32);cost=0;A=trans.shape[1]
    while np.any(out==target):
        mask=out==target
        lengths=rng.integers(1,radius+1,size=int(mask.sum()))
        x=np.zeros(len(lengths),np.int32)
        for t in range(radius):
            active=t<lengths
            x[active]=trans[x[active],rng.integers(A,size=int(active.sum()))]
        cost+=int(lengths.sum());out[mask]=x
    return out,cost

def rollout(weights,starts,env,rng,h,gradient=False,trace=False):
    trans,feat,target,_,_,_=env
    A=trans.shape[1];states=starts.copy();alive=states!=target
    history=[];trajectory=[];active_count=0
    for _ in range(h):
        x=feat[states];logits=x@weights
        p=np.exp(logits-logits.max(axis=1,keepdims=True));p/=p.sum(axis=1,keepdims=True)
        choice=np.minimum((rng.random(len(states))[:,None]>np.cumsum(p,axis=1)).sum(axis=1),A-1)
        if gradient:history.append((x,p,choice,alive.copy()))
        if trace:trajectory.append(choice.copy())
        active_count+=int(alive.sum())
        states=np.where(alive,trans[states,choice],states);alive &= states!=target
    reward=(~alive).astype(np.float32);hits=int(reward.sum())
    result=dict(hits=hits,actions=active_count)
    if gradient:
        adv=reward-reward.mean();grad=np.zeros_like(weights)
        if np.any(adv):
            for x,p,choice,active in history:
                score=-p.copy();score[np.arange(len(choice)),choice]+=1
                score*=(adv*active)[:,None];grad+=x.T@score/len(starts)
        result['gradient']=grad
    if trace:result.update(states=states,trajectory=np.array(trajectory).T)
    return result

def exact_root(weights,env,h):
    trans,feat,target,_,_,_=env
    logits=(feat@weights).astype(np.float64)
    p=np.exp(logits-logits.max(axis=1,keepdims=True));p/=p.sum(axis=1,keepdims=True)
    hit=np.zeros(len(trans));hit[target]=1
    for _ in range(h):
        hit=(hit[trans]*p).sum(axis=1);hit[target]=1
    return float(hit[0])

def train(radius,switch,seed,env,steps=2000,n=8):
    trans,feat,target,depth,_,gates=env
    h=int(depth[0]);A=len(gates);B=64
    rng=np.random.default_rng(seed);reset_rng=np.random.default_rng(seed+20000)
    eval_rng=np.random.default_rng(seed+10000)
    w=rng.normal(0,.02,(feat.shape[1],A)).astype(np.float32)
    m=np.zeros_like(w);v=np.zeros_like(w);records=[]
    count=reset_count=active=0;first=None
    now=time.monotonic()
    for i in range(steps+1):
        if i%200==0 or i==steps:
            r=rollout(w,np.zeros(512,np.int32),env,eval_rng,h)
            records.append(dict(step=i,root_hits=r['hits'],train_hits=count,
                                train_actions=active,reset_actions=reset_count))
        if i==steps:break
        rad=0 if switch and i>=int(steps*.3) else radius
        starts,cost=reset(trans,target,B,rad,reset_rng)
        r=rollout(w,starts,env,rng,h,True)
        count+=r['hits'];reset_count+=cost;active+=r['actions']
        if first is None and r['hits']:first=i
        grad=r['gradient']
        m=.9*m+.1*grad;v=.999*v+.001*grad*grad
        w+=.01*(m/(1-.9**(i+1)))/(np.sqrt(v/(1-.999**(i+1)))+1e-8)
    r=rollout(w,np.zeros(512,np.int32),env,np.random.default_rng(seed+30000),h,trace=True)
    wins={}
    for state,actions in zip(r['states'],r['trajectory']):
        if state!=target:continue
        a=tuple(map(int,actions));assert verify(n,[gates[j] for j in a],h)['reward']==1
        wins[a]=wins.get(a,0)+1
    assert sum(wins.values())==r['hits']
    return dict(radius=radius,switch=switch,seed=seed,steps=steps,batch=B,horizon=h,
                n=n,first_train_hit=first,records=records,root_exact=exact_root(w,env,h),
                fresh_hits=r['hits'],fresh_trials=512,
                paths=[dict(actions=a,count=c) for a,c in wins.items()],
                weights=w.tolist(),seconds=time.monotonic()-now)

_ENV=None
def worker(args):
    global _ENV
    radius,switch,seed,steps,n=args
    if _ENV is None:_ENV=graph(n)
    return train(radius,switch,seed,_ENV,steps,n)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--calibrate",action="store_true")
    p.add_argument("--steps",type=int,default=2000)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--seeds",type=int,nargs="+",default=list(range(42,50)))
    p.add_argument("--n",type=int,default=8)
    p.add_argument("--out",type=Path,default=Path(__file__).with_name("results.json"))
    args=p.parse_args()
    if args.calibrate:
        results=[]
        for n in (6,7,8):
            e=graph(n);r=calibration(n,e);results.append(r);print(r,flush=True)
        Path(__file__).with_name("calibration.json").write_text(json.dumps(results,indent=2))
    else:
        import multiprocessing as mp
        modes=[(0,False)]+[(r,s) for r in (12,18,24) for s in (False,True)]
        tasks=[(r,s,seed,args.steps,args.n) for r,s in modes for seed in args.seeds]
        results=[]
        with mp.get_context("spawn").Pool(args.workers) as pool:
            for row in pool.imap_unordered(worker,tasks):
                results.append(row)
                args.out.write_text(json.dumps(results,indent=2))
                print(row['radius'],row['switch'],row['seed'],row['first_train_hit'],row['root_exact'],
                      row['fresh_hits'],round(row['seconds'],2),flush=True)
