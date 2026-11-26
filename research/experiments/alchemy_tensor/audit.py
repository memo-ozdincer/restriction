"""Independent rank oracle and replay/counter audit after the registered run."""
from itertools import combinations
from pathlib import Path
import json,numpy as np
import train
from native_environment import TERMS,tensor_value
HERE=Path(__file__).parent
d=json.loads((HERE/'results.json').read_text())
env=train.make_graph(); train.init(env)
ranks={0:0}
for k in range(1,5):
    for ss in combinations(range(len(TERMS)),k):
        t=train.scalar_tensor(ss)
        ranks.setdefault(t,k)
test_ranks={str(tensor_value(env[0][i])):ranks[train.scalar_tensor(env[0][i])] for i in env[4]['test']}
quantities={}
for mode in train.MODES:
    arms=[a for r in d['results'] for a in r['arms'] if a['mode']==mode]
    counts=np.sum([a['test']['rank_counts'] for a in arms],axis=0)
    expanded=np.sum([a['test']['expanded_by_rank'] for a in arms],axis=0)
    quantities[mode]=dict(rank_counts=counts.tolist(),expansion_counts=expanded.tolist(),expanded_conditional_rank=[float(x/y) if y else None for x,y in zip(expanded,counts)])
for r in d['results']:
    assert len(r['pretrain'])==d['config']['pre']
    for arm in r['arms']:
        assert len(arm['train'])==d['config']['post']
        for row in arm['train']:
            assert row['policy']+row['reset']==train.H*train.GROUP*train.GROUPS
        w={k:np.array(a,dtype=np.float32) for k,a in arm['weights'].items()}
        ev=train.evaluate(w,'test',r['seed']+20_000)
        # The saved eval ran scalar verification of every path. Replaying same
        # RNG on Apple Silicon can differ near categorical float boundaries.
        assert abs(ev['rank']-arm['test']['rank'])<.02
        arm_id=f"{r['seed']}_{arm['mode']}"
        quantities.setdefault('replays',{})[arm_id]={'original':arm['test']['rank'],'local':ev['rank']}
        for path in arm['test']['verified_expansion_examples'].values():
            ss=[tuple(s) for s in path]
            assert all(train.scalar_tensor(s)==train.scalar_tensor(ss[0]) for s in ss)
            assert any(len(b)>len(a) for a,b in zip(ss,ss[1:])) and len(ss[-1])<4
            from native_environment import tensor_neighbors
            assert all(b==a or b in tensor_neighbors(a,train.CAP) for a,b in zip(ss,ss[1:]))
out=dict(test_ranks=test_ranks,mean_optimal_rank=float(np.mean(list(test_ranks.values()))),quantities=quantities)
(HERE/'audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
