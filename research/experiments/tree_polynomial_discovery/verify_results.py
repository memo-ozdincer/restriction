"""Independent exact tree witness replay and frozen-policy evaluation audit.

Does not import the training generator or its verifier. Every persisted graph
witness is independently decoded, scored and canonicalized; counters are checked
for consistency (not a proof of all unsaved proposals). The final frozen policy
batch can be reconstructed from parameter arrays and evaluation RNG state
schedule. Earlier checkpoints' parameters are not archived; their total counts
are checked, not regenerated. Run, e.g. python verify_results.py results/.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import gzip
import json
import math
from pathlib import Path
import sys

import numpy as np


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode(n, code):
    require(len(code) == n - 2 and all(type(v) is int and 0 <= v < n for v in code), 'invalid Prüfer sequence')
    adj = [[] for _ in range(n)]
    counts = Counter(code)
    active = set(range(n))
    for v in code:
        u = min(x for x in active if counts[x] == 0)
        adj[u].append(v)
        adj[v].append(u)
        active.remove(u)
        counts[v] -= 1
    require(len(active) == 2, 'invalid final Prüfer edge')
    u, v = sorted(active)
    adj[u].append(v)
    adj[v].append(u)
    return adj


def add(*polys):
    out = [0] * max(map(len, polys))
    for poly in polys:
        for i, x in enumerate(poly):
            out[i] += x
    return out


def mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    out[i+j] += x*y
    return out


def coefficients(adj, family):
    """Independent recursive tree DP. Domination counts mutually exclusive
    states by positive accumulation, rather than polynomial subtraction."""
    def independent(v, parent):
        chosen, excluded = [0, 1], [1]
        for w in adj[v]:
            if w != parent:
                c, e = independent(w, v)
                chosen = mul(chosen, e)
                excluded = mul(excluded, add(c, e))
        return chosen, excluded

    def domination(v, parent):
        chosen, internally_covered, needs_parent = [0, 1], [0], [1]
        for w in adj[v]:
            if w != parent:
                c, covered, need = domination(w, v)
                chosen = mul(chosen, add(c, covered, need))
                internally_covered = add(mul(internally_covered, add(c, covered)), mul(needs_parent, c))
                needs_parent = mul(needs_parent, covered)
        return chosen, internally_covered, needs_parent

    if family == 'independence':
        a = add(*independent(len(adj)-1, -1))
    else:
        require(family == 'domination', f'unknown polynomial family: {family}')
        c, covered, need = domination(len(adj)-1, -1)
        a = add(c, covered)
    require(all(x >= 0 for x in a), 'negative coefficient')
    return a + [0] * (len(adj)+1-len(a))


def canonical(adj):
    """Find centers via diameter, then choose lexical min rooted AHU string.
    This is equivalent to training's center convention, not its algorithm."""
    def traverse(source):
        parent = {source: None}
        distance = {source: 0}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in distance:
                    parent[v] = u
                    distance[v] = distance[u]+1
                    queue.append(v)
        require(len(distance) == len(adj), 'disconnected graph')
        return max(distance, key=distance.get), parent
    u, _ = traverse(0)
    v, prev = traverse(u)
    path = []
    while v is not None:
        path.append(v)
        v = prev[v]
    centers = path[(len(path)-1)//2:len(path)//2+1]
    def rooted(v, p):
        return '(' + ''.join(sorted(rooted(w,v) for w in adj[v] if w != p)) + ')'
    return min(rooted(v,-1) for v in centers)


def graph_record(code, config):
    adj = decode(config['n'], code)
    a = coefficients(adj, config['family'])
    support = [i for i, x in enumerate(a) if x > 0]
    interior = [i for i in range(1,len(a)-1) if min(a[i-1:i+2]) > 0]
    def defect(i):
        return a[i-1]*a[i+1]-a[i]*a[i]
    def normalized(i):
        return defect(i)/(a[i-1]*a[i+1]+a[i]*a[i])
    vs = [i for i in interior if defect(i) > 0]
    mode, index, required = config['score'], config['index'], config['required']
    hit = int(index in vs) if index is not None else int(len(vs)>=required)
    if mode == 'binary':
        score = hit
    elif index is not None:
        score = defect(index) if mode == 'raw' else normalized(index) if index in interior else -1.0
    elif len(interior) < required:
        score = -1 if mode == 'raw' else -1.0
    else:
        margins = [defect(i) if mode=='raw' else normalized(i) for i in interior]
        score = sorted(margins,reverse=True)[required-1]
    return {'id':canonical(adj),'violations':vs, 'defects':{str(i):str(defect(i)) for i in vs},
            'score':score,'hit':hit,'support':support,'support_endpoint':max(support) if config['family']=='independence' else min(support)}


def score_equal(x,y):
    if isinstance(x,int) and isinstance(y,int):
        return x==y
    return math.isclose(x,y,rel_tol=1e-14,abs_tol=1e-15)


def check_graph(saved, config, must_hit=False):
    verified = graph_record(saved['code'], config)
    if must_hit:
        require(verified['hit'] == 1, 'saved witness does not satisfy target')
    for key in ('id','violations','defects','support'):
        if key in saved:
            require(saved[key] == verified[key], f'graph {key} mismatch: {saved[key]} != {verified[key]}')
    if 'score' in saved:
        require(score_equal(saved['score'], verified['score']), f"score mismatch {saved['score']} != {verified['score']}")
    return verified


def registered_config(key, c, registered):
    if registered is None:
        return
    require(key in registered,f'unregistered result {key}')
    args = registered[key]
    require(len(args)%2==0,'unexpected argument schedule')
    for flag,value in zip(args[::2],args[1::2]):
        require(flag.startswith('--'),'malformed registration')
        name=flag[2:].replace('-','_')
        require(name in c,f'config absent: {name}')
        t=type(c[name])
        require(c[name]==t(value),f'config mismatch {name}: {c[name]} versus {value}')
    if '--index' not in args:
        require(c['index'] is None,'unregistered fixed index')
    defaults={'elite_frac':.1,'lr':.03,**({'augmentation_frac':.25,'archive_size':1024} if 'method' in c else {'variant':'ordinary','order':'random','ties':'random','max_attempts':None,'stop_on_hit':False,'frozen_policy':None})}
    for name,v in defaults.items():
        if '--'+name.replace('_','-') not in args:
            require(c[name]==v,f'unregistered default changed {name}')


def verify_counters(data):
    c, t, e, ctr, history, policy = (data[k] for k in ('config','train','evaluation','counters','history','policy'))
    n, b, steps, method, variant = (c[x] for x in ('n','batch','steps','method','variant'))
    require(n>=3 and b>=2 and steps>=1 and c['required']>=1, 'invalid config sizes')
    require(c['family'] in ('independence','domination') and c['score'] in ('raw','normalized','binary'),'invalid config objective')
    require(c['index'] is None or 0<c['index']<n and c['required']==1, 'invalid target')
    require(method in ('random','hill','anneal','pg','cem','pattern-lite'),'unknown method')
    require(ctr['steps']==steps==len(history),'incorrect step count')
    factor = 1+c['local_steps'] if method=='pattern-lite' else 1
    expected_calls = steps*b*factor + (b if method in ('hill','anneal') else 0)
    require(t['calls']==expected_calls,'incorrect training call count')
    require(0<=t['unique_successes']<=t['unique_sampled']<=t['calls'],'invalid unique train counts')
    require(t['unique_successes']<=t['successes']<=t['calls'],'invalid train success counts')
    require((t['first_hit'] is not None)==bool(t['successes']),'first-hit inconsistency')
    if t['first_hit'] is not None: require(1<=t['first_hit']<=t['calls'],'first hit outside budget')
    require(0<=ctr['updates']<=steps and ctr['updates']==policy['updates'],'incorrect update count')
    require(0<=ctr['mixed_binary_groups']<=steps and 0<=ctr['nonconstant_score_groups']<=steps,'incorrect mixed/nonconstant count')
    warnings=[]
    if ctr['updates']>ctr['nonconstant_score_groups']:
        excess=ctr['updates']-ctr['nonconstant_score_groups']
        # Submitted PG normalizer calls np.std on a constant floating array.
        # Mean roundoff may produce nonzero std and equal, spurious weights.
        # These specific archived runs updated every step; each excess update
        # is independently witnessed by a history batch of one isomorphism
        # class, which necessarily shares an identical score.
        constant_batches=[h for h in history if h['unique']==1]
        require(method=='pg' and c['score']=='normalized' and ctr['updates']==steps and len(constant_batches)==excess,
                'unexplained update despite constant objective')
        reproduced=0
        for h in constant_batches:
            z=np.full(b,float(h['best_score'])); std=z.std()
            reproduced+=int(bool(std) and bool(np.all((z-z.mean())/(std*b)!=0)))
        warnings.append({'code':'PG_CONSTANT_NORMALIZATION_ROUNDOFF','constant_updates':excess,
                         'reproduced_local_numpy':reproduced,'message':'Archived constant objective groups caused nonzero PG weights; causal training comparison confounded. No changes made to submitted snapshot.'})
    if c['score']=='binary':
        require(ctr['updates']<=ctr['mixed_binary_groups'],'binary update despite no mixed successes')
        require(ctr['nonconstant_score_groups']==ctr['mixed_binary_groups'],'binary signal counts disagree')
    if method not in ('pg','cem','pattern-lite'):
        require(ctr['updates']==ctr['blocked_samples']==0,'search unexpectedly trained')
    if variant not in ('balanced','matched'):
        require(ctr['blocked_samples']==0,'unexpected blocked examples')
    if variant in ('crossover','random-donor','edit'):
        require(ctr['augmented_proposals']==steps*int(b*c['augmentation_frac']),'wrong augmented proposal count')
    else:
        require(ctr['augmented_proposals']==0,'unexpected augmented proposal count')
    if method in ('hill','anneal'):
        require(ctr['edge_edit_count']==steps*b,'wrong search primitive edit count')
    if method=='pattern-lite' and variant not in ('crossover','random-donor','edit'):
        require(ctr['edge_edit_count']==steps*b*c['local_steps'],'wrong local primitive edit count')
    previous={'training_calls':0,'hits_total':0,'unique_hits_total':0,'updates_total':0,'blocked_total':0}
    for i,h in enumerate(history,1):
        calls=i*b*factor+(b if method in ('hill','anneal') else 0)
        require(h['step']==i and h['training_calls']==calls,'history call schedule mismatch')
        require(0<=h['successes']<=b and 1<=h['unique']<=b and 1<=h['largest_family']<=b,'invalid batch summary')
        for field in previous:
            require(h[field]>=previous[field],f'nonmonotonic history {field}')
        require(h['unique_hits_total']<=h['hits_total']<=calls,'invalid history success counts')
        require(h['updates_total']-previous['updates_total'] in (0,1),'invalid per-step update count')
        require(h['blocked_total']-previous['blocked_total']<=b,'too many blocked replay samples')
        if method in ('pg','cem','random'):
            require(h['hits_total']-previous['hits_total']==h['successes'],'history train success accounting mismatch')
        else:
            require(h['hits_total']-previous['hits_total']>=h['successes'],'history accepted/proposed successes exceed all evaluated successes')
        previous={k:h[k] for k in previous}
    for field,key in [('training_calls','calls'),('hits_total','successes'),('unique_hits_total','unique_successes')]:
        require(previous[field]==t[key],f'final history mismatch {field}')
    require(previous['updates_total']==ctr['updates'] and previous['blocked_total']==ctr['blocked_samples'],'final history intervention counts mismatch')
    schedule=([0]+[i for i in range(1,steps+1) if i%c['eval_every']==0 or i==steps]) if c['eval_batch'] else []
    cps=e['checkpoints']
    require([h['step'] for h in cps]==schedule,'evaluation checkpoint schedule mismatch')
    require(e['calls']==len(cps)*c['eval_batch'],'wrong eval total calls')
    require(e['successes']==sum(h['successes'] for h in cps),'wrong eval successes sum')
    require(0<=e['unique_successes']<=e['successes']<=e['calls'],'invalid eval counts')
    for i,h in enumerate(cps,1):
        require(h['evaluation_calls']==i*c['eval_batch'],'wrong eval checkpoint calls')
        require(h['training_calls']==(history[h['step']-1]['training_calls'] if h['step'] else 0),'wrong eval training checkpoint calls')
        require(0<=h['successes']<=c['eval_batch'] and 1<=h['unique']<=c['eval_batch'] and 1<=h['largest_family']<=c['eval_batch'],'wrong eval batch counts')
    params=[np.asarray(p,dtype=np.float64) for p in policy['params']]
    require([x.shape for x in params]==[(n-2,n),(n+1,n),(n,)],'invalid frozen policy parameter shapes')
    require(all(np.all(np.isfinite(x)) and np.all(np.abs(x)<=12) for x in params),'nonfinite/out-of-bounds frozen params')
    if not policy['updates']:
        require(all(not np.any(x) for x in params),'frozen params changed without updates')
    return params,warnings


def verify_cycle_counters(data):
    """Check cycle-panel variable search episode budgets and native eval counts."""
    c,t,e,search,history,policy=(data[k] for k in ('config','train','evaluation','search','history','policy'))
    n,b=c['n'],c['batch']; query_budget=c['queries']
    require(n>=3 and b>=1 and query_budget>=1 and c['required']>=1,'invalid cycle config')
    require(c['family'] in ('independence','domination') and c['score'] in ('raw','normalized','binary'),'invalid cycle objective')
    require(c['index'] is None or 0<c['index']<n and c['required']==1,'invalid cycle target')
    require(c['strategy'] in ('cycle','single') and c['starts'] in ('uniform','cem','frozen'),'invalid cycle variant')
    require(t['calls']==query_budget and history,'cycle train budget mismatch')
    require(0<=t['unique_successes']<=t['unique_sampled']<=t['calls'],'invalid cycle unique train counts')
    require(t['unique_successes']<=t['successes']<=t['calls'],'invalid cycle train success counts')
    require((t['first_hit'] is not None)==bool(t['successes']),'cycle first-hit inconsistency')
    if t['first_hit'] is not None: require(1<=t['first_hit']<=t['calls'],'cycle first hit outside budget')
    require(search['policy_updates']==policy['updates'],'cycle policy update mismatch')
    require(0<=search['accepted_swaps']<=search['attempted_insertions']<=t['calls']-search['episodes'],'cycle insertions/swaps inconsistent')
    require(0<=search['accepted_swaps']<=search['episodes']*c['max_swaps'],'cycle max swap bound exceeded')
    require(0<=search['unique_initial']<=search['episodes'] and 0<=search['unique_final']<=search['episodes'],'invalid cycle unique episodes')
    require(0<=search['initial_successes']<=search['episodes'] and 0<=search['final_successes']<=search['episodes'],'invalid cycle episode successes')
    if c['starts']!='cem':require(search['policy_updates']==search['blocked']==0,'non-CEM search unexpectedly trained')
    if c['variant']=='ordinary':require(search['blocked']==0,'ordinary cycle blocked samples')
    fields=('episodes','calls','hits_total','accepts_total','attempts_total','updates_total')
    previous={k:0 for k in fields}; init_hits=final_hits=0
    for batch,h in enumerate(history,1):
        require(h['batch']==batch,'cycle batch order')
        for k in fields:require(h[k]>=previous[k],f'cycle nonmonotonic {k}')
        d={k:h[k]-previous[k] for k in fields};previous={k:h[k] for k in fields}
        require(1<=d['episodes']<=b and d['calls']==h['batch_calls']>=d['episodes'],'invalid cycle batch budget')
        if c['per_start_queries'] is not None:require(d['calls']<=d['episodes']*c['per_start_queries'],'cycle per-start budget exceeded')
        require(0<=d['accepts_total']<=d['attempts_total']<=d['calls']-d['episodes'],'cycle batch edit accounting')
        require(d['updates_total'] in (0,1) and 0<=d['hits_total']<=d['calls'],'cycle batch update/hit accounting')
        for k in ('initial','final'):
            x=h[k]; require(0<=x['successes']<=d['episodes'] and 1<=x['unique']<=d['episodes'] and 1<=x['largest_family']<=d['episodes'],'cycle batch summary bounds')
            require(x['successes']<=d['hits_total'],'cycle endpoint wins exceed evaluated wins')
        init_hits+=h['initial']['successes'];final_hits+=h['final']['successes']
    for field,key in [('episodes','episodes'),('accepts_total','accepted_swaps'),('attempts_total','attempted_insertions'),('updates_total','policy_updates')]:
        require(previous[field]==search[key],f'cycle final history mismatch {field}')
    require(previous['calls']==t['calls'] and previous['hits_total']==t['successes'],'cycle final calls/hits mismatch')
    require(init_hits==search['initial_successes'] and final_hits==search['final_successes'],'cycle endpoint success sums differ')
    schedule=([0]+[i for i in range(1,len(history)+1) if i%c['eval_every']==0 or i==len(history)]) if c['eval_batch'] else []
    cps=e['checkpoints']
    require([x['batch'] for x in cps]==schedule and e['calls']==len(cps)*c['eval_batch'],'cycle evaluation schedule mismatch')
    require(e['successes']==sum(x['successes'] for x in cps) and 0<=e['unique_successes']<=e['successes']<=e['calls'],'cycle evaluation success counts')
    for j,x in enumerate(cps,1):
        require(x['evaluation_calls']==j*c['eval_batch'],'cycle eval call schedule mismatch')
        require(x['training_calls']==(history[x['batch']-1]['calls'] if x['batch'] else 0),'cycle train checkpoint calls')
        require(0<=x['successes']<=c['eval_batch'] and 1<=x['unique']<=c['eval_batch'] and 1<=x['largest_family']<=c['eval_batch'],'cycle eval batch counts')
    params=[np.asarray(p,dtype=np.float64) for p in policy['params']]
    require([x.shape for x in params]==[(n-2,n),(n+1,n),(n,)],'cycle policy param shapes')
    require(all(np.all(np.isfinite(x)) and np.all(np.abs(x)<=12) for x in params),'cycle nonfinite/out-of-bounds params')
    if c['starts']!='frozen' and not policy['updates']:require(all(not np.any(x) for x in params),'cycle frozen params changed without updates')
    return params,[]


def replay_final(data, params):
    c=data['config']; cps=data['evaluation']['checkpoints']
    if not cps:
        return {'status':'no evaluation'}
    n,b=c['n'],c['eval_batch']
    rng=np.random.default_rng(c['seed']+10_000_019)
    learned=(c['method'] in ('pg','cem','pattern-lite')) if 'method' in c else c['starts']!='uniform'
    if not learned:
        for _ in cps:
            codes=rng.integers(n,size=(b,n-2))
    else:
        # Every earlier checkpoint consumes exactly b*(n-2) uniform draws;
        # no dependence on its unavailable policy parameters.
        for _ in cps[:-1]:
            rng.random(b*(n-2))
        codes=np.empty((b,n-2),dtype=np.int64)
        counts=np.zeros((b,n),dtype=np.int64)
        prev=np.full(b,n,dtype=np.int64)
        rows=np.arange(b)
        for pos in range(n-2):
            z=params[0][pos]+params[1][prev]+params[2][counts]
            p=np.exp(z-z.max(axis=1,keepdims=True));p/=p.sum(axis=1,keepdims=True)
            q=(np.cumsum(p,axis=1)<rng.random(b)[:,None]).sum(axis=1)
            q=np.minimum(q,n-1);codes[:,pos]=q
            counts[rows,q]+=1;prev=q
    records=[graph_record(list(map(int,code)),c) for code in codes]
    modes=Counter(r['id'] for r in records)
    actual={'successes':sum(r['hit'] for r in records),'unique':len(modes),'largest_family':max(modes.values()),
            'best_score':max(r['score'] for r in records),'max_violations':max(len(r['violations']) for r in records),
            'mean_support_endpoint':sum(r['support_endpoint'] for r in records)/b}
    wanted={k:cps[-1][k] for k in actual}
    mismatches=[k for k,v in actual.items() if not score_equal(v,wanted[k])]
    return {'status':'match' if not mismatches else 'mismatch','actual':actual,'archived':wanted,'mismatched_fields':mismatches}


def verify_one(path, registered=None, summary=None, replay=True):
    op=gzip.open if path.suffix=='.gz' else open
    with op(path,'rt') as handle:data=json.load(handle)
    key=path.name.removesuffix('.gz').removesuffix('.json')
    c,t,e=data['config'],data['train'],data['evaluation']
    registered_config(key,c,registered)
    params,warnings=(verify_cycle_counters(data) if 'search' in data else verify_counters(data))
    if summary is not None:
        require(key in summary,'result absent from panel summary')
        s=summary[key]
        require(s['config']==c and s['train']=={k:v for k,v in t.items() if k!='witnesses'} and all(s[k]==data[k] for k in ('search','counters') if k in data),'panel summary mismatch')
        require(s['final']==e['checkpoints'][-1],'panel final mismatch')
    count=0
    for group in (t,e):
        witnesses=group['witnesses']
        require(len(witnesses)==min(128,group['unique_successes']),'incorrect saved witness count')
        ids=set()
        for saved in witnesses:
            r=check_graph(saved,c,must_hit=True)
            require(r['id'] not in ids,'duplicate saved witness canonical ID')
            ids.add(r['id']);count+=1
    b=check_graph(t['best'],c);count+=1
    require(1<=t['best']['call']<=t['calls'],'best result outside budget')
    require(t['max_violations']>=len(b['violations']),'best solution exceeds max violation count')
    if t['max_violations']:
        r=check_graph(t['max_violation_example'],c);count+=1
        require(len(r['violations'])==t['max_violations'],'max-violation example does not attain max')
    else:
        require(t['max_violation_example'] is None,'unexpected max-violation witness')
    return {'key':key,'graph_records_verified':count,'train_calls_checked':t['calls'],'eval_calls_checked':e['calls'],
            'warnings':warnings, 'frozen_replay':replay_final(data,params) if replay else {'status':'skipped'}}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    p.add_argument('--output',type=Path,default=None)
    p.add_argument('--no-replay',action='store_true')
    p.add_argument('--strict-replay',action='store_true')
    a=p.parse_args(argv)
    d=a.directory
    reg=d/'registered_specs.json'; sm=d/'summary.json'
    registered={row[0]:row[1] for row in json.loads(reg.read_text())} if reg.exists() else None
    panel=json.loads(sm.read_text()) if sm.exists() else None
    summary={r['key']:r for r in panel['runs']} if panel is not None else None
    paths=sorted(d.glob('*.json.gz'))
    if not paths:
        paths=sorted(p for p in d.glob('*.json') if p.name not in ('summary.json','registered_specs.json','verification.json'))
    require(bool(paths),'no result files')
    keys={p.name.removesuffix('.gz').removesuffix('.json') for p in paths}
    if registered is not None:
        require(keys==set(registered),'registered result file set differs')
    if summary is not None:
        require(keys==set(summary) and not panel['failed'],'panel summary incomplete/failed')
    records=[];failures=[]
    for path in paths:
        try:
            row=verify_one(path,registered,summary,replay=not a.no_replay)
            records.append(row)
            print(row['key'], row['graph_records_verified'],row['frozen_replay']['status'],flush=True)
        except Exception as exc:
            failures.append({'key':path.name,'error':repr(exc)})
            print('FAILED',path.name,repr(exc),file=sys.stderr,flush=True)
    status=Counter(r['frozen_replay']['status'] for r in records)
    result={'verified_runs':len(records),'failures':failures,'graph_records_verified':sum(r['graph_records_verified'] for r in records),
            'train_calls_checked':sum(r['train_calls_checked'] for r in records),'eval_calls_checked':sum(r['eval_calls_checked'] for r in records),
            'frozen_replay_status':dict(status),'warnings_total':sum(len(r['warnings']) for r in records), 'constant_pg_updates':sum(w['constant_updates'] for r in records for w in r['warnings'] if w['code']=='PG_CONSTANT_NORMALIZATION_ROUNDOFF'),'runs':records,
            'limitations':'Counters checked for consistency; unsaved training proposals and earlier checkpoint evaluation batches not independently replayable.'}
    output=a.output or d/'verification.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='runs'}),flush=True)
    return int(bool(failures) or a.strict_replay and status['mismatch']>0)


if __name__=='__main__':sys.exit(main())
