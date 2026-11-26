"""Independently verify C++ experiment traces by exhaustive assignments."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter

GATES = [(s, d) for s in range(4) for d in range(4) if s != d]

def perm(word):
    out = list(range(16))
    for g in word:
        src, dst = GATES[g]
        out = [x ^ ((((x >> src) & 1)) << dst) for x in out]
    return tuple(out)

def audit(path: Path):
    count = Counter()
    dataset = json.loads(Path(str(path)+'.dataset.json').read_text())
    maps = set()
    for name, words in dataset.items():
        for word in words:
            p = perm(word)
            assert p not in maps
            maps.add(p)
    for line in Path(str(path)+'.traces.jsonl').read_text().splitlines():
        row = json.loads(line)
        assert row["root"] == dataset[row["split"]][row["root_id"]]
        w = row["root"][:]
        p = perm(w)
        motif, lengths, nonshortening = 0, [], []
        for t, (pos, n, rhs) in enumerate(row["edits"]):
            assert 0 <= pos <= len(w)
            assert 0 <= n <= 3 and len(rhs) <= 3
            if n == 0:
                assert not rhs
            else:
                assert pos+n <= len(w)
                lhs = w[pos:pos+n]
                assert lhs != rhs
                assert perm(lhs) == perm(rhs)
            if t < row["prefix"]:
                assert len(rhs) >= n
            if row["ablate"]:
                assert n == 0 or len(rhs) < n
            nonshortening.append(t >= row["prefix"] and n > 0 and len(rhs) >= n)
            w[pos:pos+n] = rhs
            assert len(w) <= 40
            assert perm(w) == p
            lengths.append(len(w))
        prior = len(row["root"])
        for t, length in enumerate(lengths):
            prior = min(prior, length)
            if nonshortening[t] and any(x < prior for x in lengths[t+1:t+6]):
                motif += 1
        assert motif == row["motifs"]
        assert row["end"] == w
        count[row["label"]] += 1
    result = json.loads(Path(str(path)+'.json').read_text())
    assert result["common"]["training"]["verified"] == result["common"]["training"]["episodes"]
    for arm in result["arms"]:
        for key in ["phase_training", "tail_training", "phase_eval", "test", "ablated", "long_test"]:
            st = arm[key]
            assert st["verified"] == st["episodes"]
            assert st["reset"] + st["learned"] == st["episodes"] * 24
            assert st["proposals"] == 32 * st["episodes"] * 24
            assert sum(st["bycost"]) == st["episodes"]
            assert sum(st["motif_bycost"]) == st["motifepisodes"]
            if key == "phase_training":
                if arm["name"] == "exposure":
                    assert st["reset"] == st["episodes"] * 6
                    assert st["resetcost"] >= st["episodes"] * 24
                else:
                    assert st["reset"] == 0
            if key == "tail_training":
                assert st["reset"] == 0
    return dict(seed=result["seed"], unique_target_maps=len(maps), traces=dict(count), verified=sum(count.values()))

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("prefix", nargs="+", type=Path)
    args=p.parse_args()
    print(json.dumps([audit(x) for x in args.prefix],indent=2))
