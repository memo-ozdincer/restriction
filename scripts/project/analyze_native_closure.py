"""Descriptive token-boundary and literal-proof-style counts, not a strategy classifier."""
import argparse
import json
from pathlib import Path
import interface_discovery_pilot as lean
from train_native_closure import ARMS


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args();r=a.run;tasks=json.loads((r/'test.json').read_text());cells={};inputs={}
    for arm in ARMS:
        rs=[]
        for t in tasks:
            f=r/arm/(t['id'].replace('/','_')+'.json');batch=json.loads(f.read_text());rs+=batch['rows'];inputs[str(f.relative_to(r))]=lean.sha(f.read_bytes())
        assert len(rs)==160
        cells[arm]=dict(proposals=len(rs),first_generated_bos=sum(s['response_token_ids'][0]==100000 for s in rs),
            have_source_contract_literal=sum('have source_contract' in s['text'] for s in rs),
            rcases_source_contract_literal=sum('rcases source_contract' in s['text'] for s in rs),
            generated_tokens=sum(s['generated_tokens'] for s in rs))
    result=dict(scope='Post-generation descriptive literal-string/token counts; no semantic or causal strategy claim',cells=cells,input_sha256=inputs)
    lean.write(r/'response-style.json',result);print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
