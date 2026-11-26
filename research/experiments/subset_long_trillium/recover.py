"""Aggregate completed per-run output after the cross-platform bit-equality assertion.

D-169 specifies the numeric tolerance before accepting the output. The original
submitted training script is archived unchanged; this recovery runs no training.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

ORDER = ('exact','tolerance-only','tolerance-switch','tolerance-anneal','bits-switch',
         'bits-anneal','tolerance-late-switch','bits-only','bits-late-switch')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-rows',type=Path,required=True)
    parser.add_argument('--original-records',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    assert hashlib.sha256(args.original_records.read_bytes()).hexdigest() == 'eee1bae0c8b23d7cfcc7c540cdccac051633df0df1486968edd2aa4a8bbfca2b'
    base=json.loads(args.original_records.read_text())
    files=sorted(args.raw_rows.glob('*.json'))
    rows=[json.loads(p.read_text()) for p in files]
    assert len(rows)==72
    rmap={(r['seed'],r['mode']):r for r in rows}
    assert set(rmap)=={(seed,mode) for seed in range(42,50) for mode in ORDER}
    maxdiff=0.
    for expected in base['rows']:
        actual=rmap[expected['seed'],expected['mode']]
        prefix=[x for x in actual['records'] if x['step']<=600]
        assert len(prefix)==len(expected['records'])
        assert [{k:x[k] for k in y} for x,y in zip(prefix,expected['records'])]==expected['records']
        a=np.array(prefix[-1]['logits']); b=np.array(expected['final_logits'])
        assert np.allclose(a,b,rtol=0,atol=1e-12)
        maxdiff=max(maxdiff,float(np.max(np.abs(a-b))))
    for seed in range(42,50):
        for a,b in [('tolerance-only','tolerance-late-switch'),('bits-only','bits-late-switch')]:
            u=[r for r in rmap[seed,a]['records'] if r['step']<=600]
            v=[r for r in rmap[seed,b]['records'] if r['step']<=600]
            assert u==v
    rows=sorted(rows,key=lambda r:(r['seed'],ORDER.index(r['mode'])))
    report=dict(weights=base['weights'],target=base['target'],solutions=1,steps=60000,batch=256,eval=2048,
                original_prefix_reproduced=True,
                original_prefix_reproduction='numeric logits atol 1e-12; exact discrete checkpoint counts',
                original_prefix_logit_max_abs_difference=maxdiff,
                paired_forks_reproduced=True,
                raw_rows_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},rows=rows)
    args.out.write_text(json.dumps(report,separators=(',',':'))+'\n')
    print('RECOVERY_OK',len(rows),'max_abs_logit_difference',maxdiff)


if __name__=='__main__':
    main()
