#!/usr/bin/env python3
"""Fixed-proof concurrency diagnostic; never a new model-performance result."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def select_batches(path, steps=(100, 550)):
    batches = {step: [] for step in steps}
    with Path(path).open() as stream:
        for line in stream:
            row = json.loads(line)
            match = re.search(r':step-(\d+)$', row['batch_id'])
            if match and int(match[1]) in batches:
                batches[int(match[1])].append(row)
    for step, rows in batches.items():
        if len(rows) != 512 or len({r['proposal_id'] for r in rows}) != 512:
            raise ValueError(f'expected 512 unique proposals at step {step}')
    return batches


def compare(left, right):
    if len(left) != len(right):
        raise ValueError('unaligned result lengths')
    return {
        'verdict_disagreements': sum(a['verdict'] != b['verdict'] for a, b in zip(left, right)),
        'failure_class_disagreements': sum(a['failure_class'] != b['failure_class'] for a, b in zip(left, right)),
    }


def available_kib():
    return int(re.search(r'MemAvailable:\s+(\d+)', Path('/proc/meminfo').read_text())[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--c2-run', type=Path, required=True)
    parser.add_argument('--c3-run', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get('DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB') != '32':
        parser.error('must preserve training verifier memory limit of 32 GiB')
    # Load only after the runner selects the staged, pinned verifier.
    from verl.lean.verifier import verify_with_deepseek_verifier
    args.output_dir.mkdir(exist_ok=False)
    panels = []
    sources = {}
    for label, run, condition in [('c2', args.c2_run, 'c2_unlikeliness_2'),
                                  ('c3', args.c3_run, 'c3_hardblock_restart')]:
        metrics = json.loads((run / 'metrics.json').read_text())
        proof_log = run / 'artifacts/proofs/global_step_604.jsonl'
        digest = sha256(proof_log)
        if (metrics['condition'] != condition or
                metrics['classification'] != 'registered_full_seed42' or
                metrics['completion_marker'] != 'upstream_post_completion_stop_sentinel' or
                metrics['proof_log_sha256'] != digest):
            raise ValueError('source run is not the expected finalized training run')
        sources[label] = {'run': str(run), 'proof_log_sha256': digest,
                          'metrics_sha256': sha256(run / 'metrics.json')}
        panels.extend((f'{label}-step-{step}', rows) for step, rows in select_batches(proof_log).items())
    manifest = {'analysis': 'fixed-proof-verifier-concurrency-v1', 'sources': sources,
                'timeout_seconds': 300, 'memory_limit_gib': 32,
                'actor_loaded': False, 'panels': {name: [r['proposal_id'] for r in rows] for name, rows in panels},
                'schedule': {name: ([32, 64, 64, 32] if i % 2 == 0 else [64, 32, 32, 64])
                             for i, (name, _) in enumerate(panels)}}
    (args.output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    summary = []
    for name, rows in panels:
        passes = []
        for repeat, workers in enumerate(manifest['schedule'][name]):
            samples = [available_kib()]
            stop = threading.Event()
            def monitor():
                while not stop.wait(0.5):
                    samples.append(available_kib())
            thread = threading.Thread(target=monitor, daemon=True)
            thread.start()
            start = time.monotonic()
            try:
                # One theorem per request preserves code assembly and row order,
                # while avoiding reliance on original rows being grouped.
                outputs = verify_with_deepseek_verifier(
                    [r['proof'] for r in rows], [r['theorem_statement'] for r in rows],
                    [r['context'] for r in rows], max_workers=workers, penalize_extra_text=True)
            finally:
                stop.set()
                thread.join()
            elapsed = time.monotonic() - start
            results = [out['candidate_results'][0] for out in outputs]
            if len(results) != len(rows):
                raise ValueError('missing verifier results')
            record = {'panel': name, 'pass': repeat, 'workers': workers, 'seconds': elapsed,
                      'initial_available_kib': samples[0], 'minimum_available_kib': min(samples),
                      'peak_available_memory_drop_kib': samples[0] - min(samples),
                      'correct': sum(r['verdict'] for r in results),
                      'failure_classes': dict(Counter(r['failure_class'] or 'none' for r in results)),
                      'results': results}
            (args.output_dir / f'{name}-pass-{repeat}.json').write_text(json.dumps(record, indent=2) + '\n')
            passes.append(record)
            print(json.dumps({k: v for k, v in record.items() if k != 'results'}), flush=True)
        comparisons = [{**compare(passes[0]['results'], item['results']), 'against_pass': item['pass']}
                       for item in passes[1:]]
        seconds = {str(w): sum(p['seconds'] for p in passes if p['workers'] == w) / 2 for w in (32, 64)}
        summary.append({'panel': name, 'mean_seconds': seconds,
                        'speedup_64_over_32': seconds['32'] / seconds['64'], 'comparisons': comparisons})
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')


if __name__ == '__main__':
    main()
