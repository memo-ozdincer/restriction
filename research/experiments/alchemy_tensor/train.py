import argparse,json,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from itertools import combinations,product
import numpy as np
from native_environment import TERMS,TERM_IDS,tensor_value,tensor_neighbors
H=8
GROUPS=4
GROUP=16
PRE=400
POST=400
CAP=5
HIDDEN=32
EVAL=64
MODES=('ordinary','nonshortening','unrestricted')
def make_graph():
    roots=list(combinations([TERM_IDS[t] for t in product((1,2),repeat=3)],4))
    order=np.random.default_rng(20261127).permutation(len(roots))
    split={k:np.array([roots[i] for i in ids]) for k,ids in
           [('train',order[:48]),('validation',order[48:56]),('test',order[56:])]}
    states=list(roots);idx={s:i for i,s in enumerate(states)};rows=[]
    for state in states:
        to=[state]+tensor_neighbors(state,CAP)
        assert all(tensor_value(s)==tensor_value(state) for s in to)
        row=[]
        for s in to:
            if s not in idx:
                idx[s]=len(states);states.append(s)
            row.append(idx[s])
        rows.append(row)
    trans=np.full((len(states),max(map(len,rows))),-1,dtype=np.int32)
    for i,row in enumerate(rows):trans[i,:len(row)]=row
    features=np.zeros((len(states),len(TERMS)),np.float32)
    for i,s in enumerate(states):features[i,list(s)]=1
    ranks=features.sum(1).astype(int)
    ids={k:np.array([idx[tuple(s)] for s in v]) for k,v in split.items()}
    return states,trans,features,ranks,ids
ENV=None
def init(env):global ENV;ENV=env

def weights(rng):
    return dict(W1=rng.normal(0,.1,(27,HIDDEN)).astype(np.float32),
                b1=np.zeros(HIDDEN,np.float32),W2=rng.normal(0,.1,(HIDDEN,27)).astype(np.float32),
                b2=np.zeros(27,np.float32))

def choose(p,rng,valid):
    i=(rng.random(len(p))[:,None]>=np.cumsum(p,1)).sum(1)
    return np.minimum(i,valid.sum(1)-1)

def rollout(w,starts,mode,rng,grad=False,replay=False):
    states,trans,f,ranks,_=ENV
    pos=starts.copy();history=[];trace=[pos.copy()]
    reset=policy=candidates=reset_cand=0
    for t in range(H):
        dest=trans[pos];valid=dest>=0;safe=np.maximum(dest,0)
        if mode!='ordinary' and t<2:
            reset+=len(pos);reset_cand+=int(valid.sum())
            if mode=='nonshortening':valid &= ranks[safe]>=4
            # noncontiguous mask: sample via cumulative probability then clip to last valid.
            pr=valid/valid.sum(1,keepdims=True)
            i=(rng.random(len(pos))[:,None]>=np.cumsum(pr,1)).sum(1)
            i=np.minimum(i,np.where(valid,np.arange(valid.shape[1]),-1).max(1))
        else:
            policy+=len(pos);candidates+=int(valid.sum())
            x=f[pos];h=np.tanh(x@w['W1']+w['b1']);q=h@w['W2']+w['b2']
            z=f[safe];logits=np.einsum('bd,bad->ba',q,z,optimize=False)
            logits=np.where(valid,logits,-1e30);logits-=logits.max(1,keepdims=True)
            pr=np.exp(logits);pr/=pr.sum(1,keepdims=True)
            i=choose(pr,rng,valid)
            if grad:history.append((x,h,z,pr,i))
        pos=dest[np.arange(len(pos)),i]
        assert np.all(pos>=0)
        trace.append(pos.copy())
    score=ranks[pos];reward=1-score/6
    records=dict(rank=float(score.mean()),savings=float((4-score).mean()),improved=float((score<4).mean()),rank_counts=np.bincount(score,minlength=6).tolist(),
                 policy=policy,reset=reset,candidates=candidates,reset_candidates=reset_cand,prefix_rank=float(ranks[trace[2]].mean()))
    if replay:
        for path in zip(*trace):
            target=scalar_tensor(states[path[0]])
            for a,b in zip(path,path[1:]):
                assert b in trans[a] and scalar_tensor(states[b])==target
        seq=ranks[np.array(trace)]
        expands=(np.diff(seq,axis=0)>0).any(0)
        improved=score<4
        records.update(expanded=float(expands.mean()),expanded_and_improved=float((expands&improved).mean()),
                       expanded_by_rank=[int((expands&(score==k)).sum()) for k in range(6)],
                       total=int(len(pos)))
        examples={}
        for k in range(len(pos)):
            if expands[k] and improved[k]:
                key=int(starts[k])
                if key not in examples and len(examples)<5:
                    examples[key]=[states[int(p[k])] for p in trace]
        records['verified_expansion_examples']=examples
    if not grad:return records
    adv=(reward.reshape(-1,GROUP)-reward.reshape(-1,GROUP).mean(1,keepdims=True)).ravel().astype(np.float32)/len(pos)
    g={k:np.zeros_like(a) for k,a in w.items()}
    for x,h,z,pr,i in history:
        sc=-pr;sc[np.arange(len(pos)),i]+=1;sc*=adv[:,None]
        dq=np.einsum('ba,bad->bd',sc,z,optimize=False)
        g['W2']+=h.T@dq;g['b2']+=dq.sum(0)
        dh=(dq@w['W2'].T)*(1-h*h)
        g['W1']+=x.T@dh;g['b1']+=dh.sum(0)
    return records,g

def scalar_tensor(state):
    bits=[]
    for i,j,k in product(range(2),repeat=3):
        bits.append(sum(((TERMS[t][0]>>i)&1)*((TERMS[t][1]>>j)&1)*((TERMS[t][2]>>k)&1) for t in state)%2)
    return tuple(bits)

def evaluate(w,split,seed):
    return rollout(w,np.repeat(ENV[4][split],EVAL),'ordinary',np.random.default_rng(seed),False,True)

def optimize(w,m,v,step,mode,rng,iters):
    logs=[]
    for j in range(iters):
        t=step+j+1
        starts=np.repeat(rng.choice(ENV[4]['train'],GROUPS),GROUP)
        rec,g=rollout(w,starts,mode,rng,True)
        for k in w:
            m[k]=.9*m[k]+.1*g[k];v[k]=.999*v[k]+.001*g[k]**2
            w[k]+=.003*(m[k]/(1-.9**t))/(np.sqrt(v[k]/(1-.999**t))+1e-8)
        logs.append(rec)
    return logs

def run(job):
    seed,pre,post=job
    rng=np.random.default_rng(seed);w=weights(rng);m={k:np.zeros_like(a) for k,a in w.items()};v={k:np.zeros_like(a) for k,a in w.items()}
    before=evaluate(w,'validation',seed+10_000)
    logs=optimize(w,m,v,0,'ordinary',rng,pre)
    common=evaluate(w,'validation',seed+10_000)
    test_common=evaluate(w,'test',seed+20_000)
    qualified=common['savings']>.5
    allres=[]
    common_weights={k:a.tolist() for k,a in w.items()}
    for mode in MODES:
        ws,ms,vs=[{k:a.copy() for k,a in d.items()} for d in (w,m,v)]
        logs2=optimize(ws,ms,vs,pre,mode,np.random.default_rng(seed+30_000),post)
        test=evaluate(ws,'test',seed+20_000)
        val=evaluate(ws,'validation',seed+10_000)
        allres.append(dict(mode=mode,test=test,validation=val,train=logs2,weights={k:a.tolist() for k,a in ws.items()}))
    return dict(seed=seed,qualified=qualified,before=before,common=common,test_common=test_common,pretrain=logs,common_weights=common_weights,arms=allres)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--workers',type=int,default=4);ap.add_argument('--smoke',action='store_true');args=ap.parse_args()
    global PRE,POST
    if args.smoke:PRE=POST=2
    env=make_graph();init(env); print('states',len(env[0]),'degree',env[1].shape[1],flush=True)
    seeds=[42] if args.smoke else [42,43,44,45]
    begin=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers,initializer=init,initargs=(env,)) as pool:
        results=list(pool.map(run,[(s,PRE,POST) for s in seeds]))
    args.out.write_text(json.dumps(dict(config=dict(seeds=seeds,pre=PRE,post=POST,horizon=H,group=GROUP,groups=GROUPS,eval=EVAL,states=len(env[0]),degree=env[1].shape[1],splits={k:[tensor_value(env[0][i]) for i in a] for k,a in env[4].items()}),results=results,seconds=time.monotonic()-begin),indent=2))
    print([(r['seed'],r['qualified'],r['common']['savings'],[(a['mode'],a['test']['savings']) for a in r['arms']]) for r in results],flush=True)
if __name__=='__main__':main()
