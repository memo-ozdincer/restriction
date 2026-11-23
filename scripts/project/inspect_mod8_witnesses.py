"""Inspect literal nonnegative integer counterexample pairs on the recurring test root."""
from collections import Counter
import json
import re
from pathlib import Path
from analyze_crossfit_blocking import sha256

ROOT = Path(__file__).resolve().parents[2]
TARGET = 'numbertheory_notequiv2i2jasqbsqdiv8'
PAIR = re.compile(r"(?:\bh[₀-₉0-9\w']*\s+|\buse\s+)(\d+)(?:\s*,\s*|\s+)(\d+)\b")


def main():
    sources = json.loads((ROOT/'results/symmetric_recovery_c0_c1_c2_c3_seed42_pass128.json').read_text())['sources']
    output = {}
    for arm, source in sources.items():
        path = Path(source['proof_log'])
        assert sha256(path) == source['proof_log_sha256']
        with path.open() as stream:
            rows = [r for r in map(json.loads, stream) if r['theorem_name'] == TARGET][:128]
        assert len(rows) == 128
        counts = Counter()
        for row in rows:
            pairs = [(int(x), int(y)) for x,y in PAIR.findall(row['proof'])]
            detected = any(x%2 == y%2 == 0 and (x*x+y*y)%8 != 0 for x,y in pairs)
            counts['with_literal_counterexample'] += int(detected)
            counts['accepted'] += int(row['correct'])
            counts['accepted_with_literal_counterexample'] += int(detected and row['correct'])
        output[arm] = dict(counts)
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
