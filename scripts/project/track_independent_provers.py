#!/usr/bin/env python3
"""Replicate near-miss tracking on deduplicated public compiler-labelled candidates."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

import pyarrow.parquet as pq
from track_near_misses import Bank, analyze, meaningful, category
from track_external_near_misses import canonicalize_proof


def extract(r):
    source=r['source']
    # Name must be exact and declaration must be singular and line-initial.
    decls=list(re.finditer(r"(?m)^(?:theorem|lemma)\s+([^\s(:]+)",source))
    if len(decls)!=1 or decls[0].group(1)!=r['problem']:
        return None
    start=decls[0].start()
    # Require exact tactic proof boundary, not a different target.
    match=re.search(r':=\s*by\s*\n',source[start:])
    if match is None:
        return None
    end=start+match.end()
    # Conservatively exclude other top-level declarations after the proof.
    body=source[end:]
    if re.search(r'(?m)^(?:def|abbrev|axiom|opaque|example|instance|theorem|lemma)\s',body):
        return None
    return (r['problem'],source[start:end],source[:start]),body.rstrip('\n')+'\n'


def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--canonical',action='store_true');a=p.parse_args()
    inv=json.loads(Path('research/experiments/failed_proof_corpus_20261125/evaluation-benchmark-inventory.json').read_text())
    assert hashlib.file_digest(a.input.open('rb'),'sha256').hexdigest()==next(x['sha256'] for x in inv if x['path'].endswith('.parquet'))
    stats=defaultdict(Counter)
    data=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    within={}
    for i,r in enumerate(pq.read_table(a.input).to_pylist()):
        m=r['prover_model']; bench=r['benchmark']; s=stats[(bench,m)]
        s['published_rows']+=1
        assert (r['label']==1)==(r['status']=='passed')
        if r['status']=='wrong_declaration':
            s['wrong_declaration']+=1;continue
        parsed=extract(r)
        if parsed is None:
            s['unsupported_source']+=1;continue
        k,body=parsed
        if a.canonical: body=canonicalize_proof(body)+'\n'
        s['included']+=1;s['accepted' if r['label'] else 'rejected']+=1
        data[bench][m][k].append(dict(proof=body,correct=bool(r['label']),failure_class='correct' if r['label'] else 'lean_rejected',
                                     proposal_id=f'epfl-row-{i}',candidate_index=r['candidate_index']))
    for b,models in data.items():
        for m,groups in models.items():
            s=stats[(b,m)]; s['groups']=len(groups)
            for k,rs in groups.items():
                rs.sort(key=lambda x:(x['candidate_index'],x['proposal_id']))
                bank=Bank(rs)
                for body in bank.bad:
                    if body in bank.good:
                        s['contradictory_identical_bodies']+=1;continue
                    siblings=bank.siblings(body)
                    if siblings:
                        s['unique_near_misses']+=1
                        if any(sum(map(meaningful,sc))>=2 for _,_,sc,_,_ in siblings):s['strict_near_misses']+=1
                        wkey=f'{b}/{m}'
                        entries=within.setdefault(wkey,[])
                        entries.append(dict(theorem=k[0],statement=k[1],failed=''.join(body),ids=bank.bad[body],
                                            siblings=[dict(proof=''.join(g),ids=bank.good[g],old=old,new=new,
                                                           category=category(old,new),retained_lines=sum(map(meaningful,sc)))
                                                      for g,i,sc,old,new in siblings]))
            print(b,m,dict(s),flush=True)
    comparisons={}
    for b,models in data.items():
        for m,groups in models.items():
            for target,tgroups in models.items():
                if target==m:continue
                keys=sorted(k for k in groups.keys() & tgroups.keys() if len(groups[k])>=16 and len(tgroups[k])>=16)
                key=f'{b}/{m}/{target}'
                result=analyze({'c0':{k:groups[k][:16] for k in keys},
                                'cross_prover':{k:tgroups[k][:8] for k in keys}},discovery_n=8,observation_n=8)
                comparisons[key]=dict(eligible_groups=len(keys),**result)
                print(key,len(keys),len(result['records']),{k:v for k,v in result['counts'].items() if k.endswith(('/all','/strict'))},flush=True)
    with a.output.open('x') as f:json.dump({'source_stats':{'/'.join(k):v for k,v in stats.items()},'comparisons':comparisons,'within_records':within,'canonical':a.canonical},f,indent=2,ensure_ascii=False)


if __name__=='__main__':main()
