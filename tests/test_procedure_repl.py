"""Protocol/integrity tests. Actual pinned Lean evidence is produced by --output demo."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/project/procedure_repl.py"
spec = importlib.util.spec_from_file_location("procedure_repl", SCRIPT)
repl = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = repl
spec.loader.exec_module(repl)


FAKE = '''
import json, sys, time
env, proof = 0, 0
while True:
    line = sys.stdin.readline()
    if not line:
        break
    if not line.strip():
        continue
    q = json.loads(line)
    if q.get("tactic") == "sleep":
        time.sleep(3)
    if q.get("tactic") == "bad":
        r = {"message": "Lean error: bad tactic"}
    elif "cmd" in q:
        r = {"env": env}
        env += 1
        if "rfl" in q["cmd"]:
            before = q["cmd"].split("rfl", 1)[0]
            row, col = before.count("\\n") + 1, len(before.rsplit("\\n", 1)[-1])
            r["tactics"] = [{"proofState": proof, "goals": "α : Nat\\n⊢ α = α",
                             "tactic": "rfl", "pos": {"line": row, "column": col},
                             "endPos": {"line": row, "column": col + 3}}]
            proof += 1
    else:
        r = {"proofState": proof, "goals": []}
        proof += 1
    sys.stdout.write(json.dumps(r, indent=2) + "\\n\\n")
    sys.stdout.flush()
'''


class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        binary = self.root / "repl"
        binary.write_text(f"#!{sys.executable}\n" + textwrap.dedent(FAKE))
        binary.chmod(0o755)
        self.runtime = {"sha256": "test-runtime", "repl": str(binary),
                        "lean_path": "", "elan_home": str(self.root), "project": str(self.root)}
        self.recorders = []

    def tearDown(self):
        for recorder in self.recorders:
            recorder.close()
        self.tmp.cleanup()

    def recorder(self, name="session", **kwargs):
        recorder = repl.Recorder(self.runtime, self.root / name, **kwargs)
        self.recorders.append(recorder)
        return recorder

    def fixture(self, recorder):
        env, _, _ = recorder.command(b"import Mathlib\n")
        source = "theorem test (α : Nat) : α = α := by rfl\n".encode()
        final_env, states, _ = recorder.command(source, env)
        return source, env, final_env, states[0]

    def test_unicode_spans_pre_states_and_environment_survive_protocol(self):
        recorder = self.recorder()
        source, env, final_env, state = self.fixture(recorder)
        self.assertEqual(source[state.start_byte:state.end_byte], b"rfl")
        self.assertEqual(state.phase, "pre_tactic")
        self.assertEqual(final_env.commands, (0, 1))
        request = json.loads((recorder.output / "request-0001.json").read_bytes())
        self.assertEqual(request["env"], env.id)
        self.assertTrue(request["allTactics"])
        self.assertEqual((recorder.output / "source-0001.lean").read_bytes(), source)
        after, response = recorder.step(state, expected_environment_sha256=final_env.sha256)
        self.assertEqual(response["goals"], [])
        self.assertEqual(after.phase, "after_step")
        with self.assertRaisesRegex(repl.RecorderError, "PRE-tactic"):
            recorder.step(after)
        raw = (recorder.output / "response-0002.raw").read_bytes()
        self.assertTrue(raw.endswith(b"\n\n"))

    def test_foreign_handles_and_wrong_environment_fail_before_lean_call(self):
        recorder, other = self.recorder(), self.recorder("other")
        _, env, _, state = self.fixture(recorder)
        for action in (lambda: other.step(state), lambda: other.command(b"check", env)):
            with self.assertRaisesRegex(repl.RecorderError, "wrong session"):
                action()
        self.assertEqual(other.exchanges, 0)
        with self.assertRaisesRegex(repl.RecorderError, "wrong environment"):
            recorder.step(state, expected_environment_sha256=env.sha256)
        self.assertEqual(recorder.exchanges, 2)
        with self.assertRaisesRegex(repl.RecorderError, "unsupported cut"):
            recorder.certify_cut(state)

    def test_exact_replay_fresh_session_and_source_integrity(self):
        original, replay = self.recorder(), self.recorder("replay")
        _, _, final_env, state = self.fixture(original)
        recovered = replay.replay(original.output, 1, 0)
        self.assertNotEqual(recovered.session, state.session)
        self.assertEqual(recovered.environment_sha256, final_env.sha256)
        self.assertEqual(replay.step(recovered)[1]["goals"], [])
        (original.output / "source-0001.lean").write_bytes(b"changed")
        with self.assertRaisesRegex(repl.RecorderError, "checksum mismatch"):
            replay.replay(original.output, 1, 0)
        with self.assertRaisesRegex(repl.RecorderError, "checksum mismatch"):
            original.step(state)

    def test_wrong_runtime_replay_and_existing_directory_refused(self):
        original, replay = self.recorder(), self.recorder("replay")
        self.fixture(original)
        replay.runtime = {**self.runtime, "sha256": "changed"}
        with self.assertRaisesRegex(repl.RecorderError, "wrong environment/toolchain"):
            replay.replay(original.output, 1, 0)
        self.assertEqual(replay.exchanges, 0)
        with self.assertRaises(FileExistsError):
            repl.Recorder(self.runtime, original.output)

    def test_errors_preserve_raw_response_and_timeout_terminates(self):
        recorder = self.recorder(timeout=0.5)
        _, _, _, state = self.fixture(recorder)
        with self.assertRaisesRegex(repl.RecorderError, "bad tactic"):
            recorder.step(state, "bad")
        self.assertIn(b"bad tactic", (recorder.output / "response-0002.raw").read_bytes())
        with self.assertRaisesRegex(repl.RecorderError, "timeout; session terminated"):
            recorder.step(state, "sleep")
        recorder.process.wait(timeout=3)
        self.assertIsNotNone(recorder.process.returncode)
        self.assertTrue((recorder.output / "response-0003.raw").exists())


class SourcePositionTests(unittest.TestCase):
    def test_multibyte_and_line_boundaries(self):
        source = "-- λ\nα := β\n".encode()
        self.assertEqual(source[repl.byte_offset(source, {"line": 2, "column": 5}):], "β\n".encode())
        self.assertEqual(repl.byte_offset(source, {"line": 3, "column": 0}), len(source))
        # Lean 4.9 FileMap.toPosition falls back to byte offsets on its last line.
        self.assertEqual(repl.byte_offset("α rfl".encode(), {"line": 1, "column": 3}), 3)
        for pos in ({"line": 0, "column": 0}, {"line": 4, "column": 0}, {"line": 1, "column": 99}):
            with self.assertRaises(repl.RecorderError):
                repl.byte_offset(source, pos)


if __name__ == "__main__":
    unittest.main()
