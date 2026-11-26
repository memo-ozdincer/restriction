"""CPU-only fixed-task exposure/switch pilots. No solution labels in training."""
import argparse
import concurrent.futures
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np

HERE = Path(__file__).resolve().parent
TSP_CASE = json.loads((HERE / "tsp_case.json").read_text())
COORDS = np.asarray(TSP_CASE["coordinates"], dtype=np.float32)
TSP_REFERENCE = TSP_CASE["reference"]


def softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    p = np.exp(z)
    return p / p.sum(axis=-1, keepdims=True)


def sample_probs(p, rng):
    return np.minimum((rng.random(len(p))[:, None] > p.cumsum(1)).sum(1), p.shape[1]-1)


def adam(w, grad, m, v, step, lr):
    m *= .9
    m += .1 * grad
    v *= .999
    v += .001 * grad**2
    w += lr * (m / (1 - .9**step)) / (np.sqrt(v / (1 - .999**step)) + 1e-8)


class TSP:
    horizon = 16
    dim = 15
    def __init__(self):
        self.point_count = len(COORDS)
        self.goal = TSP_REFERENCE

    def starts(self, mode, rng, group):
        n = self.point_count
        indices = np.arange(n) if mode == "root" else np.sort(rng.choice(n, int(rng.integers(20,41)), replace=False))
        coords = COORDS[indices]
        d = np.linalg.norm(coords[:,None] - coords[None,:], axis=-1)
        p = rng.permutation(len(coords))
        ii, jj = np.triu_indices(len(coords), 2)
        valid = (jj - ii > 1) & ~((ii == 0) & (jj == len(coords)-1))
        ii,jj = ii[valid],jj[valid]
        moves = np.stack([ii,jj], axis=-1)
        warmup = 0
        # The fixed warmup is local descent, not access to a reference tour.
        while True:
            q = np.roll(p,-1)
            a,b,c,e = p[ii],q[ii],p[jj],q[jj]
            delta = d[a,c]+d[b,e]-d[a,b]-d[c,e]
            k = int(delta.argmin())
            if delta[k] >= -1e-6:
                break
            i,j = moves[k]
            p[i+1:j+1] = p[i+1:j+1][::-1]
            warmup += 1
        return (coords,d,moves,np.tile(p,(group,1))), (warmup,(warmup+1)*len(moves))

    @staticmethod
    def cost(d,p):
        return d[p,np.roll(p,-1,axis=1)].sum(1)

    @staticmethod
    def features(coords,d,moves,p):
        i,j = moves.T
        q = np.roll(p,-1,axis=1)
        a,b,c,e = p[:,i],q[:,i],p[:,j],q[:,j]
        ab,ce,ac,be = d[a,b],d[c,e],d[a,c],d[b,e]
        # Raw coordinate endpoints and scale-normalized distances; identical in all arms.
        scale = (d[p,q].mean(1)+1e-6)[:,None]
        f = np.stack([ab/scale,ce/scale,ac/scale,be/scale,(ab+ce-ac-be)/scale,
                      d[a,e]/scale,d[b,c]/scale],axis=-1)
        g = np.concatenate([coords[a],coords[b],coords[c],coords[e]], axis=-1)
        return np.concatenate([g,f],axis=-1).astype(np.float32)

    def rollout(self,w,start,rng,grad):
        coords,d,moves,p = start
        p = p.copy()
        b = len(p)
        ref = self.cost(d,p)
        best = ref.copy()
        best_tours=p.copy()
        history=[]
        best_trace=[]
        elapsed_best=np.full(b,-1)
        padded_candidates=self.point_count*(self.point_count-3)//2
        for t in range(self.horizon):
            actual=self.features(coords,d,moves,p)
            # Same number of policy score slots and score-gradient operations in every arm.
            x=np.zeros((b,padded_candidates,self.dim),dtype=np.float32)
            x[:,:len(moves)]=actual
            logits=x@w
            logits[:,len(moves):]=-np.inf
            prob=softmax(logits)
            picked=np.minimum(sample_probs(prob,rng),len(moves)-1)
            if grad:
                # Score derivative for each chain; no full feature history needed.
                history.append(x[np.arange(b),picked]-np.einsum("ba,baf->bf",prob,x))
            for row,(i,j) in enumerate(moves[picked]):
                p[row,i+1:j+1] = p[row,i+1:j+1][::-1]
            costs=self.cost(d,p)
            improved = costs < best
            elapsed_best[improved] = t
            best_tours[improved]=p[improved]
            best = np.minimum(best,costs)
            best_trace.append(best.copy())
        # Group-best timestamp cutoff from the published NICO mechanics.
        score=np.maximum(ref-best,0)/np.maximum(ref,1e-8)
        if grad and score.max()>0:
            winning=(score==score.max())
            cutoff=int(elapsed_best[winning].min())
            centered=(ref-best_trace[cutoff])/ref
            centered -= centered.mean()
            gradient=(np.stack(history[:cutoff+1]).sum(0)*centered[:,None]).mean(0)/(cutoff+1)
        else:
            gradient=np.zeros_like(w)
        assert np.all(np.sort(p,axis=1)==np.arange(len(coords)))
        if not grad:
            for tour,cost in zip(best_tours,best):
                assert sorted(tour.tolist())==list(range(len(coords)))
                independently=sum(math.dist(coords[a],coords[b]) for a,b in zip(tour,np.roll(tour,-1)))
                assert abs(independently-cost)<1e-5
        return dict(score=score.tolist(),best=best.tolist(),best_tours=best_tours.tolist() if not grad else [],reference=ref.tolist(),gradient=gradient,
                    informative=bool(np.any(gradient)) if grad else bool(score.max()>score.min()),
                    actions=b*self.horizon,candidates=b*self.horizon*len(moves),
                    padded_candidates=b*self.horizon*padded_candidates)


def flip_masks():
    n=3
    return np.array([sum(1<<(r*n+c) for r,c in [(i,j),(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
                         if 0<=r<n and 0<=c<n) for i in range(n) for j in range(n)],dtype=np.uint16)


MASKS=flip_masks()
GOAL=(1<<9)-1 # all lit
DIST={GOAL:0}
queue=deque([GOAL])
while queue:
    s=queue.popleft()
    for mask in MASKS:
        q=s^int(mask)
        if q not in DIST:
            DIST[q]=DIST[s]+1
            queue.append(q)
ROOT=min(s for s,d in DIST.items() if d==max(DIST.values()))
FEATURES=(((np.arange(512)[:,None]>>np.arange(9))&1)*2-1).astype(np.float32)
FEATURES=np.concatenate([FEATURES,np.ones((512,1),np.float32)],axis=1)


class Flip:
    horizon=DIST[ROOT]
    dim=(10,9)
    goal=GOAL
    def starts(self,mode,rng,group):
        if mode=="root":
            return np.full(group,ROOT,dtype=np.uint16),0
        if mode=="uniform":
            s=int(rng.choice(sorted(set(DIST)-{GOAL})))
            return np.full(group,s,dtype=np.uint16),0
        s=GOAL
        moves=0
        while s==GOAL:
            count=int(rng.integers(1,5))
            for _ in range(count):
                s ^= int(rng.choice(MASKS))
            moves+=count
        return np.full(group,s,dtype=np.uint16),moves

    def rollout(self,w,start,rng,grad):
        state=start.copy()
        done=state==GOAL
        b=len(state)
        hist=[]
        actions=[]
        active=0
        for _ in range(self.horizon):
            x=FEATURES[state]
            prob=softmax(x@w)
            choice=sample_probs(prob,rng)
            if grad:
                diff=-prob
                diff[np.arange(b),choice]+=1
                hist.append((x.copy(),diff,~done))
            if not grad: actions.append(np.where(done,-1,choice))
            active+=int((~done).sum())
            state=np.where(done,state,state^MASKS[choice])
            done |= state==GOAL
        reward=done.astype(np.float32)
        gradient=np.zeros_like(w)
        if grad:
            advantage=reward-reward.mean()
            for x,diff,alive in hist:
                gradient+=x.T@(diff*(advantage*alive)[:,None])/b
        if not grad:
            actions=np.array(actions).T.tolist()
            for first,seq,win in zip(start,actions,done):
                replay=[(int(first)>>i)&1 for i in range(9)]
                for gate in seq:
                    if gate<0:continue
                    i,j=divmod(gate,3)
                    for r,c in [(i,j),(i+1,j),(i-1,j),(i,j+1),(i,j-1)]:
                        if 0<=r<3 and 0<=c<3:replay[3*r+c]^=1
                assert all(replay)==bool(win)
        return dict(score=reward.tolist(),best=reward.tolist(),paths=actions if not grad else [],gradient=gradient,
                    informative=bool(reward.max()>reward.min()),actions=active,candidates=b*self.horizon*9)


def train(domain,arm,seed,updates,group,eval_groups,tsp_gain_init):
    env=TSP() if domain=="tsp" else Flip()
    init=np.random.default_rng(seed)
    w=init.normal(0,.02,env.dim).astype(np.float32)
    if domain=="tsp":w[12]+=tsp_gain_init
    m=np.zeros_like(w);v=np.zeros_like(w)
    reset_rng=np.random.default_rng(seed+10000)
    policy_rng=np.random.default_rng(seed+20000)
    switch = max(1,int(updates*.3))
    records=[]
    inform=success=active=warmup=candidates=padded_candidates=warmup_comparisons=0
    phase_inform=phase_success=0
    t=time.monotonic()
    def evaluate():
        # Every checkpoint and paired arm receives precisely the same evaluation starts.
        rr=np.random.default_rng(seed+30000)
        pr=np.random.default_rng(seed+40000)
        values=[]
        witnesses=[]
        for _ in range(eval_groups):
            start,_=env.starts("root",rr,group)
            result=env.rollout(w,start,pr,False)
            values.extend(result["best"])
            witnesses.extend(result.get("best_tours",result.get("paths",[])))
        index=int(np.argmin(values) if domain=="tsp" else np.argmax(values))
        return dict(witness=witnesses[index],mean=float(np.mean(values)),best=float(min(values) if domain=="tsp" else max(values)),
                    optimum_hits=int(sum(x<=TSP_REFERENCE+1e-5 for x in values)) if domain=="tsp" else int(sum(values)),
                    trials=len(values))
    cadence=max(1,updates//10)
    for step in range(updates+1):
        if step%cadence==0 or step==switch or step==updates:
            records.append(dict(step=step,evaluation=evaluate(),informative_groups=inform,
                                positive_rollouts=success,active_actions=active,warmup_actions=warmup,
                                candidate_scores=candidates,padded_candidate_scores=padded_candidates,
                                warmup_candidate_comparisons=warmup_comparisons,phase_informative=phase_inform,
                                phase_positive=phase_success))
        if step==updates:break
        mode="root" if arm=="root" or (arm.endswith("_switch") and step>=switch) else arm.removesuffix("_switch")
        if step==switch:
            phase_inform=phase_success=0
        start,cost=env.starts(mode,reset_rng,group)
        result=env.rollout(w,start,policy_rng,True)
        if domain=="tsp":
            count,comparisons=cost
            warmup+=count;warmup_comparisons+=comparisons
        else:
            warmup+=cost
        active+=result["actions"]; candidates+=result["candidates"]
        padded_candidates+=result.get("padded_candidates",result["candidates"])
        info=int(result["informative"]); positives=sum(x>0 for x in result["score"])
        inform+=info;success+=positives;phase_inform+=info;phase_success+=positives
        adam(w,result["gradient"],m,v,step+1,.01)
    return dict(domain=domain,arm=arm,seed=seed,group=group,updates=updates,horizon=env.horizon,switch=switch,
                padded_slots=updates*group*env.horizon,tsp_gain_init=tsp_gain_init if domain=="tsp" else None,records=records,weights=w.tolist(),
                seconds=time.monotonic()-t)


def job(args):
    return train(*args)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--domain",choices=["tsp","flip","both"],default="both")
    p.add_argument("--updates",type=int,default=1000)
    p.add_argument("--tsp-gain-init",type=float,choices=[0.,10.],default=10.)
    p.add_argument("--group",type=int,default=16)
    p.add_argument("--eval-groups",type=int,default=8)
    p.add_argument("--seeds",type=int,nargs="+",default=[42,43,44,45,46,47,48,49])
    p.add_argument("--workers",type=int,default=1)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    arms={"tsp":["root","subset","subset_switch"],"flip":["root","uniform","uniform_switch","near","near_switch"]}
    domains=list(arms) if a.domain=="both" else [a.domain]
    jobs=[(d,m,s,a.updates,a.group,a.eval_groups,a.tsp_gain_init) for d in domains for m in arms[d] for s in a.seeds]
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
        for result in pool.map(job,jobs):
            name=f'{result["domain"]}-{result["arm"]}-{result["seed"]}.json'
            (a.out/name).write_text(json.dumps(result,separators=(",",":")))
            print(name,result["records"][-1],flush=True)


if __name__=="__main__":
    main()
