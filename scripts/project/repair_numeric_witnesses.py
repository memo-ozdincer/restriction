"""Replace only the two witness expressions, preserving every generated proof-closing command."""
import argparse
import json
from pathlib import Path
import re
from block_numeric_witnesses import lean,statement


def replace_pair(body,x,y):
    patterns=[
        (r'(\buse\s+)\d+(\s*,\s*)\d+(?:\s*\*\s*\d+)?',r'\g<1>%d\g<2>%d'),
        (r'(⟨\s*)\d+(\s*,\s*)\d+',r'\g<1>%d\g<2>%d'),
        (r'(apply Exists.intro )\d+(\n\s*apply Exists.intro )\d+',r'\g<1>%d\g<2>%d'),
    ]
    for pattern,replacement in patterns:
        result,n=re.subn(pattern,replacement%(x,y),body)
        if n==1:
            return result
    raise ValueError(body)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle',type=Path)
    parser.add_argument('run',type=Path)
    parser.add_argument('out',type=Path)
    a=parser.parse_args()
    raw=json.loads((a.run/'discovery/samples.json').read_text())['rows']
    pairs=[(x,y) for x in range(1,65) for y in range(x+1,65) if x*x+y*y==65*65]
    jobs={}
    rows=[]
    for r in raw:
        body,error=lean.completion_code(r['text'])
        assert not error
        for x,y in pairs+[(1,2)]:
            code=lean.HEADER+statement([])+replace_pair(body,x,y)+'\n#print axioms target'
            key=lean.sha(code)
            jobs[key]=dict(id=key,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),
                           verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
            rows.append(dict(sample=r['sample_index'],pair=[x,y],key=key))
    a.out.mkdir()
    lean.write(a.out/'sources.json',{k:v['code'] for k,v in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4)
    assert all(not v.get('system_errors') for v in vs)
    valid={r['id'] for r in vs if r['accepted']}
    for row in rows:
        row['accepted']=row['key'] in valid
    lean.write(a.out/'results.json',rows)
    print({str(pair):sum(r['accepted'] for r in rows if r['pair']==list(pair)) for pair in pairs+[(1,2)]})


if __name__=='__main__':
    main()
