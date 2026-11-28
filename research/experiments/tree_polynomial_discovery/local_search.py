"""Exact cycle-deletion local search and a small local/global comparator.

Hypothesis: failure of one random edge-swap at a time may reflect incomplete
local search; examining all deletions after a native random nonedge insertion
could recover gradient-bearing mathematical objects. Compare at matched exact
verifier calls, not number of attempted insertions. No witness is used in
search or training. The search is adapted from Ramos & Sun §3.2
(https://arxiv.org/html/2510.18826), not byte-for-byte source reproduction.
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import numpy as np
from environment import prufer_to_edges, edges_to_prufer
from train import Policy, Evaluator, cem_weights, summary_batch


def norm_edge(a,b):
    return (min(a,b),max(a,b))


def tree_path(n,edges,a,b):
    """Unique path edges from a to b in a valid tree."""
    adj=[[] for _ in range(n)]
    for x,y in edges:
        adj[x].append(y);adj[y].append(x)
    parent={a:a};stack=[a]
    while b not in parent:
        x=stack.pop()
        for y in adj[x]:
            if y not in parent:parent[y]=x;stack.append(y)
    path=[];x=b
    while x!=a:
        y=parent[x];path.append(norm_edge(x,y));x=y
    return path[::-1]


def nonedges(n,edges):
    existing=set(edges)
    return [(a,b) for a in range(n) for b in range(a+1,n) if (a,b) not in existing]


def cycle_neighbors(n,edges,added):
    """Return one candidate for each original tree edge on the cycle.
    Deleting the inserted edge yields the original tree (score cached)."""
    if added in edges:raise ValueError('insertion must be a nonedge')
    base=edges|{added}
    return [(removed,base-{removed}) for removed in tree_path(n,edges,*added)]


def optimize(code,evaluator,rng,*,max_swaps=10,strategy='cycle',order='random',
             budget=None,stop_on_hit=False,ties='random',max_attempts=None):
    """Optimize one fixed-n labeled tree.

    budget counts actual evaluator calls, including initial tree. If the
    complete next cycle does not fit the budget, end without evaluating a
    partial cycle. Original tree remains candidate via its cached score.
    A fixed list of nonedges from the initial tree is visited once, as in
    paper §3.2. Input successes are left unchanged; stop_on_hit=False
    continues optimizing if a successful intermediate is encountered.
    Accepted distinct moves (including equality when ties='random') count
    toward max_swaps. 'single' draws one random deletion after the same
    insertion, not the random-cut-then-connect scheme in train.py.
    """
    if max_swaps<0 or budget is not None and budget<1:raise ValueError('invalid budget')
    if strategy not in ('cycle','single') or order not in ('random','lex') or ties not in ('random','stay'):raise ValueError('invalid search option')
    n=evaluator.args.n;code=np.array(code,dtype=np.int64); start=evaluator.calls
    current=evaluator.evaluate(code);initial=current
    edges={norm_edge(a,b) for a,b in prufer_to_edges(code,n)}
    candidates=nonedges(n,edges)
    if order=='random':rng.shuffle(candidates)
    swaps=attempts=skipped=0;break_reason='nonedges_exhausted'
    if initial[1]:break_reason='input_success'
    else:
        for added in candidates:
            if swaps>=max_swaps:break_reason='swap_limit';break
            if max_attempts is not None and attempts>=max_attempts:break_reason='attempt_limit';break
            if added in edges:
                skipped+=1;continue
            neighbors=cycle_neighbors(n,edges,added)
            if strategy=='single':neighbors=[neighbors[int(rng.integers(len(neighbors)))]]
            if budget is not None and evaluator.calls-start+len(neighbors)>budget:
                break_reason='query_budget';break
            attempts+=1
            best=current[0]; best_choices=[(code,edges,current)]
            for removed,next_edges in neighbors:
                c=np.asarray(edges_to_prufer(n,sorted(next_edges)),dtype=np.int64)
                rec=evaluator.evaluate(c)
                if rec[0]>best:best=rec[0];best_choices=[(c,next_edges,rec)]
                elif rec[0]==best:best_choices.append((c,next_edges,rec))
            if ties=='stay' and current[0]==best:continue
            newcode,newedges,newrec=(best_choices[int(rng.integers(len(best_choices)))] if ties=='random' else best_choices[0])
            if newedges!=edges:swaps+=1
            code,edges,current=newcode,newedges,newrec
            if stop_on_hit and current[1]:break_reason='success';break
    return {'code':code,'record':current,'initial':initial,'calls':evaluator.calls-start,
            'swaps':swaps,'attempts':attempts,'skipped_nonedge':skipped,'stop_reason':break_reason}


def restore_policy(path,n):
    data=json.loads(Path(path).read_text());p=Policy(n)
    if data['config']['n']!=n:raise ValueError('cannot restore different-size policy')
    params=[np.asarray(x,dtype=np.float64) for x in data['policy']['params']]
    if len(params)!=len(p.params) or any(a.shape!=b.shape for a,b in zip(params,p.params)):
        raise ValueError('policy architecture mismatch')
    p.params=params
    return p,data['config']


def run(args):
    t0=time.monotonic();rng=np.random.default_rng(args.seed);erng=np.random.default_rng(args.seed+10_000_019)
    ev=Evaluator(args); ee=Evaluator(args); policy=Policy(args.n); source_config=None
    if args.starts=='frozen':policy,source_config=restore_policy(args.frozen_policy,args.n)
    history=[];checkpoints=[];batches=0;accepted_total=attempts_total=0;hits_initial=hits_final=0
    initial_ids=set();final_ids=set();episodes=0;update_count=blocked_total=0
    def fresh_eval(step):
        if not args.eval_batch:return
        codes=(rng_eval_uniform() if args.starts=='uniform' else policy.sample(args.eval_batch,erng))
        records=[ee.evaluate(c) for c in codes]
        checkpoints.append({'batch':step,'training_calls':ev.calls,'evaluation_calls':ee.calls,**summary_batch(records)})
    def rng_eval_uniform():return erng.integers(args.n,size=(args.eval_batch,args.n-2))
    fresh_eval(0)
    while ev.calls<args.queries:
        b=min(args.batch,args.queries-ev.calls)
        starts=(rng.integers(args.n,size=(b,args.n-2)) if args.starts=='uniform' else policy.sample(b,rng))
        results=[]
        for code in starts:
            remain=args.queries-ev.calls
            if remain<=0:break
            res=optimize(code,ev,rng,max_swaps=args.max_swaps,strategy=args.strategy,order=args.order,
                         budget=min(remain,args.per_start_queries) if args.per_start_queries else remain,
                         stop_on_hit=args.stop_on_hit,ties=args.ties,max_attempts=args.max_attempts)
            results.append(res);accepted_total+=res['swaps'];attempts_total+=res['attempts'];episodes+=1
            initial,final=res['initial'],res['record'];hits_initial+=initial[1];hits_final+=final[1]
            initial_ids.add(initial[2]);final_ids.add(final[2])
        rec=[r['record'] for r in results]; initial=[r['initial'] for r in results];batches+=1
        if args.starts=='cem' and len(rec)>1:
            vals,hits,ids,_,_=zip(*rec);w,blocked=cem_weights(vals,hits,ids,args.variant,args.score,rng,args.elite_frac)
            blocked_total+=blocked;update_count+=int(policy.update(np.array([r['code'] for r in results]),w,args.lr))
        history.append({'batch':batches,'episodes':episodes,'calls':ev.calls,'hits_total':ev.successes,
                        'accepts_total':accepted_total,'attempts_total':attempts_total,'updates_total':update_count,
                        'initial':summary_batch(initial),'final':summary_batch(rec),'batch_calls':sum(r['calls'] for r in results)})
        if batches%args.eval_every==0 or ev.calls>=args.queries:fresh_eval(batches)
    elapsed=time.monotonic()-t0
    out={'config':vars(args),'source_config':source_config,'train':{'calls':ev.calls,'successes':ev.successes,
             'first_hit':ev.first_hit,'unique_successes':len(ev.hit_ids),'unique_sampled':len(ev.seen_ids),
             'witnesses':ev.witnesses,'best':ev.best,'max_violations':ev.max_violations,
             'max_violation_example':ev.max_violation_example},
         'search':{'episodes':episodes,'accepted_swaps':accepted_total,'attempted_insertions':attempts_total,
                   'initial_successes':hits_initial,'final_successes':hits_final,'unique_initial':len(initial_ids),
                   'unique_final':len(final_ids),'policy_updates':update_count,'blocked':blocked_total},
         'evaluation':{'calls':ee.calls,'successes':ee.successes,'unique_successes':len(ee.hit_ids),
                       'witnesses':ee.witnesses,'checkpoints':checkpoints},'history':history,
         'policy':{'params':[x.tolist() for x in policy.params],'updates':policy.t},
         'elapsed_seconds':elapsed,'queries_per_second':(ev.calls+ee.calls)/max(elapsed,1e-9),
         'notes':'Exact cached original score; cycle completeness means do not evaluate partial final cycle. No star penalty/path reset. Fixed initial nonedges; random order or lexicographic. CEM is imitation, not on-policy RL. Frozen evaluation uses no local search.'}
    p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'output':str(p),'calls':ev.calls,'hits':ev.successes,'unique_hits':len(ev.hit_ids),
        'best':ev.best['score'],'episodes':episodes,'final_hits':hits_final,'qps':out['queries_per_second']}),flush=True)
    return out


def parse_args(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n',type=int,required=True);p.add_argument('--family',choices=['independence','domination'],default='independence')
    p.add_argument('--index',type=int);p.add_argument('--required',type=int,default=1)
    p.add_argument('--score',choices=['raw','normalized','binary'],default='raw')
    p.add_argument('--strategy',choices=['cycle','single'],default='cycle');p.add_argument('--order',choices=['random','lex'],default='random')
    p.add_argument('--ties',choices=['random','stay'],default='random');p.add_argument('--max-swaps',type=int,default=10)
    p.add_argument('--max-attempts',type=int);p.add_argument('--per-start-queries',type=int)
    p.add_argument('--stop-on-hit',action='store_true');p.add_argument('--queries',type=int,default=100_000)
    p.add_argument('--starts',choices=['uniform','cem','frozen'],default='uniform');p.add_argument('--frozen-policy')
    p.add_argument('--variant',choices=['ordinary','balanced','matched'],default='ordinary');p.add_argument('--batch',type=int,default=64)
    p.add_argument('--elite-frac',type=float,default=.1);p.add_argument('--lr',type=float,default=.03)
    p.add_argument('--eval-batch',type=int,default=0);p.add_argument('--eval-every',type=int,default=25)
    p.add_argument('--seed',type=int,default=42);p.add_argument('--output',required=True)
    a=p.parse_args(argv)
    if a.n<3 or a.required<1 or a.queries<1 or a.max_swaps<0 or a.batch<1 or a.eval_batch<0 or a.eval_every<1 or not 0<a.elite_frac<=1:p.error('invalid parameters')
    if a.max_attempts is not None and a.max_attempts<1 or a.per_start_queries is not None and a.per_start_queries<1:p.error('invalid per-start limit')
    if a.index is not None and (a.required!=1 or not 0<a.index<a.n):p.error('fixed index requires one interior violation')
    if (a.starts=='frozen')!=bool(a.frozen_policy):p.error('frozen-policy path required only with frozen starts')
    if a.variant!='ordinary' and a.starts!='cem':p.error('masking applies to CEM only')
    return a


if __name__=='__main__':run(parse_args())
