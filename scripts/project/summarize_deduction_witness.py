#!/usr/bin/env python3
"""Produce compact internal counts, exact attempt subset, and public RL comparison."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

def summarize(banks):
    summary, selected = {}, {}
    for c, bank in banks.items():
        d = defaultdict(Counter)
        s = {}
        for k, r in bank['roots'].items():
            x = d[r['category']]
            x['roots'] += 1
            x['solved'] += any(a.startswith('accepted') for a in r['counts'])
            x.update(r['counts'])
            if 'attempts' in r:
                s[k] = r
        f = Counter()
        for a in s['amc12b_2020_p6']['attempts']:
            line = next((l.strip() for l in a['proof'].splitlines()
                         if re.match(r"\s*(use\b|exact\s*⟨|refine'?\s*⟨)", l)), '(none)')
            group = 'known_correct' if line in ('use (n + 1)', 'use (n + 2 - 1)') else 'other_or_unclassified'
            f[group+'/'+a['outcome']] += 1
        summary[c] = {'sha256': bank['sha256'], 'member': bank['member'],
                      'totals': bank['totals'], 'categories': d, 'factorial_exact_forms': f,
                      'per_root': {k: {'category': r['category'], 'counts': r['counts']}
                                   for k,r in bank['roots'].items()}}
        selected[c] = s
    return summary, selected

def public_summary(selected, file, inventory):
    import pyarrow.parquet as pq
    source = next(x for x in inventory if x['path'] == str(file))
    with file.open('rb') as f:
        assert hashlib.file_digest(f, 'sha256').hexdigest() == source['sha256']
    rows = pq.read_table(file).to_pylist()
    result = {}
    for k,r in selected['c0'].items():
        rr = [x for x in rows if x['problem_name'] == k]
        assert len(rr) == 4 and all(x['formal_statement'] == r['statement'] for x in rr)
        result[k] = {'statement':r['statement'], 'counts':Counter(x['status'] for x in rr)}
    return {'source':source, 'roots':result}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('screen', type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('public_parquet',type=Path)
    args = p.parse_args()
    summary, selected = summarize(json.loads(args.screen.read_text()))
    inventory = json.loads(Path('research/experiments/failed_proof_corpus_20261125/external-inventory.json').read_text())
    public = public_summary(selected,args.public_parquet,inventory)
    args.output.mkdir(parents=True,exist_ok=True)
    for name, body in [('screen-summary.json',summary), ('public-v15rl-summary.json',public)]:
        (args.output/name).write_text(json.dumps(body,indent=2,ensure_ascii=False)+'\n')
    (args.output/'selected-attempts.json.gz').write_bytes(gzip.compress(json.dumps(selected,ensure_ascii=False).encode(),mtime=0))

if __name__ == '__main__':
    main()
