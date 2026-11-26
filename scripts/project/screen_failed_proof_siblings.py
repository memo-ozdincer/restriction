#!/usr/bin/env python3
"""Find literal single-line differences between archived rejected/accepted siblings."""
import argparse
import collections
import json
from pathlib import Path


def screen(path):
    groups = collections.defaultdict(list)
    physical = 0
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            groups[row['theorem_name']].append(row)
            physical += 1
    assert len(groups) == 467 and physical == 59904
    counts = collections.Counter()
    examples = {}
    roots = set()
    for name, rows in groups.items():
        rows = rows[:128]
        assert len(rows) == 128
        buckets = collections.defaultdict(list)
        for row in rows:
            buckets[(row['theorem_statement'], row['context'])].append(row)
        for items in buckets.values():
            good = {}
            for r in items:
                if r['correct']:
                    good[tuple(r['proof'].splitlines(keepends=True))] = r
            deleted = collections.defaultdict(list)
            for lines in good:
                for i, ln in enumerate(lines):
                    if ln.strip():
                        deleted[lines[:i]+lines[i+1:]].append((i, lines))
            unique_bad = set()
            matched = set()
            for r in items:
                counts['registered'] += 1
                if r['correct']:
                    counts['correct'] += 1
                    continue
                counts['all_failed'] += 1
                if r['failure_class'] != 'lean_rejected':
                    continue
                counts['lean_rejected'] += 1
                b = tuple(r['proof'].splitlines(keepends=True))
                unique_bad.add(b)
                if b in good:
                    counts['contradictory_identical_attempts'] += 1
                    continue
                hits = {}
                for i, a in deleted.get(b, []):
                    hits.setdefault('insert', a)
                for i, ln in enumerate(b):
                    if not ln.strip():
                        continue
                    key = b[:i]+b[i+1:]
                    if key in good:
                        hits.setdefault('delete', key)
                    for j, a in deleted.get(key, []):
                        if i == j and a[i] != ln:
                            hits.setdefault('replace', a)
                if not hits:
                    continue
                counts['matched_attempts'] += 1
                matched.add(b)
                roots.add(name)
                for kind, a in hits.items():
                    counts[kind] += 1
                    if len(examples.setdefault(kind, [])) < 12:
                        examples[kind].append(dict(theorem=name, statement=r['theorem_statement'],
                            rejected=r['proof'], accepted=good[a]['proof'],
                            rejected_id=r['proposal_id'], accepted_id=good[a]['proposal_id']))
            counts['unique_rejected_bodies'] += len(unique_bad)
            counts['matched_unique_bodies'] += len(matched)
    counts['matched_theorems'] = len(roots)
    return dict(counts=counts, examples=examples, matched_theorems=sorted(roots))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    result = {}
    for path in sorted(args.root.rglob('eval128-*/artifacts/proofs/*.jsonl')):
        condition = path.parents[2].name.split('-')[1]
        result[condition] = screen(path)
        print(condition, result[condition]['counts'], flush=True)
    assert set(result) == {'c0','c1','c2','c3'}
    with args.output.open('x') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
