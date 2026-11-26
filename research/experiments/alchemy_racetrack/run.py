"""Small exact original racetrack, paired post-competence evolution."""
import argparse,json,itertools,time
from pathlib import Path
import multiprocessing as mp
import numpy as np
W,H,SPEED,T=24,15,3,50
A=np.array(list(itertools.product((-1,0,1),repeat=2)))
POP,EP,HIDDEN=24,12,12
DIM=8
PARAM=(DIM+1)*HIDDEN+(HIDDEN+1)*9
SEEDS=range(42,46)
GAPS=np.random.default_rng(20261127).permutation(np.arange(1,9))
TRAIN=GAPS[:4];TEST=GAPS[4:]
ST=np.array(list(itertools.product(range(W),range(H),range(-SPEED,SPEED+1),range(-SPEED,SPEED+1))))
def encode(x,y,vx,vy):return (((x*H+y)*7+vx+3)*7+vy+3)
ROOT=encode(1,7,0,0)
GOAL=ST[:,0]==W-1

def build():
    trans=np.empty((8,len(ST),9),np.int32);coll=np.zeros_like(trans,dtype=bool)
    feat=np.empty((8,len(ST),DIM))
    x,y,vx,vy=ST.T
    for gap in range(1,9):
        feat[gap-1]=np.column_stack((x/(W-1),y/(H-1),vx/3,vy/3,
                    (gap+2.5-y)/H,np.full(len(x),(gap+2.5)/H),(12-x)/W,np.ones(len(x))))
        for a,(ax,ay) in enumerate(A):
            u=np.clip(vx+ax,-3,3);v=np.clip(vy+ay,-3,3)
            bad=np.zeros(len(x),bool);nx=x.copy();ny=y.copy()
            for i in range(1,4):
                xx=x+np.rint(u*i/3).astype(int);yy=y+np.rint(v*i/3).astype(int)
                bad|=(xx<0)|(xx>=W)|(yy<0)|(yy>=H)|((xx==12)&((yy<gap)|(yy>=gap+6)))
                nx,ny=xx,yy
            valid=~bad
            dest=encode(np.where(valid,nx,x),np.where(valid,ny,y),np.where(valid,u,0),np.where(valid,v,0))
            trans[gap-1,:,a]=np.where(GOAL,np.arange(len(x)),dest)
            coll[gap-1,:,a]=bad&~GOAL
    return trans,coll,feat
ENV=None
def initialize():global ENV;ENV=build()
def stream(seed,key,g=0):return np.random.default_rng([seed,key,g])
def policy(w,f,noise,clock):
    f=f.copy();f[...,7]=1-clock/T
    h=np.tanh(np.einsum('pnd,pdh->pnh',f,w[:,: (DIM+1)*HIDDEN].reshape(len(w),DIM+1,HIDDEN)[:,:DIM])+
               w[:,: (DIM+1)*HIDDEN].reshape(len(w),DIM+1,HIDDEN)[:,None,DIM])
    o=w[:,(DIM+1)*HIDDEN:].reshape(len(w),HIDDEN+1,9)
    return np.argmax(np.einsum('pnh,pha->pna',h,o[:,:HIDDEN])+o[:,None,HIDDEN]+noise,axis=-1)
def reset(mode,maps,length,rng,common):
    tr,cl,feat=ENV; s=np.full(len(maps),ROOT,dtype=int)
    for t in range(int(length.max())):
        if mode=='random':a=rng.integers(0,9,len(maps))
        else:a=policy(common[None],feat[maps,s][None],rng.normal(0,.4,(1,len(maps),9)),t)[0]
        q=tr[maps,s,a]
        s=np.where(t<length,q,s)
    assert not GOAL[s].any(), 'prefix too short to finish'
    return s

def simulate(w,maps,states,elapsed,noise,trace=False):
    tr,co,feat=ENV; p,n=len(w),len(maps)
    s=np.tile(states,(p,1)); clock=np.tile(elapsed,(p,1)); hit=np.full((p,n),T+1,int);collision=np.zeros_like(hit);cross=np.full_like(hit,-1);moves=0
    path=[]
    for i in range(T):
        alive=(clock<T)&(hit>T)
        if not alive.any():break
        a=policy(w,feat[maps[None],s],noise[i][None],clock)
        q=tr[maps[None],s,a];collision+=alive&co[maps[None],s,a];moves+=int(alive.sum())
        new=alive&(ST[s,0]<12)&(ST[q,0]>=12)&(cross<0)
        cross[new]=np.abs(ST[q[new],2])+np.abs(ST[q[new],3])
        s=np.where(alive,q,s);clock+=alive
        hit=np.where(alive&GOAL[s],clock,hit)
        if trace:path.append(s.copy().tolist())
    score=np.where(hit<=T,1+(T-hit)/T,0.)
    return score,hit,collision,cross,moves,path

def eval_policy(w,gaps,seed,key):
    maps=np.repeat(gaps-1,64);rng=stream(seed,key)
    noise=rng.normal(0,.4,(T,len(maps),9));out=simulate(w[None],maps,np.full(len(maps),ROOT),np.zeros(len(maps),int),noise,True)
    score,hit,col,cross,moves,path=out;ok=hit[0]<=T
    return dict(hit_rate=float(ok.mean()),score=float(score.mean()),finish_times=hit[0].tolist(),
                success_time=float(hit[0,ok].mean()) if ok.any() else None,collisions=col[0].tolist(),cross_speed=cross[0].tolist(),
                maps=maps.tolist(),path=path)

def step(pop,seed,g,mode,common):
    rng=stream(seed,2,g);maps=np.resize(TRAIN-1,EP);rng.shuffle(maps)
    length=rng.integers(1,9,EP) if mode!='ordinary' else np.zeros(EP,int)
    states=reset(mode,maps,length,rng,common) if mode!='ordinary' else np.full(EP,ROOT)
    noise=stream(seed,3,g).normal(0,.4,(T,EP,9))
    scores,hit,col,cross,moves,_=simulate(pop,maps,states,length,noise)
    rng=stream(seed,4,g);order=np.lexsort((rng.random(POP),-scores.mean(1)))
    champ=pop[order[0]].copy();parents=pop[rng.choice(order[:4],POP-1)]
    return np.vstack((champ,parents+rng.normal(0,.15,parents.shape))),champ,dict(
        train_score=float(scores.mean()),train_success=float((hit<=T).mean()),moves=moves,
        prefix_actual=int(length.sum()),prefix_conceptual=int(length.sum()*POP),
        padded_slots=POP*EP*T)

def run(seed):
    pop=stream(seed,1).normal(0,.5,(POP,PARAM));history=[];begin=time.monotonic();champ=pop[0]
    milestone=None
    for g in range(300):
        pop,champ,row=step(pop,seed,g,'ordinary',None)
        if (g+1)%50==0:
            e=eval_policy(champ,TRAIN,seed,100+g);history.append(dict(gen=g+1,success=e['hit_rate'],score=e['score']))
            if e['hit_rate']>=.9:
                milestone=g+1;break
    result=dict(seed=seed,milestone=milestone,common_history=history,baseline=eval_policy(champ,TEST,seed,999),arms={})
    if milestone is not None:
        for mode in ('ordinary','random','policy'):
            pop2=pop.copy();champ2=champ.copy();records=[]
            for j in range(200):
                pop2,champ2,row=step(pop2,seed,milestone+j,mode if j<100 else 'ordinary',champ)
                records.append(row)
                if j==99:mid=eval_policy(champ2,TEST,seed,999)
            result['arms'][mode]=dict(mid=mid,final=eval_policy(champ2,TEST,seed,999),weights=champ2.tolist(),training=records)
    result['seconds']=time.monotonic()-begin
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--workers',type=int,default=4);a=a.parse_args()
    rows=[]
    with mp.Pool(a.workers,initializer=initialize) as p:
        for r in p.imap_unordered(run,SEEDS):
            rows.append(r);a.out.write_text(json.dumps(dict(train=TRAIN.tolist(),test=TEST.tolist(),rows=rows)))
            print(r['seed'],r['milestone'],r['baseline']['score'],{m:x['final']['score'] for m,x in r['arms'].items()},flush=True)
