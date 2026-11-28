"""CPU tree discovery; no analytical witnesses imported by learners.

Hypotheses: raw defect selects low-magnitude negative coefficients; normalized
terminal scoring may change the trap. Isomorphic duplicate balancing and native
subtree recombination may improve discovery without prescribed motifs. Binary
PG updates only on mixed reward groups. CEM, pattern-lite, and local search are
search/elite-learning comparators, not described as ordinary on-policy RL.
All methods optimize a fixed size/target; no cross-size transfer claim.
"""
from __future__ import annotations
import argparse
import json
import math
import time
from collections import Counter
from pathlib import Path
import numpy as np
from environment import (prufer_to_edges, edges_to_prufer, independence_polynomial,
                         domination_polynomial, tree_id, violations, score, defect)


def adj(n, edges):
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a].append(b); g[b].append(a)
    return g


def component(g, root, avoid):
    seen = {avoid}; out = []; stack = [root]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u); out.append(u)
        stack.extend(v for v in g[u] if v not in seen)
    return out


def random_edge_edit(n, code, rng):
    """Delete a uniformly random edge, reconnect the two components uniformly."""
    e = list(prufer_to_edges(code, n)); j = int(rng.integers(n-1)); a,b = e.pop(j)
    side = component(adj(n, e), a, b); s = set(side)
    other = [u for u in range(n) if u not in s]
    e.append((int(rng.choice(side)), int(rng.choice(other))))
    return np.array(edges_to_prufer(n,e),dtype=np.int64)


def cut_components(n, edges):
    g=adj(n,edges); out={}
    for a,b in edges:
        for root,parent in ((a,b),(b,a)):
            c=component(g,root,parent)
            out.setdefault(len(c),[]).append((root,parent,c))
    return out


def crossover(n, recipient, donor, rng):
    """Uniformly choose compatible pendant components, replace recipient's
    component by donor's rooted topology. No score or mathematical motif.
    The replaced component can include all but one vertex. The recipient
    labels are randomly assigned, except its attachment root is preserved.
    Returns (code, structural edge edit count)."""
    e=list(prufer_to_edges(recipient,n)); d=list(prufer_to_edges(donor,n))
    ec=cut_components(n,e); dc=cut_components(n,d)
    common=sorted(set(ec)&set(dc))
    nontrivial=[s for s in common if s>1]
    if nontrivial:
        common=nontrivial
    # Uniform over feasible sizes, then cuts; no preference for specific size.
    k=int(rng.choice(common)); r,p,rs=ec[k][int(rng.integers(len(ec[k])))]
    dr,dp,ds=dc[k][int(rng.integers(len(dc[k])))]
    rset=set(rs); dset=set(ds); rem=[x for x in rs if x!=r]; rng.shuffle(rem)
    mapping={dr:r}; mapping.update(zip((x for x in ds if x!=dr),rem))
    new=[(a,b) for a,b in e if not (a in rset and b in rset)]
    new.extend((mapping[a],mapping[b]) for a,b in d if a in dset and b in dset)
    oldset={tuple(sorted(q)) for q in e}; newset={tuple(sorted(q)) for q in new}
    edits=len(oldset-newset)
    return np.array(edges_to_prufer(n,new),dtype=np.int64),edits


class Policy:
    """Small categorical autoregression. Token logits depend on the position,
    previous token and each token's own occurrence count (native history).
    No hand-coded graph score or preferred motif. Shared count parameters
    enable exchangeable multiplicity learning; position/transition terms
    permit label-specific structures. Fixed n, not a transferable architecture."""
    def __init__(self,n):
        self.n=n; self.length=n-2
        self.params=[np.zeros((self.length,n)),np.zeros((n+1,n)),np.zeros(n)]
        self.m=[x.copy() for x in self.params]; self.v=[x.copy() for x in self.params]; self.t=0
    def probs(self,pos,prev,counts):
        x=self.params[0][pos]+self.params[1][prev]+self.params[2][counts]
        x=x-x.max(axis=1,keepdims=True); x=np.exp(x); return x/x.sum(axis=1,keepdims=True)
    def sample(self,batch,rng):
        n=self.n; codes=np.empty((batch,self.length),dtype=np.int64)
        prev=np.full(batch,n,dtype=np.int64); counts=np.zeros((batch,n),dtype=np.int64); rows=np.arange(batch)
        for pos in range(self.length):
            p=self.probs(pos,prev,counts)
            q=(np.cumsum(p,axis=1)<rng.random(batch)[:,None]).sum(axis=1)
            q=np.minimum(q,n-1); codes[:,pos]=q; counts[rows,q]+=1; prev=q
        return codes
    def update(self,codes,weights,lr):
        if not np.any(weights): return False
        n=self.n; batch=len(codes); prev=np.full(batch,n,dtype=np.int64)
        counts=np.zeros((batch,n),dtype=np.int64); rows=np.arange(batch)
        g=[np.zeros_like(x) for x in self.params]
        for pos in range(self.length):
            p=self.probs(pos,prev,counts); q=codes[:,pos]
            z=-p; z[rows,q]+=1.; z*=weights[:,None]
            g[0][pos]=z.sum(axis=0); np.add.at(g[1],prev,z)
            g[2]+=np.bincount(counts.ravel(),weights=z.ravel(),minlength=n)
            counts[rows,q]+=1; prev=q
        self.t+=1
        # Normalize per-token shared count gradient by sequence length to
        # keep the shared parameter scale comparable. Adam is same all arms.
        g[2]/=self.length
        for i,x in enumerate(self.params):
            self.m[i]=.9*self.m[i]+.1*g[i]; self.v[i]=.999*self.v[i]+.001*g[i]**2
            x+=lr*(self.m[i]/(1-.9**self.t))/(np.sqrt(self.v[i]/(1-.999**self.t))+1e-8)
            np.clip(x,-12,12,out=x)
        return True


class Evaluator:
    def __init__(self,args):
        self.args=args; self.calls=0; self.successes=0; self.hit_ids=set(); self.seen_ids=set(); self.first_hit=None
        self.witnesses=[]; self.best=None; self.max_violations=0; self.max_violation_example=None
    def evaluate(self,code):
        a=self.args; n=a.n; edges=prufer_to_edges(code,n)
        coeff=(independence_polynomial if a.family=='independence' else domination_polynomial)(n,edges)
        vs=tuple(violations(coeff)); hit=int(a.index in vs) if a.index is not None else int(len(vs)>=a.required)
        val=score(coeff,index=a.index,required=a.required,mode=a.score)
        # Preserve exact integer ranking for raw score; convert Fraction/other
        # numeric values only after exact native success checking.
        val=int(val) if a.score in ('raw','binary') else float(val)
        cid=tree_id(n,edges); self.calls+=1; self.seen_ids.add(cid)
        if hit:
            self.successes+=1
            if self.first_hit is None:self.first_hit=self.calls
            if cid not in self.hit_ids:
                self.hit_ids.add(cid)
                if len(self.witnesses)<128:
                    self.witnesses.append({'code':list(map(int,code)), 'id':cid, 'violations':list(vs),
                                           'defects':{str(i):str(defect(coeff,i)) for i in vs}})
        # Best by exact objective, with native witness information.
        if self.best is None or val>self.best['score']:
            self.best={'score':val,'code':list(map(int,code)), 'id':cid,'violations':list(vs),
                       'support':[i for i,x in enumerate(coeff) if x>0], 'call':self.calls}
        if len(vs)>self.max_violations:
            self.max_violations=len(vs); self.max_violation_example={'code':list(map(int,code)),'violations':list(vs),
                'defects':{str(i):str(defect(coeff,i)) for i in vs}}
        return val,hit,cid,len(vs),max(i for i,x in enumerate(coeff) if x>0) if a.family=='independence' else min(i for i,x in enumerate(coeff) if x>0)


def select_mask(ids, hits, selected, variant, mode, rng):
    """For binary, only correct duplicate examples eligible for balancing.
    For dense, all selected examples eligible. Matched control masks the
    same number from the same eligible pool uniformly. Failures unchanged
    in binary. Returns actual retained selection and blocked count."""
    eligible=[i for i in selected if mode!='binary' or hits[i]]
    seen=set(); dup=[]
    for i in rng.permutation(eligible):
        if ids[i] in seen: dup.append(int(i))
        else: seen.add(ids[i])
    if variant=='balanced': blocked=set(dup)
    elif variant=='matched': blocked=set(map(int,rng.choice(eligible,size=len(dup),replace=False))) if dup else set()
    else: blocked=set()
    return [int(i) for i in selected if i not in blocked],len(blocked)


def pg_weights(vals, hits, ids, variant, mode, rng):
    # Exact equality must precede floating moments: a rounded mean of
    # repeated float rewards can otherwise manufacture nonzero variance.
    if all(v==vals[0] for v in vals):return np.zeros(len(vals)),0
    r=np.asarray(vals,dtype=np.float64); scale=r.std()
    if not scale or not np.isfinite(scale):return np.zeros(len(r)),0
    w=(r-r.mean())/(scale*len(r))
    retained,blocked=select_mask(ids,hits,list(range(len(r))),variant,mode,rng)
    if blocked:
        keep=np.zeros(len(r),dtype=bool); keep[retained]=True; w[~keep]=0
    return w,blocked


def cem_weights(vals,hits,ids,variant,mode,rng,elite_frac):
    # Constant groups contain no reward signal. Uniform tie-breaking otherwise.
    if all(v==vals[0] for v in vals):return np.zeros(len(vals)),0
    order=list(rng.permutation(len(vals))); order.sort(key=lambda i:vals[i],reverse=True)
    k=max(1,int(math.ceil(len(vals)*elite_frac))); selected=order[:k]
    if mode=='binary': selected=[i for i in selected if hits[i]]
    selected,blocked=select_mask(ids,hits,selected,variant,mode,rng)
    w=np.zeros(len(vals)); w[selected]=1./k
    return w,blocked


def summary_batch(records):
    val,hit,cid,nviol,support=zip(*records); c=Counter(cid)
    return {'successes':sum(hit),'unique':len(c),'largest_family':max(c.values()),
            'best_score':max(val),'max_violations':max(nviol),'mean_support_endpoint':float(np.mean(support))}


def run(args):
    started=time.monotonic(); rng=np.random.default_rng(args.seed); erng=np.random.default_rng(args.seed+10_000_019)
    ev=Evaluator(args); ee=Evaluator(args); n=args.n; b=args.batch; method=args.method; variant=args.variant
    policy=Policy(n); archive=[]; history=[]; checkpoints=[]; blocked_total=0; edits=0; aug=0; steps=0
    chains=None; current=None; total_updates=0; mixed=0; nonzero=0
    def fresh_eval(step):
        codes=policy.sample(args.eval_batch,erng) if method in ('pg','cem','pattern-lite') else erng.integers(n,size=(args.eval_batch,n-2))
        records=[ee.evaluate(code) for code in codes]
        checkpoints.append({'step':step,'training_calls':ev.calls,'evaluation_calls':ee.calls,**summary_batch(records)})
    if args.eval_batch:fresh_eval(0)
    for step in range(1,args.steps+1):
        if method in ('hill','anneal'):
            if chains is None:
                chains=rng.integers(n,size=(b,n-2)); current=[ev.evaluate(c) for c in chains]
            proposed=np.array([random_edge_edit(n,c,rng) for c in chains]); edits+=b
            rec=[ev.evaluate(c) for c in proposed]
            # Annealing compares normalized score difference by a group scale;
            # this avoids implicit dependence on huge raw magnitudes. Exact
            # rankings remain exact. Greedy uses no float penalty.
            scale=max(1e-20,float(np.std([float(r[0]) for r in rec+current])))
            temp=max(.01,1.-(step-1)/args.steps)
            for j,(old,new) in enumerate(zip(current,rec)):
                accept=new[0]>=old[0] or (method=='anneal' and rng.random()<math.exp(max(-700,float(new[0]-old[0])/(scale*temp))))
                if accept:chains[j]=proposed[j];current[j]=new
        else:
            proposed=(rng.integers(n,size=(b,n-2)) if method=='random' else policy.sample(b,rng))
            if variant in ('crossover','random-donor','edit') and method in ('cem','pattern-lite'):
                for j in rng.choice(b,size=int(b*args.augmentation_frac),replace=False):
                    acc=archive[int(rng.integers(len(archive)))] if archive else rng.integers(n,size=n-2)
                    donor=rng.integers(n,size=n-2) if variant=='random-donor' else acc
                    candidate,k=crossover(n,proposed[j],donor,rng)
                    if variant=='edit':
                        candidate=proposed[j]
                        for _ in range(k):candidate=random_edge_edit(n,candidate,rng)
                    proposed[j]=candidate; aug+=1; edits+=k
            rec=[ev.evaluate(c) for c in proposed]
            raw=summary_batch(rec)
            if method=='pattern-lite':
                # Fixed k independent legal edge-swap proposals, accept
                # nondecreasing exact score. Not paper replication (which
                # checks all cycle-deletions for a sampled edge insertion).
                for _ in range(args.local_steps):
                    cand=np.array([random_edge_edit(n,c,rng) for c in proposed]); edits+=b
                    updated=[ev.evaluate(c) for c in cand]
                    for j,(old,new) in enumerate(zip(rec,updated)):
                        if new[0]>=old[0]:proposed[j]=cand[j];rec[j]=new
            if method in ('pg','cem','pattern-lite'):
                vals,hits,ids,_,_=zip(*rec); mixed+=int(0<sum(hits)<b)
                nonzero+=int(any(v!=vals[0] for v in vals))
                if method=='pg':w,blocked=pg_weights(vals,hits,ids,variant,args.score,rng)
                else:w,blocked=cem_weights(vals,hits,ids,variant,args.score,rng,args.elite_frac)
                blocked_total+=blocked; total_updates+=int(policy.update(proposed,w,args.lr))
                if variant in ('crossover','random-donor','edit'):
                    # Uniform bounded FIFO archive of prior native proposals,
                    # both successful and failed; no analyst witness.
                    archive.extend(c.copy() for c in proposed); archive=archive[-args.archive_size:]
        record={'step':step,'training_calls':ev.calls,'hits_total':ev.successes,'unique_hits_total':len(ev.hit_ids),
                'updates_total':total_updates,'blocked_total':blocked_total,**summary_batch(rec)}
        if method=='pattern-lite':record['before_local']=raw
        history.append(record); steps=step
        if args.eval_batch and (step%args.eval_every==0 or step==args.steps):fresh_eval(step)
    elapsed=time.monotonic()-started
    out={'config':vars(args),'train':{'calls':ev.calls,'successes':ev.successes,'first_hit':ev.first_hit,
            'unique_successes':len(ev.hit_ids),'unique_sampled':len(ev.seen_ids),'best':ev.best,
            'max_violations':ev.max_violations,'max_violation_example':ev.max_violation_example,'witnesses':ev.witnesses},
         'evaluation':{'calls':ee.calls,'successes':ee.successes,'unique_successes':len(ee.hit_ids),
                       'witnesses':ee.witnesses,'checkpoints':checkpoints},
         'counters':{'steps':steps,'updates':total_updates,'mixed_binary_groups':mixed,'nonconstant_score_groups':nonzero,
                     'blocked_samples':blocked_total,'edge_edit_count':edits,'augmented_proposals':aug},
         'history':history,'elapsed_seconds':elapsed,'queries_per_second':(ev.calls+ee.calls)/max(elapsed,1e-9),
         'policy':{'params':[x.tolist() for x in policy.params],'updates':policy.t},
         'notes':'evaluation always fresh ordinary generation; for nonlearned search methods evaluation is uniform random (not a learned policy).'}
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'output':str(path),'calls':ev.calls,'hits':ev.successes,
        'unique_hits':len(ev.hit_ids),'best':ev.best['score'],'max_violations':ev.max_violations,'elapsed':elapsed,'qps':out['queries_per_second']}),flush=True)
    return out


def parse_args(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--family',choices=['independence','domination'],default='independence');p.add_argument('--n',type=int,required=True)
    p.add_argument('--index',type=int);p.add_argument('--required',type=int,default=1)
    p.add_argument('--score',choices=['raw','normalized','binary'],default='normalized')
    p.add_argument('--method',choices=['random','hill','anneal','pg','cem','pattern-lite'],default='pg')
    p.add_argument('--variant',choices=['ordinary','balanced','matched','crossover','random-donor','edit'],default='ordinary')
    p.add_argument('--steps',type=int,default=100);p.add_argument('--batch',type=int,default=128);p.add_argument('--seed',type=int,default=42)
    p.add_argument('--eval-batch',type=int,default=256);p.add_argument('--eval-every',type=int,default=25)
    p.add_argument('--elite-frac',type=float,default=.1);p.add_argument('--lr',type=float,default=.03)
    p.add_argument('--augmentation-frac',type=float,default=.25);p.add_argument('--archive-size',type=int,default=1024)
    p.add_argument('--local-steps',type=int,default=4);p.add_argument('--output',required=True)
    a=p.parse_args(argv)
    if a.n<3 or a.steps<1 or a.batch<2 or a.required<1 or a.eval_batch<0 or a.eval_every<1 or not 0<a.elite_frac<=1 or not 0<=a.augmentation_frac<=1 or a.archive_size<1 or a.local_steps<0:p.error('invalid size/budget')
    if a.index is not None and (a.required!=1 or not 0<a.index<a.n):p.error('fixed index requires one interior violation')
    if a.variant in ('balanced','matched') and a.method not in ('pg','cem','pattern-lite'):p.error('masking requires learner')
    if a.variant in ('crossover','random-donor','edit') and a.method not in ('cem','pattern-lite'):p.error('off-policy proposals only for elite learning')
    return a


if __name__=='__main__':run(parse_args())
