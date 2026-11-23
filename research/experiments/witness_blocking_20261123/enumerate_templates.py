"""Enumerate translated three-point witnesses up to swapping sets and reflection."""
from collections import defaultdict
from itertools import combinations
import json


def enumerate_templates(max_width):
    buckets = defaultdict(list)
    for triple in combinations(range(max_width+1), 3):
        buckets[sum(triple), sum(x*x for x in triple)].append(triple)
    result = set()
    for bucket in buckets.values():
        for left,right in combinations(bucket,2):
            if set(left).intersection(right) or min(left+right) != 0:
                continue
            width = max(left+right)
            reflected = [tuple(sorted(width-x for x in triple)) for triple in (left,right)]
            result.add(min(tuple(sorted((left,right))), tuple(sorted(reflected))))
    return sorted(result, key=lambda pair:(max(pair[0]+pair[1]),pair))


if __name__ == '__main__':
    print(json.dumps(enumerate_templates(12), indent=2))
