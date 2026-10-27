#!/usr/bin/env python3
"""CPU-only persistent Lean state recorder; never a correctness/reward verifier.

allTactics handles denote PRE-tactic states. Handles belong to one live process.
Durability comes from exact command replay, not integer IDs or printed-goal hashes.
This instrument does not extract/certify cuts or infer semantic state equality.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
import queue
import shutil
import subprocess
import threading
import time
import uuid


class RecorderError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n").encode()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def byte_offset(source: bytes, position: dict) -> int:
    """Match pinned FileMap: codepoint columns, except final line's byte fallback."""
    lines = source.decode("utf-8").split("\n")
    line, col = position["line"] - 1, position["column"]
    if line < 0 or line >= len(lines) or col < 0:
        raise RecorderError("invalid source position")
    prefix = ("\n".join(lines[:line]) + ("\n" if line else "")).encode()
    if line == len(lines) - 1:
        tail = lines[line].encode()
        if col > len(tail):
            raise RecorderError("invalid source position")
        try:
            tail[:col].decode()
        except UnicodeDecodeError as exc:
            raise RecorderError("source position splits UTF-8 character") from exc
        return len(prefix) + col
    if col > len(lines[line]):
        raise RecorderError("invalid source position")
    return len(prefix) + len(lines[line][:col].encode())


def capture_runtime(project: Path, elan_home: Path) -> dict:
    """Hash the complete available .olean/.so search universe, not just git IDs.

    This intentionally fingerprints a superset of imported modules. Absolute
    roots are part of the identity. A copied installation must be re-audited.
    Files must remain immutable while the recorded session is running.
    """
    project, elan_home = project.resolve(), elan_home.resolve()
    env = {**os.environ, "ELAN_HOME": str(elan_home),
           "PATH": str(elan_home / "bin") + os.pathsep + os.environ.get("PATH", "")}
    lake = str(elan_home / "bin/lake")
    def query(*args):
        return subprocess.check_output([lake, "env", *args], cwd=project, env=env,
                                       stderr=subprocess.PIPE, text=True).strip()
    lean_path = query("printenv", "LEAN_PATH")
    prefix = Path(query("lean", "--print-prefix"))
    version = query("lean", "--version")
    repl = project / ".lake/packages/REPL/.lake/build/bin/repl"
    # Prefer host coreutils: cluster module versions may preload a newer libc
    # shim that the prebuilt Lean executable cannot load.
    stdbuf = shutil.which("stdbuf", path=os.defpath) or shutil.which("stdbuf")
    if stdbuf is None:
        raise RecorderError("stdbuf is required for the pinned REPL's buffered stdout")
    printenv = shutil.which("printenv", path=os.defpath)
    if printenv is None:
        raise RecorderError("host printenv is required to inventory the stdbuf preload")
    preload = subprocess.check_output([stdbuf, "-oL", printenv, "LD_PRELOAD"],
                                      text=True, env=env).strip().replace(":", " ").split()
    if not preload or any(not Path(p).is_absolute() for p in preload):
        raise RecorderError("cannot resolve the actual stdbuf preload library")
    roots = {prefix / "lib/lean"}
    roots.update((project / p).resolve() for p in lean_path.split(os.pathsep) if p)
    files = {project / "lean-toolchain", project / "lake-manifest.json",
             project / "lakefile.lean", prefix / "bin/lean", prefix / "bin/lake", repl, Path(stdbuf)}
    files.update(Path(p) for p in preload)
    missing_roots = []
    for root in sorted(roots):
        if not root.is_dir():
            missing_roots.append(str(root))
            continue
        files.update(root.rglob("*.olean"))
        files.update(root.rglob("*.so"))
    files.update((project / ".lake/packages/REPL/REPL").rglob("*.lean"))
    inventory = [{"path": str(p), "bytes": p.stat().st_size, "sha256": file_hash(p)}
                 for p in sorted(files)]
    data = {"project": str(project), "elan_home": str(elan_home), "repl": str(repl),
            "lean_path": lean_path, "lean_version": version, "files": inventory, "stdbuf": stdbuf,
            "stdbuf_preload": preload,
            "missing_search_roots": missing_roots,
            "scope": "all available olean/so files, Lean/lake/REPL binaries, REPL sources and lock/config files"}
    return {**data, "sha256": digest(json_bytes(data))}


@dataclass(frozen=True)
class Environment:
    session: str
    id: int
    sha256: str
    commands: tuple[int, ...]


@dataclass(frozen=True)
class Snapshot:
    session: str
    id: int
    environment_sha256: str
    command: int
    tactic_index: int
    start_byte: int
    end_byte: int
    phase: str = "pre_tactic"


# This is a conservative eligibility check, NOT frame independence certification.
# In particular, isolated/focused sibling obligations may be hidden by Lean's
# tactic combinators. No arbitrary cut may be admitted on this check alone.
SINGLE_GOAL_GUARD = """open Lean Elab Tactic Meta in
elab "procedure_recorder_single_goal" : tactic => do
  let goals ← Lean.Elab.Tactic.getGoals
  unless goals.length == 1 do
    throwError "procedure recorder: unsupported goal count"
  for goal in goals do
    goal.withContext do
      let target ← Lean.instantiateMVars (← goal.getType)
      if target.hasMVar then
        throwError "procedure recorder: unresolved target metavariable"
      for decl in (← Lean.getLCtx) do
        let type ← Lean.instantiateMVars decl.type
        if type.hasMVar then
          throwError "procedure recorder: unresolved local-type metavariable"
        if let some value := decl.value? then
          let value ← Lean.instantiateMVars value
          if value.hasMVar then
            throwError "procedure recorder: unresolved local-value metavariable"
"""


class Recorder:
    def __init__(self, runtime: dict, output: Path, timeout: float = 120):
        self.runtime, self.output, self.timeout = runtime, Path(output), timeout
        self.output.mkdir(parents=True, exist_ok=False)
        self.session = uuid.uuid4().hex
        self.environments, self.snapshots, self.commands = {}, {}, []
        self.exchanges, self.elapsed = 0, 0.0
        self._write("session.json", {"session": self.session, "runtime": runtime,
                                     "snapshot_phase": "pre_tactic", "semantic_identity_claim": False})
        env = {**os.environ, "LEAN_PATH": runtime["lean_path"], "ELAN_HOME": runtime["elan_home"],
               "PATH": str(Path(runtime["elan_home"]) / "bin") + os.pathsep + os.environ.get("PATH", "")}
        self._stderr = (self.output / "stderr.log").open("wb")
        # Upstream IO.println does not flush when stdout is a pipe. A fresh
        # communicate() verifier hides this by closing stdin; persistence needs
        # line buffering. The original REPL binary itself remains unchanged.
        command = ([runtime["stdbuf"], "-oL"] if runtime.get("stdbuf") else []) + [runtime["repl"]]
        self.process = subprocess.Popen(command, cwd=runtime["project"], env=env,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self._stderr)
        self._lines = queue.Queue()
        def read():
            for line in iter(self.process.stdout.readline, b""):
                self._lines.put(line)
            self._lines.put(None)
        self._reader = threading.Thread(target=read, daemon=True)
        self._reader.start()

    def _write(self, name, value):
        (self.output / name).write_bytes(json_bytes(value))

    def close(self):
        if getattr(self, "_closed", False):
            return
        self._closed = True
        if not self.process.stdin.closed:
            self.process.stdin.close()
        if self.process.poll() is None:
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self._reader.join(timeout=5)
        self.process.stdout.close()
        self._stderr.close()
        self._write("costs.json", {"repl_requests": self.exchanges, "repl_wall_seconds": self.elapsed,
                                  "model_proposals": 0, "generated_tokens": 0, "gpu_jobs": 0})

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _exchange(self, request: dict) -> dict:
        index = self.exchanges
        self.exchanges += 1
        self._write(f"request-{index:04d}.json", request)
        started, raw = time.monotonic(), b""
        try:
            self.process.stdin.write(json_bytes(request) + b"\n")
            self.process.stdin.flush()
            while True:
                remaining = self.timeout - (time.monotonic() - started)
                if remaining <= 0:
                    raise queue.Empty
                line = self._lines.get(timeout=remaining)
                if line is None:
                    raise RecorderError("REPL exited before a complete response")
                raw += line
                if not line.strip() and raw.strip():
                    break
            response = json.loads(raw)
            if not isinstance(response, dict):
                raise RecorderError("REPL response is not an object")
        except queue.Empty as exc:
            self.process.kill()  # a timed-out protocol stream cannot safely resume
            raise RecorderError("REPL response timeout; session terminated") from exc
        finally:
            elapsed = time.monotonic() - started
            self.elapsed += elapsed
            (self.output / f"response-{index:04d}.raw").write_bytes(raw)
            self._write(f"exchange-{index:04d}.json", {"seconds": elapsed,
                        "request_sha256": digest(json_bytes(request)), "response_sha256": digest(raw)})
        errors = [m for m in response.get("messages", []) if m.get("severity") == "error"]
        if "message" in response or errors or response.get("sorries"):
            raise RecorderError("Lean rejected request: " + json.dumps(response, ensure_ascii=False))
        return response

    def _check_env(self, env):
        if env.session != self.session:
            raise RecorderError("wrong session for environment handle")
        if self.environments.get(env.id) != env:
            raise RecorderError("unknown or altered environment handle")

    def _check_snapshot(self, state, expected_environment_sha256=None):
        if state.session != self.session:
            raise RecorderError("wrong session for proof-state handle")
        if self.snapshots.get(state.id) != state:
            raise RecorderError("unknown or altered proof-state handle")
        if expected_environment_sha256 is not None and state.environment_sha256 != expected_environment_sha256:
            raise RecorderError("wrong environment for proof-state replay")

    def command(self, source: bytes, env: Environment | None = None):
        if not isinstance(source, bytes):
            raise TypeError("source must be exact UTF-8 bytes")
        text = source.decode("utf-8")
        if env is not None:
            self._check_env(env)
        index = len(self.commands)
        (self.output / f"source-{index:04d}.lean").write_bytes(source)
        request = {"cmd": text, "allTactics": True}
        if env is not None:
            request["env"] = env.id
        response = self._exchange(request)
        parent_hash = env.sha256 if env else self.runtime["sha256"]
        env_hash = digest(json_bytes({"parent": parent_hash, "source_sha256": digest(source)}))
        new_env = Environment(self.session, response["env"], env_hash,
                              (env.commands if env else ()) + (index,))
        self.environments[new_env.id] = new_env
        record = {"source_sha256": digest(source), "environment": asdict(new_env),
                  "parent_environment": asdict(env) if env else None,
                  "response": response, "snapshots": []}
        states = []
        for i, tactic in enumerate(response.get("tactics", [])):
            start, end = byte_offset(source, tactic["pos"]), byte_offset(source, tactic["endPos"])
            if end < start or not source[start:end]:
                raise RecorderError("invalid or empty tactic span")
            state = Snapshot(self.session, tactic["proofState"], env_hash, index, i, start, end)
            states.append(state)
            self.snapshots[state.id] = state
            record["snapshots"].append({**asdict(state), "tactic_bytes_sha256": digest(source[start:end]),
                "printed_goals_debug_sha256": digest(tactic["goals"].encode()),
                "environment_note": "command lineage identifier; snapshot's elaborator environment is held by REPL"})
        self.commands.append(record)
        self._write(f"command-{index:04d}.json", record)
        return new_env, states, response

    def bootstrap(self, imports=b"import Mathlib\nimport Aesop\n"):
        """Install the explicitly recorded meta guard before extracting states.

        The pinned REPL cannot compile this guard's nested run_tac program in a
        saved proof context, so its elaborator is declared in a command first.
        """
        return self.command(imports + SINGLE_GOAL_GUARD.encode())

    def step(self, state: Snapshot, tactic: str | None = None, *, expected_environment_sha256=None):
        self._check_snapshot(state, expected_environment_sha256)
        if tactic is None:
            if state.phase != "pre_tactic":
                raise RecorderError("automatic next tactic requires an extracted PRE-tactic snapshot")
            source = (self.output / f"source-{state.command:04d}.lean").read_bytes()
            if digest(source) != self.commands[state.command]["source_sha256"]:
                raise RecorderError("source checksum mismatch")
            tactic = source[state.start_byte:state.end_byte].decode()
        response = self._exchange({"proofState": state.id, "tactic": tactic})
        next_state = Snapshot(self.session, response["proofState"], state.environment_sha256,
                              state.command, state.tactic_index, state.start_byte, state.end_byte, "after_step")
        self.snapshots[next_state.id] = next_state
        self._write(f"step-{self.exchanges - 1:04d}.json", {"before": asdict(state),
                    "after": asdict(next_state), "tactic_sha256": digest(tactic.encode()), "response": response})
        return next_state, response

    def check_single_goal(self, state):
        """Reject visible multi-goal/unresolved-meta cases; never authorize a cut."""
        return self.step(state, "procedure_recorder_single_goal")

    def certify_cut(self, _state):
        raise RecorderError("unsupported cut certification: use a separately kernel-checked closed lemma")

    def replay(self, recorded: Path, command_index: int, tactic_index: int):
        """Replay exact ancestor commands; allocate fresh, session-local handles."""
        recorded = Path(recorded)
        session = json.loads((recorded / "session.json").read_bytes())
        if session["runtime"]["sha256"] != self.runtime["sha256"]:
            raise RecorderError("wrong environment/toolchain for recorded replay")
        record = json.loads((recorded / f"command-{command_index:04d}.json").read_bytes())
        env, selected = None, None
        for old_index in record["environment"]["commands"]:
            old = json.loads((recorded / f"command-{old_index:04d}.json").read_bytes())
            source = (recorded / f"source-{old_index:04d}.lean").read_bytes()
            if digest(source) != old["source_sha256"]:
                raise RecorderError("source checksum mismatch during replay")
            env, states, _ = self.command(source, env)
            if env.sha256 != old["environment"]["sha256"]:
                raise RecorderError("environment lineage mismatch during replay")
            if old_index == command_index:
                if tactic_index < 0 or tactic_index >= len(states):
                    raise RecorderError("missing tactic in replay")
                selected = states[tactic_index]
                expected = old["snapshots"][tactic_index]
                if (selected.start_byte, selected.end_byte) != (expected["start_byte"], expected["end_byte"]):
                    raise RecorderError("tactic span changed during replay")
        if selected is None:
            raise RecorderError("selected command absent from replay lineage")
        return selected


def demo(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    hypothesis = ("A pre-tactic snapshot from an authored single-goal have proof can be advanced "
                  "in one persistent session and reconstructed from exact source/environment replay; "
                  "session/environment mismatches and unsupported cuts fail closed.")
    (output / "hypothesis.json").write_bytes(json_bytes({"hypothesis": hypothesis,
        "data_role": "newly authored instrument fixtures; no model samples or transfer-panel witnesses",
        "decision": "whether persistent replay is ready as an observation instrument, not training admission"}))
    runtime_started = time.monotonic()
    runtime = capture_runtime(args.project, args.elan_home)
    runtime_seconds = time.monotonic() - runtime_started
    source = """theorem recorder_fixture (α : Nat) : α + 0 = α := by
  have h : α = α := by
    rfl
  simpa using h
""".encode()
    results = {}
    with Recorder(runtime, output / "original") as recorder:
        env, _, _ = recorder.bootstrap()
        final_env, states, response = recorder.command(source, env)
        selected = next(s for s in states if source[s.start_byte:s.end_byte] == b"simpa using h")
        _, audit = recorder.check_single_goal(selected)
        _, next_response = recorder.step(selected, expected_environment_sha256=final_env.sha256)
        results["pre_goals"] = response["tactics"][selected.tactic_index]["goals"]
        results["post_goals"] = next_response["goals"]
        results["pre_snapshot_nonempty_post_empty"] = bool(results["pre_goals"]) and not next_response["goals"]
        results["single_goal_guard_passed"] = not audit.get("messages")
        for name, action in {
            "wrong_environment_rejected": lambda: recorder.step(selected, expected_environment_sha256=env.sha256),
            "cut_rejected": lambda: recorder.certify_cut(selected),
        }.items():
            try:
                action()
            except RecorderError as exc:
                results[name] = str(exc)
            else:
                raise AssertionError(name)
        _, multi, _ = recorder.command(b"example : True /\\ True := by\n  constructor\n  all_goals trivial\n", env)
        multi_state = next(s for s in multi if b"all_goals trivial" ==
                           (recorder.output / f"source-{s.command:04d}.lean").read_bytes()[s.start_byte:s.end_byte])
        try:
            recorder.check_single_goal(multi_state)
        except RecorderError as exc:
            results["multi_goal_rejected"] = str(exc)
        else:
            raise AssertionError("multiple goals admitted")
        shared_source = b"example : Exists (fun n : Nat => n = n) := by\n  refine Exists.intro ?_ ?_\n  swap\n  . rfl\n  . exact 0\n"
        _, shared, _ = recorder.command(shared_source, env)
        shared_state = next(s for s in shared if shared_source[s.start_byte:s.end_byte] == b"rfl")
        try:
            recorder.check_single_goal(shared_state)
        except RecorderError as exc:
            results["shared_metavariable_rejected"] = str(exc)
        else:
            raise AssertionError("shared metavariable boundary admitted")
    with Recorder(runtime, output / "replay") as replay:
        try:
            replay.step(selected)
        except RecorderError as exc:
            results["wrong_session_rejected"] = str(exc)
        else:
            raise AssertionError("foreign handle admitted")
        recreated = replay.replay(output / "original", selected.command, selected.tactic_index)
        _, replay_response = replay.step(recreated)
        results["replayed_post_goals"] = replay_response["goals"]
        results["replay_response_equal"] = {k: v for k, v in next_response.items() if k != "proofState"} == {
            k: v for k, v in replay_response.items() if k != "proofState"}
        wrong = {**runtime, "sha256": "0" * 64}
        replay.runtime = wrong
        try:
            replay.replay(output / "original", selected.command, selected.tactic_index)
        except RecorderError as exc:
            results["wrong_runtime_replay_rejected"] = str(exc)
        else:
            raise AssertionError("wrong runtime admitted")
        replay.runtime = runtime
    report = {"hypothesis": hypothesis, "results": results, "runtime_sha256": runtime["sha256"],
        "lean_version": runtime["lean_version"], "runtime_hash_seconds": runtime_seconds,
        "hashed_files": len(runtime["files"]), "hashed_bytes": sum(f["bytes"] for f in runtime["files"]),
        "wall_seconds": time.monotonic() - started, "hardware": platform.uname()._asdict(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": subprocess.check_output(["git", "status", "--short"], text=True),
        "source_sha256": digest(source), "script_sha256": file_hash(Path(__file__)),
        "model_proposals": 0, "gpu_jobs": 0, "seed": None,
        "limits": ["Printed goals are debug views, not semantic identities.",
                   "Goal guard cannot establish independence of hidden focused siblings; all cuts rejected.",
                   "Command lineage hash is not the exact internal elaborator-environment hash.",
                   "No proof extraction, axiom audit, training admission, or production correctness substitution."]}
    (output / "report.json").write_bytes(json_bytes(report))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--elan-home", type=Path, required=True)
    demo(parser.parse_args())
