"""Recheck the two mathematical statements with the project's Lean verifier."""
import argparse
import json
import sys
from pathlib import Path

directory = Path(__file__).resolve().parent
sys.path.insert(0,str(directory.parents[2]/'scripts/project'))
from interface_discovery_pilot import verify_one

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('bundle',type=Path)
args = parser.parse_args()
for name, file in [('two_point_rigidity','rigidity'),('translated_family','family'),('workbook_collision','workbook')]:
    result = verify_one(dict(id=name,code=(directory/(name+'.lean')).read_text(),
        verifier=str(args.bundle/'verifier/DeepSeek-Prover-V1.5'),lake=str(args.bundle/'lean/elan/bin/lake')))
    (directory/(file+'-verdict.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(name,result['accepted'],str(result['errors'])[:1900],flush=True)
    assert result['accepted']
