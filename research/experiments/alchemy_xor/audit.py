"""Independent Python checker for held-out traces and motif summaries."""
import csv
import hashlib
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from statistics import mean
P=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'results'
ROOT={1,2,4,8,16}
def decode(t):
    return {i for i in range(1,32) if t&(1<<i)}
def rank(s):
    b=[]
    for x in sorted(s,reverse=True):
        for y in b:x=min(x,x^y)
        if x:b.append(x);b.sort(reverse=True)
    return len(b)
def audit(path,tasks,expected):
    stats=defaultdict(list);seen=set()
    for i,j,t,ok,l,shared,cancel,trace in csv.reader(path.open()):
        i,j,t,ok,l,shared,cancel=map(int,(i,j,t,ok,l,shared,cancel));assert 384<=i<640 and 0<=j<8 and t==tasks[i] and (i,j) not in seen
        seen.add((i,j));target=decode(t);assert rank(target)==5
        avail=set(ROOT)
        expr={x: {b for b in range(32) if (x&b).bit_count()%2} for x in ROOT}
        anc={x:set() for x in ROOT};made=[]
        for gate in trace.rstrip(';').split(';') if trace else []:
            z,a,b=map(int,gate.split(':'));assert not target<=avail, 'did not stop at success'
            assert a in avail and b in avail and z not in avail and z
            avail.add(z);made.append(z)
            expr[z]=expr[a]^expr[b];assert expr[z]=={b for b in range(32) if (z&b).bit_count()%2}
            anc[z]={z}|anc[a]|anc[b]
        assert len(made)==l<=20 and ok==(target<=avail)
        assert ok or l==20
        sh=ca=0
        if ok:
            for z in set(made)-target:
                uses=[v for v in target if z in anc[v]]
                sh+=len(uses)>=2;ca+=any(z&~v for v in uses)
            assert (shared,cancel)==(sh,ca)
        else:assert (shared,cancel)==(0,0)
        stats['all'].append([ok,l,sh,ca])
        if ok:stats[str(l)].append([ok,l,sh,ca])
    assert len(seen)==2048
    r=stats.pop('all');wins=sum(x[0] for x in r);cost=mean(x[1] for x in r if x[0]);rew=mean(x[0]*(2-x[1]/20) for x in r)
    assert wins==expected['ok'] and abs(cost-expected['conditional_cost'])<1e-10 and abs(rew-expected['reward'])<1e-10
    return {'ok':wins,'cost':cost,'reward':rew,'shared':mean(x[2] for x in r if x[0]),'cancel':mean(x[3] for x in r if x[0]),'bins':{k:{'n':len(v),'shared':mean(x[2] for x in v),'cancel':mean(x[3] for x in v)} for k,v in stats.items()}}
def main():
    out={};alltasks=None
    for f in sorted(P.glob('seed-*.json')):
        data=json.loads(f.read_text());seed=data['seed'];tasks=list(map(int,(P/f'maps-{seed}.txt').read_text().splitlines()))
        assert len(tasks)==len(set(tasks))==640 and all(rank(decode(t))==5 for t in tasks)
        if alltasks is None:alltasks=tasks
        else:assert tasks==alltasks
        r={'common':audit(P/f'trace-{seed}-common.csv',tasks,data['common_heldout'])}
        for arm in data['arms']:
            k=arm['mode'];r[str(k)]=audit(P/f'trace-{seed}-{k}.csv',tasks,arm['heldout'])
        out[str(seed)]=r
    assert len(out)==4
    report={}
    for arm in ['common','0','1','2']:
        rr=[r[arm] for r in out.values() if arm in r]
        if rr:
            report[arm]={k:mean(r[k] for r in rr) for k in ('ok','cost','reward','shared','cancel')}
            bins=defaultdict(list)
            for r in rr:
                for k,v in r['bins'].items():bins[k].append(v)
            report[arm]['bins']={k:{'n':sum(x['n'] for x in v),'shared':sum(x['n']*x['shared'] for x in v)/sum(x['n'] for x in v),'cancel':sum(x['n']*x['cancel'] for x in v)/sum(x['n'] for x in v)} for k,v in sorted(bins.items(),key=lambda z:int(z[0]))}
    print(json.dumps({'summary':report,'seeds':out},indent=2))
if __name__=='__main__':main()
