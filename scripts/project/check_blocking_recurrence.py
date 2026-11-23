"""Measure split-half recurrence of exclusive solves from frozen evaluation logs."""
from collections import Counter
import json
from pathlib import Path
from scripts.project.analyze_evaluation_accumulation import load_run

ROOT = Path(__file__).resolve().parents[2]


def label(left, right):
    return ('both' if right else 'grpo') if left else ('blocking' if right else 'neither')


def main():
    sources = json.loads((ROOT/'results/symmetric_recovery_c0_c1_c2_c3_seed42_pass128.json').read_text())['sources']
    arms = []
    for key, condition in [('c1', 'c1_grpo_default'), ('c3', 'c3_hardblock_restart')]:
        recorded = sources[key]
        data, metadata = load_run(Path(recorded['run_dir']), condition)
        assert metadata['num_samples'] == 128 and metadata['proof_log_sha256'] == recorded['proof_log_sha256']
        arms.append(data)
    grpo, blocking = arms
    assert grpo.keys() == blocking.keys()
    splits = {}
    for name, row in grpo.items():
        split = row['dataset']
        assert split == blocking[name]['dataset']
        counts = [[sum(x['correct'] for x in d[name]['proposals'][i:i+64]) for d in arms] for i in (0, 64)]
        first, second = [label(*pair) for pair in counts]
        result = splits.setdefault(split, dict(transitions={}, exclusive=[]))
        result['transitions'].setdefault(first, Counter())[second] += 1
        if first in ('blocking', 'grpo'):
            result['exclusive'].append(dict(theorem=name, direction=first, grpo_blocking_counts=counts))
    print(json.dumps(splits, indent=2))


if __name__ == '__main__':
    main()
