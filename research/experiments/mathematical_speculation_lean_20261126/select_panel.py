"""Freeze first eight eligible hash-ranked rare-success MiniF2F questions."""
import json
from pathlib import Path
from collections import defaultdict
import hashlib
import pyarrow.parquet as pq
from verify import verify,ROOT,REPO,HEADER

p=next((REPO/'artifacts/failed-proof-corpora/internal-recovery').rglob('eval128-c0-*/artifacts/proofs/*.jsonl'))
inv=json.loads((REPO/'research/recovery/2026-11-18/evidence-inventory.json').read_text())['files']
expected=next(x['sha256'] for x in inv if 'eval128-c0-base' in x['archive_path'] and x['archive_path'].endswith('global_step_117.jsonl'))
assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==expected
dataset={r['theorem_full_name']:r for r in pq.read_table(REPO/'data/minif2f_test.parquet').to_pylist()}
rows=defaultdict(list)
for l in p.open():
 r=json.loads(l);n=r['theorem_name']
 if n in dataset and len(rows[n])<128: rows[n].append(r)
candidates=sorted((hashlib.sha256(('math-spec-lean-20261126/'+n).encode()).hexdigest(),n,v) for n,v in rows.items() if 1<=sum(r['correct'] for r in v)<=12)
selected=[];attempts=[]
for rank,n,v in candidates:
    statement=dataset[n]['theorem_statement']
    assert all(r['theorem_statement']==statement for r in v)
    # For each root, check first three archived correct proof bodies at most.
    successes=[r for r in v if r['correct']]
    for k,r in enumerate(successes[:3]):
        body=r['proof'].split(chr(96)*3,1)[0]
        rec=verify(statement,n,body,ROOT/'selection-checks'/n/str(k))
        attempts.append({'name':n,'rank':rank,'c0_correct':len(successes),'proposal_id':r['proposal_id'],**rec})
        print(n,k,rec['accepted'],rec['reason'],flush=True)
        if rec['accepted']:
            selected.append(dict(id=n,statement=statement,informal_statement=dataset[n]['informal_statement'],
                                 c0_correct=len(successes),hash_rank=rank,positive_witness_id=r['proposal_id']))
            break
    if len(selected)==8:break
assert len(selected)==8, len(selected)
(ROOT/'panel.json').write_text(json.dumps(selected,indent=2,ensure_ascii=False)+'\n')
(ROOT/'selection.json').write_text(json.dumps({'source_proof_log_sha256':expected,'dataset_sha256':hashlib.file_digest((REPO/'data/minif2f_test.parquet').open('rb'),'sha256').hexdigest(),'checks':attempts},indent=2)+'\n')
(ROOT/'header.lean').write_text(HEADER)
