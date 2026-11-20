import json
from pathlib import Path
import tempfile
import unittest

from scripts.project import cross_context_credit as credit


class CrossContextCreditTests(unittest.TestCase):
    def test_incorrect_source_never_receives_transfer_credit(self):
        self.assertEqual(credit.rewards(False, [True, True, True]), (0., 0.))
        self.assertEqual(credit.rewards(True, [True, False, True]), (1., 2/3))
        with self.assertRaises(ValueError):
            credit.rewards(True, [True, None, True])

    def test_model_requests_exclude_witnesses_and_existing_eval_graphs(self):
        tasks = credit.bank()
        requests = credit.requests(tasks)
        self.assertEqual(len(requests), 20)
        self.assertEqual(sum(r['samples'] for r in requests), 320)
        self.assertEqual({t['scope'] for t in tasks}, {'training_only'})
        for task, request in zip(tasks, requests):
            self.assertTrue(request['prompt'].endswith(task['statement']))
            self.assertNotIn(task['witness'], request['prompt'])
            self.assertNotIn('orbit', request['prompt'])
            self.assertNotIn('op_', request['prompt'])

    def test_timeouts_do_not_manufacture_brittleness_or_gate_success(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            edges, verdicts = [], []
            # Two families, each with a robust local success and an apparently
            # brittle one whose peer verdict is actually unresolved.
            for family in ('a', 'b'):
                for candidate in ('robust', 'uncertain'):
                    for index in range(4):
                        key = family + candidate + str(index)
                        edges.append({'proposal_id': family + candidate, 'source': family+'0',
                            'target': family+str(index), 'family': family,
                            'code_sha256': key, 'parse_error': None})
                        verdicts.append({'id': key, 'accepted': candidate == 'robust' or index == 0,
                            'system_errors': 'TimeoutExpired' if candidate == 'uncertain' and index == 1 else None})
            (out/'edges.json').write_text(json.dumps(edges))
            (out/'verdicts.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in verdicts))
            credit.summarize(out)
            result = json.loads((out/'analysis.json').read_text())
            self.assertFalse(result['signal_gate_passed'])
            uncertain = [r for r in result['proposals'] if r['id'].endswith('uncertain')]
            self.assertTrue(all(r['cross_reward'] is None for r in uncertain))
            # Resolve those same judgments as real kernel rejections: now the
            # proposed reward has a contrast in both families.
            for verdict in verdicts:
                verdict['system_errors'] = None
            (out/'verdicts.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in verdicts))
            credit.summarize(out)
            self.assertTrue(json.loads((out/'analysis.json').read_text())['signal_gate_passed'])


if __name__ == '__main__':
    unittest.main()
