"""Inspect generated BOS tokens hidden by skip_special_tokens decoding."""
import argparse
import json
from pathlib import Path
import interface_discovery_pilot as lean


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('run',type=Path);a=p.parse_args();r=a.run
    cells={};inputs={}
    for f in sorted((r/'samples').glob('*.json')):
        batch=json.loads(f.read_text());rs=batch['rows'];assert len(rs)==16
        cells.setdefault(batch['task'],{})[batch['mode']]=dict(proposals=16,first_generated_bos=sum(s['response_token_ids'][0]==100000 for s in rs),
            any_generated_bos=sum(100000 in s['response_token_ids'] for s in rs))
        inputs[str(f.relative_to(a.bundle))]=lean.sha(f.read_bytes())
    previous=a.bundle/'runs/contract-closure-20261124-1400174/experiment';prior_counts={}
    for arm in ['base','hindsight','executable','transport']:
        rows=[]
        for f in sorted((previous/arm).glob('*_*.json')):
            batch=json.loads(f.read_text())
            if 'rows' not in batch:continue
            rows+=batch['rows'];inputs[str(f.relative_to(a.bundle))]=lean.sha(f.read_bytes())
        assert len(rows)==160
        prior_counts[arm]=dict(proposals=160,first_generated_bos=sum(s['response_token_ids'][0]==100000 for s in rows))
    training={}
    for arm in ['hindsight','executable','transport']:
        f=previous/arm/'tokens.json';rows=json.loads(f.read_text());assert len(rows)==8
        training[arm]=dict(records=8,responses_starting_bos=sum(x['response_token_ids'][0]==100000 for x in rows));inputs[str(f.relative_to(a.bundle))]=lean.sha(f.read_bytes())
    result=dict(current=cells,previous_generation=prior_counts,previous_training=training,input_sha256=inputs,
        interpretation='Generated token 100000 is removed by skip_special_tokens decoding. Its presence is measured directly from saved token IDs; no correctness labels change.')
    lean.write(r/'boundary-token-analysis.json',result);print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
