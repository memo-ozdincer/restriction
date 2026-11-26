"""Independent unique-subset enumeration and exact policy probability audit."""
from collections import defaultdict
import itertools
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parent
D = json.loads((ROOT/'results.json').read_text())
weights = list(map(int,D['weights']))
target = int(D['target'])
# Independent scalar meet-in-middle. The witness is never supplied to train_long.py.
half = len(weights)//2
right = defaultdict(list)
for bits in itertools.product((0,1),repeat=len(weights)-half):
    right[sum(x*b for x,b in zip(weights[half:],bits))].append(bits)
solutions = []
for bits in itertools.product((0,1),repeat=half):
    subtotal = sum(x*b for x,b in zip(weights[:half],bits))
    solutions.extend(bits+tail for tail in right[target-subtotal])
assert len(solutions)==1
witness=tuple(solutions[0])
assert D['original_prefix_reproduced'] and D['paired_forks_reproduced']
assert len(D['rows'])==72 and len({(r['mode'],r['seed']) for r in D['rows']})==72


def logprob(logits):
    # Stable exact Bernoulli product in log-space, independent of training implementation.
    return -sum(float(np.logaddexp(0.,-z if b else z)) for z,b in zip(logits,witness))


def probability(logits):
    return math.exp(logprob(logits))


rows = []
for row in D['rows']:
    assert row['records'][0]['step']==0 and row['records'][-1]['step']==D['steps']==60000
    assert row['records'][-1]['logits']==row['final_logits']
    assert all(a['train_exact_hits']<=b['train_exact_hits'] and a['train_reward_hits']<=b['train_reward_hits'] for a,b in zip(row['records'],row['records'][1:]))
    logits=np.asarray(row['final_logits'])
    prob=1/(1+np.exp(-logits))
    fresh=np.random.default_rng(20261128+row['seed']).random((4096,len(weights)))<prob
    fresh_hits=0
    for candidate in fresh:
        exact=sum(w*int(b) for w,b in zip(weights,candidate))==target
        assert exact == (tuple(map(int,candidate))==witness)
        fresh_hits+=int(exact)
    trace=[dict(step=r['step'],exact_probability=probability(r['logits']),
                log10_exact_probability=logprob(r['logits'])/math.log(10),
                exact_training_hits=r['train_exact_hits'],training_reward_hits=r['train_reward_hits'],
                sampled_exact_eval=r['exact_eval']) for r in row['records']]
    first_threshold=next((r['step'] for r in trace if r['exact_probability']>=.1),None)
    best=max(trace,key=lambda x:x['exact_probability'])
    rows.append(dict(mode=row['mode'],seed=row['seed'],first_exact_batch=row['first_exact_batch'],
                     first_threshold_checkpoint=first_threshold,best_probability=best['exact_probability'],
                     best_step=best['step'],final_probability=probability(logits),
                     final_log10_probability=logprob(logits)/math.log(10),
                     fresh_exact_hits=fresh_hits,fresh_trials=4096,
                     final_training_exact_hits=row['records'][-1]['train_exact_hits'],
                     final_training_reward_hits=row['records'][-1]['train_reward_hits'],trace=trace))

modes=defaultdict(list)
for row in rows:modes[row['mode']].append(row)
summary=[]
for mode, rs in modes.items():
    assert len(rs)==8
    item=dict(mode=mode,runs=8,at_final_threshold=sum(r['final_probability']>=.1 for r in rs),
              ever_threshold=sum(r['best_probability']>=.1 for r in rs),
              mean_final_probability=sum(r['final_probability'] for r in rs)/8,
              first_exact_count=sum(r['first_exact_batch'] is not None for r in rs),
              mean_log10_final_probability=sum(r['final_log10_probability'] for r in rs)/8,
              fresh_exact_hits=sum(r['fresh_exact_hits'] for r in rs),fresh_trials=4096*8,
              checkpoint_mean_probability={str(step):sum(next(r['exact_probability'] for r in x['trace'] if r['step']==step) for x in rs)/8 for step in (0,600,3000,6000,15000,30000,60000)},
              per_seed=[{k:v for k,v in r.items() if k!='trace'} for r in rs])
    summary.append(item)
    print(mode,'hits',item['first_exact_count'],'ever>=10%',item['ever_threshold'],
          'final>=10%',item['at_final_threshold'], 'mean_final',round(item['mean_final_probability'],6),
          'fresh',item['fresh_exact_hits'])
(ROOT/'audit.json').write_text(json.dumps(dict(uniqueness=True,summary=summary,rows=rows),separators=(',',':'))+'\n')
