"""Recompute the online pilot's gates and transfer counts from individual proposals."""
import argparse
from collections import Counter
import json
from pathlib import Path

from run_recursive_grpo import TRANSFER, lean, promote
from verl.lean.proof_modes import mode_id


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('run', type=Path)
    p.add_argument('panel', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    train = {x['theorem']:x['statement'] for x in json.loads(a.panel.read_text())['panel']}
    transfer = {k:f'theorem {k} {v} := by\n' for k,v in TRANSFER.items()}
    summary = {}
    for arm in ['discovery','control','recursive']:
        root = a.run/arm
        phases = ['learn','discover'] if arm=='discovery' else ['first','second','probe','transfer']
        expected = [(phase,k) for phase in phases for k in (transfer if phase=='transfer' else train)]
        groups = lean.rows(root/'groups.jsonl')
        assert [(g['phase'],g['name']) for g in groups]==expected
        blocks = {k:[] for k in train} if arm!='recursive' else json.loads((a.run/'discovery/blocklist.json').read_text())
        counts = {}
        cells = []
        for g in groups:
            phase,name = g['phase'],g['name']
            folder = root/f'{phase}-{name}'
            raw = json.loads((folder/'samples.json').read_text())
            assert [r['sample_index'] for r in raw]==list(range(16))
            assert all(r['seed']==g['seed'] for r in raw)
            statements = transfer if phase=='transfer' else train
            source = lean.HEADER+statements[name]
            sources = json.loads((folder/'sources.json').read_text())
            verdicts = lean.rows(folder/'lean.jsonl')
            assert {v['id'] for v in verdicts}==set(sources) and len(verdicts)==len(sources)
            accepted = set()
            for v in verdicts:
                assert lean.sha(sources[v['id']]['code'])==v['id']==v['code_sha256']
                assert not v.get('system_errors')
                if v['accepted']:
                    assert v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS
                    accepted.add(v['id'])
            modes = []
            for row in raw:
                body,error = lean.completion_code(row['text'])
                key = None if error else lean.sha(source+body+'\n#print axioms '+name+'\n')
                assert key is None or key in sources
                modes.append(mode_id(body) if key in accepted else None)
            active = blocks.get(name,[])
            assert modes==g['correct_modes'] and active==g['blocked_before']
            correct = sum(m is not None for m in modes)
            hits = sum(m in active for m in modes)
            step = phase in ('learn','first','second') and hits<correct<16
            assert step==g['optimizer_step']
            new = promote(modes,active) if phase=='discover' or (arm=='recursive' and phase=='first') else None
            assert new==g['promoted']
            if new:
                active.append(new)
            cell = dict(name=name,phase=phase,accepted=correct,distinct_modes=len(set(modes)-{None}),
                        matches_archive=hits,step=int(step),promotions=int(bool(new)))
            counts.setdefault(phase,Counter()).update(dict(proposals=16,solved=int(correct>0),
                       accepted=correct,physical_checks=len(sources),matches_archive=hits,steps=int(step),
                       promotions=int(bool(new))))
            cells.append(cell)
        assert blocks==json.loads((root/'blocklist.json').read_text())
        summary[arm]=dict(totals=counts,cells=cells,adapter_sha256=lean.sha((root/'adapter/adapter_model.safetensors').read_bytes()))
    final_blocks = json.loads((a.run/'recursive/blocklist.json').read_text())
    paired = {}
    for arm in ['control','recursive']:
        for g in lean.rows(a.run/arm/'groups.jsonl'):
            if g['phase'] != 'probe':
                continue
            name = g['name']
            counts = Counter(m for m in g['correct_modes'] if m is not None)
            survivors = {m:n for m,n in counts.items() if m not in final_blocks[name]}
            paired.setdefault(name,{})[arm] = dict(accepted=sum(counts.values()),
                outside_final_blocklist=sum(survivors.values()),distinct_outside=len(survivors))
    summary['paired_probe'] = paired
    lean.write(a.output,summary)


if __name__=='__main__':
    main()
