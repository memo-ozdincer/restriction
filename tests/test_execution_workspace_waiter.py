import argparse
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/project/wait_execution_workspace.py"
spec = importlib.util.spec_from_file_location("execution_workspace_waiter", SCRIPT)
waiter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(waiter)


class WaiterTests(unittest.TestCase):
    def test_owner_account_and_terminal_states_fail_closed(self):
        info = "JobId=1176227 Account=def-zhijing UserId=tester(123) JobState=RUNNING NodeList=node01"
        self.assertEqual(waiter.validate_job(info, 1176227, 123, "tester")["NodeList"], "node01")
        for changed in (info.replace("def-zhijing", "rrg-zhijing"),
                        info.replace("tester(123)", "someone(456)"),
                        info.replace("RUNNING", "COMPLETED"),
                        info.replace("1176227", "1176228")):
            with self.assertRaises(ValueError):
                waiter.validate_job(changed, 1176227, 123, "tester")

    def test_polling_waits_sixty_seconds_then_returns_single_running_state(self):
        statuses = iter([{"JobState": "PENDING"}, {"JobState": "PENDING"},
                         {"JobState": "RUNNING", "NodeList": "node01"}])
        elapsed = [0]
        sleeps = []
        updates = []

        def sleep(seconds):
            sleeps.append(seconds)
            elapsed[0] += seconds

        result = waiter.poll_until_running(lambda: next(statuses),
            lambda *args, **kwargs: updates.append((args, kwargs)),
            monotonic=lambda: elapsed[0], sleep=sleep)
        self.assertEqual(result["NodeList"], "node01")
        self.assertEqual(sleeps, [60, 60])
        self.assertEqual(len(updates), 2)

    def test_wait_deadline_never_invokes_cancellation_or_launch(self):
        elapsed = [0]

        def sleep(seconds):
            elapsed[0] += seconds

        with self.assertRaisesRegex(TimeoutError, "not cancelled"):
            waiter.poll_until_running(lambda: {"JobState": "PENDING"}, lambda *a, **k: None,
                max_wait_seconds=90, monotonic=lambda: elapsed[0], sleep=sleep)
        self.assertEqual(elapsed[0], 90)

    def test_remote_login_command_preserves_every_argument_without_home_override(self):
        args = argparse.Namespace(bundle=Path("/shared/a b;touch injected"),
            panel_dir=Path("/shared/panel$(touch injected)"), output=Path("/shared/output'quoted"),
            job_id=1176227, commit="a" * 40, manifest_sha256="b" * 64)
        command = waiter.ssh_command("node01", Path("/shared/python"), Path("/shared/code space"), args)
        login_command = shlex.split(command[-1])
        self.assertEqual(login_command[:2], ["/bin/bash", "-lc"])
        self.assertEqual(len(login_command), 3)
        self.assertEqual(shlex.split(login_command[2]), [
            "/shared/python", "-B", "-u", "/shared/code space/" + waiter.RUNNER,
            "--bundle", str(args.bundle), "--panel", str(args.panel_dir),
            "--output", str(args.output), "--job-id", str(args.job_id),
            "--commit", args.commit, "--panel-sha256", args.manifest_sha256])
        self.assertIn("BatchMode=yes", command)
        self.assertIn("ServerAliveInterval=30", command)
        self.assertNotIn("HOME=", command[-1])
        for node in ("-oProxyCommand=bad", "node;touch_bad", "node $(bad)"):
            with self.assertRaisesRegex(ValueError, "hostname"):
                waiter.ssh_command(node, Path("python"), Path("code"), args)

    def test_remote_login_shell_executes_literal_paths_without_injection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            python = root / "python 'quoted"
            python.symlink_to(sys.executable)
            snapshot = root / "code space;touch injected_source"
            runner = snapshot / waiter.RUNNER
            runner.parent.mkdir(parents=True)
            runner.write_text("import json, sys\nprint(json.dumps(sys.argv))\n")
            args = argparse.Namespace(bundle=root / "bundle; touch injected_bundle",
                panel_dir=root / "panel$(touch injected_panel)",
                output=root / "output'quoted`touch injected_output`",
                job_id=1176227, commit="a" * 40, manifest_sha256="b" * 64)
            command = waiter.ssh_command("node01", python, snapshot, args)
            # Emulate SSH's remote shell, including the nested Bash login shell.
            result = subprocess.run(["/bin/sh", "-c", command[-1]], cwd=root,
                                    capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout), [str(runner),
                "--bundle", str(args.bundle), "--panel", str(args.panel_dir),
                "--output", str(args.output), "--job-id", str(args.job_id),
                "--commit", args.commit, "--panel-sha256", args.manifest_sha256])
            self.assertEqual(list(root.glob("injected_*")), [])

    def test_transport_failure_is_attempted_once_and_marker_prevents_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = []

            def execute(command, **kwargs):
                calls.append(command)
                return subprocess.CompletedProcess(command, 255)

            arguments = (["ssh", "node"], root / "attempt.json", {"node": "node"},
                         root / "ssh.log", lambda *a, **k: None)
            with self.assertRaisesRegex(RuntimeError, "may have started"):
                waiter.launch_once(*arguments, execute=execute)
            with self.assertRaises(FileExistsError):
                waiter.launch_once(*arguments, execute=execute)
            self.assertEqual(len(calls), 1)
            self.assertTrue(json.loads((root / "attempt.json").read_text())["launch_attempted"])

    def test_snapshot_is_pinned_and_readonly_and_requires_runner_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            for relative in (waiter.RUNNER, waiter.ANALYZER):
                path = repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("print('pinned')\n")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.com",
                            "commit", "-qm", "source"], check=True)
            commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            (repo / waiter.RUNNER).write_text("print('mutable working tree')\n")
            watcher = root / "watcher"
            watcher.mkdir()
            snapshot, digest = waiter.prepare_snapshot(repo, commit, watcher)
            self.assertEqual((snapshot / waiter.RUNNER).read_text(), "print('pinned')\n")
            self.assertEqual((snapshot / waiter.RUNNER).stat().st_mode & 0o222, 0)
            self.assertEqual(digest, waiter.sha256(watcher / "source.tar"))
            with self.assertRaisesRegex(ValueError, "40-character"):
                waiter.prepare_snapshot(repo, commit[:8], watcher)

    def test_completed_logs_require_fresh_witness_and_exact_output_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "generation_complete.json").write_text(json.dumps({
                "trained_samples": 0, "status": "generation_complete_pending_independent_analysis"}))
            (root / "witness_checks.json").write_text(json.dumps({"complete": True, "invalid_tasks": []}))
            for label in ("practice", "diagnostic"):
                folder = root / label
                folder.mkdir()
                proof = folder / "proof.jsonl"
                proof.write_text("{}\n")
                (folder / "process_status.json").write_text(json.dumps({"completion_candidate": True,
                    "timed_out": False, "proof_log": str(proof), "proof_log_sha256": waiter.sha256(proof)}))
            logs, certificates = waiter.completed_logs(root)
            self.assertEqual(set(logs), {"practice", "diagnostic"})
            self.assertEqual(len(certificates), 4)
            (root / "witness_checks.json").write_text(json.dumps({"complete": True, "invalid_tasks": ["bad"]}))
            with self.assertRaisesRegex(ValueError, "witness"):
                waiter.completed_logs(root)
            (root / "witness_checks.json").write_text(json.dumps({"complete": True, "invalid_tasks": []}))
            (root / "practice/proof.jsonl").write_text("corrupted")
            with self.assertRaisesRegex(ValueError, "changed"):
                waiter.completed_logs(root)


if __name__ == "__main__":
    unittest.main()
