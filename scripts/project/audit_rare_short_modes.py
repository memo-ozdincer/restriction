"""Frozen C0 rare-short signature diagnostic; see research/RRL_SELECTIVE_SHARPENING_2026-11-26.md."""
import collections
import glob
import json
import statistics as s
from pathlib import Path

banks = {}
for arm in range(4):
    p, = glob.glob(f'artifacts/failed-proof-corpora/internal-recovery/restriction-rl/runs/eval128-c{arm}*/artifacts/proofs/global_step_117.jsonl')
    b = collections.defaultdict(list)
    with open(p) as f:
        for line in f:
            r = json.loads(line)
            k = r['theorem_hash']
            if len(b[k]) < 128:
                b[k].append((r['correct'], r['tactic_prefix_signature'], r['token_count']))
    banks[arm] = b
rows = []
for k, b in banks[0].items():
    if any(len(banks[a][k]) != 128 for a in range(4)):
        continue
    modes = collections.defaultdict(list)
    for c, m, n in b[:64]:
        if c:
            modes[m].append(n)
    if not modes:
        continue
    dom = max(modes, key=lambda m: len(modes[m]))
    if len(modes[dom]) < 4 or len(modes[dom]) * 2 <= sum(map(len, modes.values())):
        continue
    opts = [(s.median(v) / s.median(modes[dom]), m) for m, v in modes.items()
            if m != dom and 1 <= len(v) <= 4 and s.median(v) <= s.median(modes[dom]) / 2]
    if not opts:
        continue
    ratio, m = min(opts)
    counts = [sum(c and sig == m for c, sig, n in
                  (banks[a][k][64:128] if a == 0 else banks[a][k][:64])) for a in range(4)]
    rows.append(dict(theorem_hash=k, mode=m, ratio=ratio, counts=counts))
print('roots', len(rows))
for a in range(4):
    print(a, 'discovered', sum(r['counts'][a] > 0 for r in rows),
          'total draws', sum(r['counts'][a] for r in rows))
for a in (1, 3):
    shared = [r for r in rows if r['counts'][2] and r['counts'][a]]
    print('shared', a, len(shared), 'RTU', sum(r['counts'][2] for r in shared),
          'other', sum(r['counts'][a] for r in shared))
Path('research/experiments/rrl_sharpening_20261126/rare_short_modes.json').write_text(
    json.dumps(rows, indent=2) + '\n')
