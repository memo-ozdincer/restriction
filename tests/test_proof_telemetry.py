import unittest
from unittest.mock import patch

from verl.lean.telemetry import build_proposal_telemetry, telemetry_identity
import verl.lean.verifier as verifier


class ProposalTelemetryTests(unittest.TestCase):
    def _record(self, theorem_index=0, candidate_index=0):
        config_hash, environment_hash = telemetry_identity(
            '{"seed":42}', {"git_commit": "abc", "model_revision": "def"}
        )
        return build_proposal_telemetry(
            run_id="c0",
            batch_id="c0:step-1",
            theorem_index=theorem_index,
            candidate_index=candidate_index,
            theorem_name="Example.t",
            theorem_statement="theorem t : True := by",
            context="",
            proof="by\n  trivial\n```",
            response_token_count=7,
            verifier_result={
                "verdict": True,
                "lean_complete": True,
                "parse_time_seconds": 0.001,
                "queue_wait_time_seconds": 0.25,
                "verification_time_seconds": 1.5,
                "worker_id": 3,
                "failure_class": None,
                "timed_out": False,
                "verifier_error": None,
            },
            resolved_config_sha256=config_hash,
            environment_sha256=environment_hash,
        )

    def test_record_is_deterministic_and_contains_observational_fields(self):
        first = self._record()
        self.assertEqual(first, self._record())
        self.assertEqual(first["token_count"], 7)
        self.assertEqual(first["queue_wait_time"], 0.25)
        self.assertEqual(first["verification_time"], 1.5)
        self.assertEqual(first["worker_id"], 3)
        for key in (
            "proposal_id", "theorem_hash", "proof_hash", "batch_id",
            "parse_time", "verdict", "failure_class", "timed_out",
            "tactic_prefix_signature", "config_hash", "environment_hash",
        ):
            self.assertIn(key, first)

    def test_padded_duplicate_theorem_positions_have_distinct_proposal_ids(self):
        self.assertNotEqual(
            self._record(theorem_index=0)["proposal_id"],
            self._record(theorem_index=1)["proposal_id"],
        )

    def test_environment_hash_is_bound_to_resolved_config(self):
        _, environment_a = telemetry_identity("config-a", {"git_commit": "abc"})
        _, environment_b = telemetry_identity("config-b", {"git_commit": "abc"})
        self.assertNotEqual(environment_a, environment_b)


class _FakeScheduler:
    outputs = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def submit_all_request(self, code_files):
        self.code_files = code_files
        return list(range(len(code_files)))

    def get_all_request_outputs(self, request_ids):
        return self.outputs

    def close(self):
        pass


class VerifierTelemetryTests(unittest.TestCase):
    def test_candidate_taxonomy_preserves_success_indices(self):
        _FakeScheduler.outputs = [
            {"complete": True, "system_errors": "", "verify_time": 1.0,
             "queue_wait_time": 0.1, "worker_id": 0},
            {"complete": False, "system_errors": "", "verify_time": 2.0,
             "queue_wait_time": 0.2, "worker_id": 1},
            {"complete": False, "system_errors": "subprocess.TimeoutExpired",
             "verify_time": 300.0, "queue_wait_time": 0.3, "worker_id": 2},
            {"complete": False, "system_errors": "", "verify_time": 0.1,
             "queue_wait_time": 0.4, "worker_id": 3},
        ]
        proofs = [
            "by\n  trivial\n```",
            "by\n  exact False.elim (by contradiction)\n```",
            "by\n  aesop\n```",
            "by\n  trivial",  # no closing code fence: wrapper parse failure
        ]
        with patch.object(verifier, "Lean4ServerScheduler", _FakeScheduler):
            output = verifier.verify_with_deepseek_verifier(
                proofs, ["theorem t : True := "], [""], max_workers=4
            )[0]

        self.assertEqual(output["success_indices"], [0])
        candidates = output["candidate_results"]
        self.assertEqual([item["verdict"] for item in candidates], [True, False, False, False])
        self.assertEqual(
            [item["failure_class"] for item in candidates],
            [None, "lean_rejected", "timeout", "proof_parse_failure"],
        )
        self.assertTrue(candidates[2]["timed_out"])
        self.assertEqual(candidates[0]["verification_time_seconds"], 1.0)
        self.assertEqual(candidates[0]["queue_wait_time_seconds"], 0.1)
        self.assertEqual(candidates[0]["worker_id"], 0)


if __name__ == "__main__":
    unittest.main()
