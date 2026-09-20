#!/usr/bin/env python3
"""Archive small textual run evidence; inventory but do not bundle large data."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(exist_ok=False)
    inventory = []
    suffixes = {'.md', '.json', '.log', '.yaml', '.yml', '.sh', '.sbatch', '.txt', '.tsv'}
    with tarfile.open(args.output / 'run-provenance.tar.gz', 'w:gz') as archive:
        for path in sorted(args.runs.rglob('*')):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(args.runs)
            size = path.stat().st_size
            include = (path.suffix in suffixes and size <= 16 * 1024 * 1024
                       and not {'actor', 'critic', 'train_batch_buffer'} & set(relative.parts))
            row = {'path': str(relative), 'bytes': size, 'included_in_archive': include}
            if include:
                row['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                archive.add(path, arcname=str(relative), recursive=False)
            else:
                row['reason_not_archived'] = 'large or non-textual artifact, dataset, raw proof log, or model state'
            inventory.append(row)
    report = {'scope': str(args.runs.resolve()), 'files': inventory,
              'included_files': sum(r['included_in_archive'] for r in inventory),
              'unarchived_files': sum(not r['included_in_archive'] for r in inventory),
              'warning': 'An inventory does not back up excluded files. External models and environments are outside scope.'}
    (args.output / 'run-inventory.json').write_text(json.dumps(report, indent=2) + '\n')
    for path in sorted(args.output.iterdir()):
        print(path.name, path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
