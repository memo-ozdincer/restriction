"""Freeze a train-only panel using discovery proposals, then measure remaining modes."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from analyze_crossfit_blocking import sha256, unique_top
from verl.lean.proof_modes import mode_id, tactic_heads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    validation = json.loads((args.runs / 'c0-base-20260804-seed42-complete/validation.json').read_text())
    groups = defaultdict(list)
    for item in validation['proof_logs']:
        path = args.runs / item['path'].split('/runs/')[1]
        assert sha256(path) == item['sha256']
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                group = groups[row['theorem_name']]
                if len(group) < 32:
                    group.append(row)
    assert len(groups) == 9655 and all(len(g) == 32 for g in groups.values())
    panel = []
    eligible = 0
    for name in sorted(groups, key=lambda k: hashlib.sha256(k.encode()).digest()):
        rows = groups[name]
        counts = Counter(mode_id(x['proof']) for x in rows[:16] if x['correct'])
        blocked = []
        for _ in range(2):
            leader = unique_top(counts)
            if leader is None or counts[leader] < max(2, .4 * counts.total()):
                break
            blocked.append(dict(mode=leader, count=counts.pop(leader)))
        if len(blocked) != 2 or counts.total() < 2:
            continue
        eligible += 1
        if len(panel) == 8:
            continue
        ids = [entry['mode'] for entry in blocked]
        held = [row for row in rows[16:] if row['correct']]
        remaining = [sum(mode_id(x['proof']) not in ids[:depth] for x in held) for depth in range(3)]
        examples = {}
        for row in held:
            proof = row['proof']
            examples.setdefault(mode_id(proof), dict(proof=proof, heads=tactic_heads(proof)))
        panel.append(dict(theorem=name, statement=rows[0]['theorem_statement'], blocked=blocked,
                          held_remaining=remaining, held_examples=examples))
    args.output.write_text(json.dumps(dict(eligible=eligible, panel=panel), indent=2)+'\n')


if __name__ == '__main__':
    main()
