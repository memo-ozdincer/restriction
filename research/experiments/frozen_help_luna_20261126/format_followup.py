"""Three registered diagnostic Low continuations from format-only recovered lemma."""
import json
import concurrent.futures as cf
from run import ROOT, source, verify, one_proof

row=next(r for r in json.loads((ROOT/'panel.json').read_text()) if r['id']=='reverse')
base=ROOT/'diagnostics'
obj=json.loads((base/'reverse-format-only-object.json').read_text())
assert json.loads((base/'reverse-format-only'/'verdict.json').read_text())['accepted']
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    fs=[ex.submit(one_proof,row,'format_only_low',i,[obj],'low') for i in range(3)]
    for f in cf.as_completed(fs):f.result()
for i in range(3):
    d=ROOT/'rollouts'/'reverse'/'format_only_low'/str(i)
    if json.loads((d/'outcome.json').read_text())['accepted']:
        body=json.loads((d/'answer.json').read_text())['body']
        verify(d/'replay_bare',source(row,body,[]),'root')
