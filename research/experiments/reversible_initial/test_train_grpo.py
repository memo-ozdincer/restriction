import json
import unittest
from collections import Counter

from environment import distances, execute, identity
from train_grpo import training_rows, reward_records, summarize


class CircuitGRPOTests(unittest.TestCase):
    def test_matched_arms(self):
        a, b = (training_rows(arm, 512) for arm in ('identity', 'exploratory'))
        a, b = ([json.loads(r['circuit_json']) for r in rows] for rows in (a,b))
        goal = tuple(a[0]['target'])
        expected = distances(3, goal)
        self.assertEqual(expected[identity(3)], 8)
        self.assertEqual(len(a), len(b))
        self.assertTrue(all(tuple(r['current']) == identity(3) for r in a))
        self.assertGreater(len({tuple(r['current']) for r in b}), 490)
        self.assertTrue(all(tuple(r['current']) != goal for r in b))
        for x, y in zip(a,b):
            self.assertEqual((x['budget'], x['target'], x['group_id']), (y['budget'], y['target'], y['group_id']))
            self.assertEqual(expected[tuple(y['current'])], y['exact_distance'])
        self.assertEqual(Counter(r['exact_distance'] for r in b), {2:3,3:11,4:37,5:117,6:211,7:130,8:3})

    def test_rewards_are_state_dependent(self):
        start = identity(3)
        target = execute(3, [(0, ())], start)
        row = dict(current=start,target=target,budget=8,exact_distance=1,group_id=0)
        answer = '{"actions":[{"target":0,"controls":[]}]}'
        rows = reward_records([[{'role':'assistant','content':answer}], 'garbage'], [json.dumps(row)]*2)
        self.assertEqual([r['reward'] for r in rows], [1,0])
        self.assertEqual(summarize(rows)['pass_at_1'], 0.5)
        row['current'] = target
        self.assertEqual(reward_records([answer], [json.dumps(row)])[0]['reward'], 0)

    def test_no_oracle_in_prompt(self):
        for row in training_rows('exploratory', 8):
            query = row['prompt'][0]['content']
            self.assertNotIn('exact_distance', query)
            self.assertNotIn('group_id', query)
            self.assertEqual(set(json.loads(query.rsplit('\n',1)[1])), {'current','target','budget'})

    def test_empty_or_incorrect_completions(self):
        row = training_rows('identity', 1)[0]['circuit_json']
        for completion in ('', '{}', 'null', [{'role':'assistant','content':None}], [None]):
            self.assertEqual(reward_records([completion],[row])[0]['reward'], 0)
        with self.assertRaises(ValueError):
            reward_records([''], [])


if __name__ == '__main__':
    unittest.main()
