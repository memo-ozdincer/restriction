"""Registered post-hoc deterministic checks; no model calls."""
import json
from pathlib import Path
from run import ROOT, verify, source, helper_source, dump

panel={r['id']:r for r in json.loads((ROOT/'panel.json').read_text())}
base=ROOT/'diagnostics'
base.mkdir(exist_ok=False)
for key in ('walk','reverse','tree'):
    row=panel[key]
    objs=[json.loads(p.read_text()) for p in sorted((ROOT/'rollouts'/key/'helper').glob('*/checked-object.json'))]
    obj=next(o for o in objs if o)
    verdict=verify(base/(key+'-exact-use'),source(row,'exact '+obj['name'],[obj]),'root')
    print(key,'exact verified',verdict['accepted'])
row=panel['reverse']
a=json.loads((ROOT/'rollouts'/'reverse'/'helper'/'0'/'answer.json').read_text())
assert a['type'].startswith('h : ')
b={**a,'type':a['type'][4:],'name':'help0'}
assert a['term']==b['term']
dump(base/'reverse-format-only-object.json',b)
v=verify(base/'reverse-format-only',helper_source(row,b),'obj')
print('format-only:',v['accepted'])
