#!/usr/bin/env python3
"""Inspect published test reference edits, not repair model generations."""
import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('directory',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args()
    inv=json.loads((a.directory/'inventory.json').read_text())
    result={}
    for item in inv:
        f=Path(item['path'])
        if not f.name.endswith('.jsonl'):continue
        assert hashlib.file_digest(f.open('rb'),'sha256').hexdigest()==item['sha256']
        counts=Counter();source=Counter();examples={}
        for i,line in enumerate(f.open()):
            r=json.loads(line);counts['rows']+=1;source[r['source']]+=1
            old=r['incorrect_proof'].splitlines();new=r['correct_proof'].splitlines()
            ops=[op for op in SequenceMatcher(None,old,new,autojunk=False).get_opcodes() if op[0]!='equal']
            if not ops:counts['identical']+=1
            elif len(ops)==1 and max(ops[0][2]-ops[0][1],ops[0][4]-ops[0][3])==1:
                counts['single_line_edit']+=1
                counts['one_line_'+ops[0][0]]+=1
            else:counts['multiple_line_edit']+=1
            if not r.get('state_at_error') or r['state_at_error']=='Could not retrieve proof state.':counts['missing_state']+=1
            if not r.get('error'):counts['missing_error']+=1
            if ops and len(examples)<3:
                examples[str(i)]=dict(src_hash=r['src_hash'],error=str(r.get('error'))[:400],
                    changes=[dict(old=old[i1:i2],new=new[j1:j2]) for tag,i1,i2,j1,j2 in ops])
        result[f.stem]=dict(counts=counts,source_counts=source,examples=examples)
    assert sum(x['counts']['rows'] for x in result.values())==1835
    with a.output.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print({k:v['counts'] for k,v in result.items()})


if __name__=='__main__':main()
