"""Independent terminal / exact-probability audits for the two supplementary tasks."""
import json,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
HERE=Path(__file__).resolve().parent

def p(s,w,width):
    x=np.eye(width,dtype=np.float32)[list(s)].reshape(-1)
    z=(x@w).astype(np.float64)
    q=np.exp(z-z.max());return q/q.sum()

def linear():
    from linear_certificate import N,ACTIONS,ROOT,HORIZON
    task=json.loads((HERE/'linear_task.json').read_text());goal=tuple(task['target'])
    dag=json.loads((HERE/'linear_dag.json').read_text())
    def word(s,x):return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(s))
    def move(v,a):
        i,j=ACTIONS[a];return v^(((v>>j)&1)<<i)
    def apply(seq):
        out=[]
        for x in range(1<<N):
            v=x
            for a in seq:v=move(v,a)
            out.append(v)
        return out
    target=[word(goal,x) for x in range(1<<N)]
    paths=[(ROOT,[])]
    for layer in dag:
        links={tuple(row['state']):row['links'] for row in layer}
        paths=[(tuple(dst),seq+[a]) for s,seq in paths for a,dst in links[s]]
    assert len(paths)==task['path_count']
    assert all(s==goal and apply(seq)==target for s,seq in paths)
    def exact(w):
        d={ROOT:1.}
        for layer in dag:
            n=defaultdict(float)
            for row in layer:
                s=tuple(row['state']);q=p(s,w,1<<N)
                for a,dst in row['links']:n[tuple(dst)]+=d[s]*q[a]
            d=n
        return d[goal]
    rows=[]
    for f in sorted((HERE/'linear_runs').glob('*.json')):
        r=json.loads(f.read_text());w=np.array(r['weights'],dtype=np.float32)
        init=np.random.default_rng(r['seed']).normal(0,.02,w.shape).astype(np.float32)
        result=dict(mode=r['mode'],switch=r['switch'],seed=r['seed'],initial_exact_probability=exact(init),final_exact_probability=exact(w),weights_unchanged=bool(np.array_equal(init,w)),final=r['records'][-1],first_root_win_batch=r['first_root_win_batch'])
        if result['final_exact_probability']>=.01:
            rng=np.random.default_rng(99400+r['seed']);hits=0;example=None
            for _ in range(512):
                truth=list(range(1<<N));seq=[]
                for _ in range(HORIZON):
                    # Recover matrix from independently simulated basis vectors.
                    s=tuple(sum(((truth[1<<j]>>i)&1)<<j for j in range(N)) for i in range(N))
                    a=int(rng.choice(len(ACTIONS),p=p(s,w,1<<N)));seq.append(a)
                    truth=[move(v,a) for v in truth]
                if truth==target:hits+=1;example=seq
            result.update(scalar_hits=hits,scalar_trials=512,verified_example=example)
        rows.append(result)
    (HERE/'linear_audit.json').write_text(json.dumps(rows,indent=2))
    print('linear paths',len(paths),'uniform',exact(np.zeros((160,20),dtype=np.float32)))
    for r in rows:print(r['mode'],r['switch'],r['seed'],r['final_exact_probability'],r.get('scalar_hits'))
def three():
    from three import rare_environment,WIDTH,ACTIONS,H
    sys.path.insert(0,str(HERE.parent/'reversible_initial'))
    from environment import gate_library,execute,verify
    t,x,root,goal,target=rare_environment()[0];lib=gate_library(3)
    d=np.full(len(t),-1);d[goal]=0;front=np.array([goal])
    for depth in range(1,H+1):
        front=np.unique(t[front].ravel());front=front[d[front]<0];d[front]=depth
    def state(i):return tuple(x[i].reshape(WIDTH,WIDTH).argmax(1))
    paths=[(root,[])]
    for depth in range(H,0,-1):paths=[(dst,seq+[a]) for s,seq in paths for a,dst in enumerate(t[s]) if d[dst]==depth-1]
    assert len(paths)==rare_environment()[1]
    assert all(s==goal and verify(3,tuple(target),[lib[a] for a in seq],H)['reward'] for s,seq in paths)
    def exact(w):
        total=0.
        for s,seq in paths:
            cur=root;prob=1.
            for a in seq:
                prob*=p(state(cur),w,WIDTH)[a];dst=t[cur,a]
                assert execute(3,[lib[a]],state(cur))==state(dst)
                cur=dst
            total+=prob
        return total
    rows=[]
    for f in sorted((HERE/'three_runs').glob('*.json')):
        r=json.loads(f.read_text());w=np.array(r['weights'],dtype=np.float32)
        init=np.random.default_rng(r['seed']).normal(0,.02,w.shape).astype(np.float32)
        result=dict(mode=r['mode'],switch=r['switch'],seed=r['seed'],initial_exact_probability=exact(init),final_exact_probability=exact(w),weights_unchanged=bool(np.array_equal(init,w)),final=r['records'][-1])
        assert np.isclose(result['final_exact_probability'],r['records'][-1]['root_probability'],rtol=1e-4,atol=0)
        rows.append(result)
    (HERE/'three_audit.json').write_text(json.dumps(rows,indent=2))
    print('three paths',len(paths))
if __name__=='__main__':
    linear()
    three()
