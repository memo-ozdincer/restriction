import unittest
import contextlib
import io
import json
from pathlib import Path
import tempfile
import types
from unittest.mock import patch
from scripts.project.benchmark_verifier_workers import compare, main, sha256


class WorkerBenchmarkTests(unittest.TestCase):
    def test_separates_verdict_and_failure_class_changes(self):
        a = [{'verdict': True, 'failure_class': None}, {'verdict': False, 'failure_class': 'timeout'}]
        b = [{'verdict': False, 'failure_class': 'timeout'}, {'verdict': False, 'failure_class': 'lean_rejected'}]
        self.assertEqual(compare(a, b), {'verdict_disagreements': 1, 'failure_class_disagreements': 2})

    def test_rejects_unaligned_results(self):
        with self.assertRaises(ValueError):
            compare([], [{'verdict': True, 'failure_class': None}])


class WorkerBenchmarkIntegrationTests(unittest.TestCase):
    """Exercise the real driver and file handling with a fake Lean backend."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for label, condition in [('c2', 'c2_unlikeliness_2'), ('c3', 'c3_hardblock_restart')]:
            run = self.root / label
            proof_log = run / 'artifacts/proofs/global_step_604.jsonl'
            proof_log.parent.mkdir(parents=True)
            with proof_log.open('w') as stream:
                for step in (100, 550):
                    for index in range(512):
                        row = {'batch_id': f'fixture:step-{step}',
                               'proposal_id': f'{label}-{step}-{index}',
                               'proof': f'proof-{step}-{index}',
                               'theorem_statement': f'theorem-{index // 32}', 'context': ''}
                        stream.write(json.dumps(row) + '\n')
            (run / 'metrics.json').write_text(json.dumps({
                'condition': condition, 'classification': 'registered_full_seed42',
                'completion_marker': 'upstream_post_completion_stop_sentinel',
                'proof_log_sha256': sha256(proof_log)}))
        self.output = self.root / 'output'
        self.calls = []

    def backend(self, proofs, statements, contexts, **kwargs):
        self.calls.append((proofs, statements, contexts, kwargs))
        return [{'candidate_results': [{'verdict': True, 'failure_class': None}]} for _ in proofs]

    def invoke(self, backend=None):
        module = types.ModuleType('verl.lean.verifier')
        module.verify_with_deepseek_verifier = backend or self.backend
        argv = ['benchmark', '--c2-run', str(self.root / 'c2'),
                '--c3-run', str(self.root / 'c3'), '--output-dir', str(self.output)]
        with patch('sys.argv', argv), patch.dict('sys.modules', {'verl.lean.verifier': module}), \
                patch.dict('os.environ', {'DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB': '32'}), \
                contextlib.redirect_stdout(io.StringIO()):
            main()

    def test_identical_inputs_counterbalanced_schedule_and_complete_outputs(self):
        self.invoke()
        expected = [32, 64, 64, 32, 64, 32, 32, 64] * 2
        self.assertEqual([c[3]['max_workers'] for c in self.calls], expected)
        self.assertTrue(all(c[3]['penalize_extra_text'] for c in self.calls))
        for start in range(0, 16, 4):
            self.assertTrue(all(c[:3] == self.calls[start][:3] for c in self.calls[start:start+4]))
        self.assertEqual(len(list(self.output.glob('*-pass-*.json'))), 16)
        summary = json.loads((self.output / 'summary.json').read_text())
        self.assertEqual(len(summary), 4)
        self.assertTrue(all(c['verdict_disagreements'] == 0 for p in summary for c in p['comparisons']))

    def test_completed_pass_survives_later_backend_failure(self):
        def fail_second(*args, **kwargs):
            if self.calls:
                raise RuntimeError('injected failure')
            return self.backend(*args, **kwargs)
        with self.assertRaisesRegex(RuntimeError, 'injected failure'):
            self.invoke(fail_second)
        self.assertTrue((self.output / 'c2-step-100-pass-0.json').is_file())
        self.assertFalse((self.output / 'summary.json').exists())

    def test_source_corruption_rejected_before_verification(self):
        proof_log = self.root / 'c2/artifacts/proofs/global_step_604.jsonl'
        with proof_log.open('a') as stream:
            stream.write('\n')
        with self.assertRaisesRegex(ValueError, 'source run'):
            self.invoke()
        self.assertEqual(self.calls, [])

    def test_existing_output_is_never_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / 'preserve.txt'
        sentinel.write_text('original')
        with self.assertRaises(FileExistsError):
            self.invoke()
        self.assertEqual(sentinel.read_text(), 'original')
        self.assertEqual(self.calls, [])
