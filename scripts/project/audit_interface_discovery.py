#!/usr/bin/env python3
"""Audit a completed pilot against its frozen requests; retain full group counts."""
import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--panel', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run = args.workspace / 'experiment'
    status = json.loads((run / 'status.json').read_text())
    if status['state'] != 'complete':
        raise RuntimeError('Only a completed run can receive a complete audit')
    spec = importlib.util.spec_from_file_location('frozen_pilot', args.workspace / 'pilot.py')
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    groups = defaultdict(list)
    sources = {}
    for model in ('base', 'grpo'):
        for phase in ('producer', 'bare', 'consumer'):
            raw_path = run / f'{model}-{phase}.jsonl'
            verdict_path = run / f'{model}-{phase}-verified.jsonl'
            rows, verdicts = read_rows(raw_path), read_rows(verdict_path)
            for path in (raw_path, verdict_path):
                sources[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
            by_id = {row['id']: row for row in rows}
            checked = {row['id']: row for row in verdicts}
            if len(by_id) != len(rows) or len(checked) != len(verdicts) or by_id.keys() != checked.keys():
                raise RuntimeError('Duplicate or unmatched records: ' + raw_path.name)
            requests = pilot.generation_requests(SimpleNamespace(
                phase=phase, panel=args.panel, artifacts=run / 'selected-artifacts.json'))
            expected_ids = set()
            for request in requests:
                for index in range(request['samples']):
                    identity = f"{model}/{request['id']}/{index}"
                    expected_ids.add(identity)
                    row = by_id[identity]
                    if any(row[key] != value for key, value in request.items() if key != 'id'):
                        raise RuntimeError('Frozen request differs: ' + identity)
                    if row['sample_index'] != index or row['model'] != model:
                        raise RuntimeError('Sample identity differs: ' + identity)
                    verdict = checked[identity]
                    body, error = pilot.completion_code(row['text'], phase == 'producer')
                    if error:
                        if verdict.get('parse_error') != error or verdict['accepted']:
                            raise RuntimeError('Parser verdict differs: ' + identity)
                    else:
                        theorem = 'reusable_fact' if phase == 'producer' else 'target'
                        code = row['prompt'].removeprefix(pilot.PREFIX) + body
                        code += '\n#print axioms ' + theorem + '\n'
                        if pilot.sha(code) != verdict['code_sha256']:
                            raise RuntimeError('Verified source differs: ' + identity)
                    if verdict['accepted'] and (not verdict['lean_complete'] or
                            not verdict['axiom_audit_found'] or
                            not set(verdict['axioms']) <= pilot.ALLOWED_AXIOMS):
                        raise RuntimeError('Acceptance audit failed: ' + identity)
                    key = (model, row['kind'], row['world'], row.get('target', ''), row['condition'])
                    groups[key].append((row, verdict))
            if expected_ids != by_id.keys():
                raise RuntimeError('Unexpected samples: ' + raw_path.name)
    table = []
    for key, pairs in sorted(groups.items()):
        texts = Counter(row['text'] for row, _ in pairs)
        good = next((row for row, verdict in pairs if verdict['accepted']), None)
        table.append(dict(zip(('model', 'kind', 'world', 'target', 'condition'), key)) | {
            'proposals': len(pairs), 'correct': sum(v['accepted'] for _, v in pairs),
            'parse_rejections': sum(bool(v.get('parse_error')) for _, v in pairs),
            'system_errors': sum(bool(v.get('system_errors')) for _, v in pairs),
            'timeouts': sum('TimeoutExpired' in str(v.get('system_errors', '')) for _, v in pairs),
            'physical_lean_calls': sum('lean_complete' in v for _, v in pairs),
            'unique_completion_texts': len(texts), 'largest_identical_text_count': max(texts.values()),
            'generated_tokens': sum(r['generated_tokens'] for r, _ in pairs),
            'supplied_tokens': sum(r['prompt_tokens'] for r, _ in pairs),
            'first_correct': ({k: good[k] for k in ('id', 'prompt', 'text')} if good else None),
        })
    output = {'complete_request_and_source_audit': True, 'job_id': status['job_id'],
              'source_sha256': sources, 'groups': table,
              'total_proposals': sum(g['proposals'] for g in table),
              'total_system_errors': sum(g['system_errors'] for g in table),
              'note': 'Correctness uses saved kernel verdicts; this audit does not rerun Lean.'}
    with args.output.open('x') as stream:
        json.dump(output, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in output.items() if k not in ('groups', 'source_sha256')}))


if __name__ == '__main__':
    main()
