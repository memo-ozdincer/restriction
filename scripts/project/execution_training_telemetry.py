#!/usr/bin/env python3
"""Opt-in training accounting and complete, weight-only checkpoint validation.

The trainer calls these helpers explicitly only when EXECUTION_TRAINING_TELEMETRY
is set. No startup hooks, optimizer substitution, or scientific policy changes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import struct
import sys
import tempfile
import time

_sequence = 0


def telemetry_enabled():
    return bool(os.environ.get("EXECUTION_TRAINING_TELEMETRY"))


def emit_event(event, *, role, **details):
    """Append an fsynced record after the operation it attests has completed."""
    destination = os.environ.get("EXECUTION_TRAINING_TELEMETRY")
    if not destination:
        return
    global _sequence
    rank = -1
    torch = sys.modules.get("torch")
    if torch is not None and torch.distributed.is_initialized():
        rank = int(torch.distributed.get_rank())
    directory = Path(destination)
    if not directory.is_absolute() or not directory.is_dir():
        raise ValueError("EXECUTION_TRAINING_TELEMETRY must be an existing absolute directory")
    _sequence += 1
    record = {"schema_version": 1, "event": event, "role": role,
              "rank": rank, "pid": os.getpid(), "hostname": socket.gethostname(),
              "sequence": _sequence, "time_unix": time.time(), **details}
    path = directory / f"{role}-rank-{rank}-pid-{os.getpid()}.jsonl"
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, f"invalid {label}")
    return value


def summarize_telemetry(path, expected_ranks=4, expected_steps=64):
    """Authenticate complete per-rank updates; count synchronized steps once.

    Token counts are summed over data-parallel ranks. Optimizer steps are
    required to match across ranks and counted once, never multiplied by GPUs.
    """
    paths = sorted(Path(path).glob("*.jsonl"))
    require(bool(paths), "missing training telemetry")
    records = []
    files = {}
    for source in paths:
        require(not source.is_symlink(), "symlink telemetry is not supported")
        rows = [json.loads(line) for line in source.read_text().splitlines()]
        require(bool(rows), "empty telemetry file")
        require(all(row.get("schema_version") == 1 for row in rows), "unknown telemetry schema")
        identity = {(row.get("hostname"), row.get("pid"), row.get("rank"), row.get("role")) for row in rows}
        require(len(identity) == 1, "mixed worker telemetry file")
        sequences = [row.get("sequence") for row in rows]
        require(all(type(n) is int and n > 0 for n in sequences)
                and sequences == sorted(set(sequences)), "nonmonotonic telemetry sequence")
        records.extend(rows)
        files[source.name] = sha256(source)
    actor = defaultdict(list)
    driver = []
    for row in records:
        require(row.get("role") in ("actor", "driver"), "unknown telemetry role")
        if row["role"] == "actor":
            actor[row["rank"]].append(row)
        else:
            require(row.get("event") in ("runtime_config", "rollout_batch", "checkpoint_saved", "actor_dispatch_complete"),
                    "unknown driver event")
            driver.append(row)
    require(set(actor) == set(range(expected_ranks)), "missing or unexpected actor ranks")
    require(len({(r["hostname"], r["pid"]) for r in driver}) == 1, "missing or duplicate training driver")
    configurations = [row for row in driver if row["event"] == "runtime_config"]
    require(len(configurations) == 1, "missing or duplicate runtime configuration")
    runtime = configurations[0]
    require(isinstance(runtime.get("resolved_config"), dict) and isinstance(runtime.get("environment"), dict),
            "invalid runtime configuration")
    from verl.lean.telemetry import telemetry_identity
    config_hash, environment_hash = telemetry_identity(
        json.dumps(runtime["resolved_config"], sort_keys=True, separators=(",", ":")), runtime["environment"])
    require(runtime.get("config_hash") == config_hash and runtime.get("environment_hash") == environment_hash,
            "runtime configuration/environment hash mismatch")
    by_rank = {}
    update_layouts = []
    total_batch_tokens = total_actual_tokens = total_attempt_tokens = 0
    for rank, rows in sorted(actor.items()):
        require(len({(r["hostname"], r["pid"]) for r in rows}) == 1, "actor restart or duplicate worker")
        updates = defaultdict(list)
        for row in rows:
            require(row["event"] in ("actor_update_begin", "optimizer_attempt", "actor_update_end"),
                    "unknown actor event")
            updates[_integer(row.get("update_index"), "update index", 1)].append(row)
        require(sorted(updates) == list(range(1, len(updates) + 1)), "missing actor update")
        actual = attempts = skipped = 0
        layout = []
        for update_index, update in sorted(updates.items()):
            update.sort(key=lambda row: row["sequence"])
            require(update[0]["event"] == "actor_update_begin" and update[-1]["event"] == "actor_update_end",
                    "incomplete actor update")
            require(sum(r["event"] == "actor_update_begin" for r in update) == 1
                    and sum(r["event"] == "actor_update_end" for r in update) == 1, "duplicate update boundaries")
            begin, end = update[0], update[-1]
            epochs = _integer(begin.get("ppo_epochs"), "PPO epochs", 1)
            size = _integer(begin.get("rows"), "actor update rows", 1)
            mini = _integer(begin.get("mini_batch_size"), "actor mini batch size", 1)
            tokens = _integer(begin.get("response_tokens"), "update response tokens", 1)
            expected_attempts = epochs * math.ceil(size / mini)
            events = update[1:-1]
            require(len(events) == expected_attempts, "optimizer attempt count mismatch")
            coordinates = [(e, i) for e in range(epochs) for i in range(math.ceil(size / mini))]
            require([(r.get("ppo_epoch"), r.get("mini_batch_index")) for r in events] == coordinates,
                    "optimizer minibatch order mismatch")
            require(all(r["event"] == "optimizer_attempt" and type(r.get("applied")) is bool for r in events),
                    "invalid optimizer attempt")
            for event in events:
                _integer(event.get("response_tokens"), "minibatch response tokens", 1)
            applied = sum(r["applied"] for r in events)
            require(end.get("optimizer_attempts") == expected_attempts
                    and end.get("optimizer_steps_applied") == applied
                    and end.get("optimizer_steps_skipped") == expected_attempts - applied,
                    "actor end counters disagree with optimizer events")
            require(sum(r["response_tokens"] for r in events) == tokens * epochs,
                    "PPO token exposure mismatch")
            actual += applied
            attempts += expected_attempts
            skipped += expected_attempts - applied
            total_batch_tokens += tokens
            total_actual_tokens += sum(r["response_tokens"] for r in events if r["applied"])
            total_attempt_tokens += sum(r["response_tokens"] for r in events)
            layout.append((update_index, size, epochs, mini, tuple(r["applied"] for r in events)))
        update_layouts.append(layout)
        by_rank[str(rank)] = {"actor_update_calls": len(updates), "optimizer_attempts": attempts,
                              "actual_optimizer_steps": actual, "skipped_optimizer_steps": skipped}
    require(all(layout == update_layouts[0] for layout in update_layouts), "rank optimizer accounting disagreement")
    first = by_rank["0"]
    require(first["actual_optimizer_steps"] > 0, "no actual optimizer updates")
    steps = [r for r in driver if r["event"] == "rollout_batch"]
    saves = [r for r in driver if r["event"] == "checkpoint_saved"]
    calls = [r for r in driver if r["event"] == "actor_dispatch_complete"]
    require(len(steps) == expected_steps and sorted(r.get("step") for r in steps) == list(range(1, expected_steps + 1)),
            "missing or duplicate rollout steps")
    for row in steps:
        require(row.get("groups") == 16 and row.get("samples_per_group") == 32, "changed rollout budget")
        admitted = _integer(row.get("admitted_groups"), "admitted groups")
        require(admitted <= 16 and row.get("skipped_groups") == 16 - admitted, "invalid group admission")
    require(len(calls) == first["actor_update_calls"], "driver/actor update counts disagree")
    require(all(r.get("step") in range(1, expected_steps + 1) for r in calls), "invalid dispatch step")
    require(sum(r["rows"] for r in calls) == sum(layout[1] for layout in update_layouts[0]) * expected_ranks,
            "driver/actor optimized row count mismatch")
    require(any(r.get("step") == expected_steps for r in saves), "final checkpoint save did not complete")
    admitted_groups = sum(r["admitted_groups"] for r in steps)
    optimized_rows = sum(r["rows"] for r in calls)
    residual = admitted_groups * 32 - optimized_rows
    require(0 <= residual < 256, "invalid final unoptimized buffer")
    return {**first, "per_rank": by_rank, "resolved_config": runtime["resolved_config"],
            "environment": runtime["environment"], "config_hash": config_hash, "environment_hash": environment_hash,
            "optimizer_step_count_convention": "synchronized steps counted once; identical counts required on every rank",
            "response_tokens_in_update_batches": total_batch_tokens,
            "response_token_exposures_with_ppo_epochs": total_attempt_tokens,
            "optimized_response_tokens": total_actual_tokens,
            "optimized_response_tokens_convention": "actual applied optimizer minibatches, including repeated PPO epochs; summed across ranks",
            "admitted_groups": admitted_groups, "skipped_groups": expected_steps * 16 - admitted_groups,
            "optimized_rows": optimized_rows, "residual_buffer_rows": residual,
            "final_checkpoint_saved": True, "files_sha256": files}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_child(root, filename):
    require(isinstance(filename, str) and Path(filename).name == filename and filename not in ("", ".", ".."),
            "unsafe checkpoint filename")
    path = root / filename
    require(path.is_file() and not path.is_symlink(), f"missing checkpoint file: {filename}")
    return path


def safetensors_inventory(directory):
    """Validate headers, offsets, exact payload length and shard-index coverage."""
    directory = Path(directory)
    index_path = directory / "model.safetensors.index.json"
    if index_path.exists():
        index = json.loads(_safe_child(directory, index_path.name).read_text())
        weight_map = index.get("weight_map")
        require(isinstance(weight_map, dict) and bool(weight_map), "empty checkpoint weight map")
        filenames = sorted(set(weight_map.values()))
    else:
        index = None
        weight_map = None
        filenames = ["model.safetensors"]
    inventory = {}
    files = {}
    total_payload = 0
    widths = {"BOOL": 1, "U8": 1, "I8": 1, "I16": 2, "U16": 2, "F16": 2,
              "BF16": 2, "I32": 4, "U32": 4, "F32": 4, "I64": 8, "U64": 8, "F64": 8}
    for filename in filenames:
        source = _safe_child(directory, filename)
        require(source.suffix == ".safetensors", "unsupported checkpoint shard format")
        with source.open("rb") as stream:
            length = stream.read(8)
            require(len(length) == 8, "truncated safetensors length header")
            header_size = struct.unpack("<Q", length)[0]
            require(0 < header_size <= 100_000_000, "invalid safetensors header size")
            header = json.loads(stream.read(header_size))
        payload_size = source.stat().st_size - 8 - header_size
        offsets = []
        for name, spec in header.items():
            if name == "__metadata__":
                continue
            require(name not in inventory, "duplicate checkpoint tensor")
            shape = spec.get("shape")
            dtype = spec.get("dtype")
            bounds = spec.get("data_offsets")
            require(isinstance(shape, list) and all(type(n) is int and n >= 0 for n in shape), "invalid tensor shape")
            require(dtype in widths, "unsupported checkpoint tensor dtype")
            require(isinstance(bounds, list) and len(bounds) == 2
                    and all(type(n) is int and n >= 0 for n in bounds), "invalid tensor offsets")
            start, end = bounds
            require(end - start == math.prod(shape) * widths[dtype], "tensor size/shape mismatch")
            require(weight_map is None or weight_map.get(name) == filename, "shard index/tensor mismatch")
            offsets.append((start, end))
            inventory[name] = {"shape": shape, "dtype": dtype, "shard": filename}
        cursor = 0
        for start, end in sorted(offsets):
            require(start == cursor and end >= start, "safetensors payload gap or overlap")
            cursor = end
        require(cursor == payload_size and bool(offsets), "truncated or trailing checkpoint payload")
        total_payload += payload_size
        files[filename] = {"sha256": sha256(source), "bytes": source.stat().st_size}
    require(weight_map is None or set(inventory) == set(weight_map), "incomplete checkpoint tensor index")
    if index is not None:
        require(index.get("metadata", {}).get("total_size") == total_payload, "checkpoint total_size mismatch")
        files[index_path.name] = {"sha256": sha256(index_path), "bytes": index_path.stat().st_size}
    return inventory, files


def validate_actor_checkpoint(checkpoint, base_model):
    """Verify full final HF actor weights, without claiming exact resumability."""
    checkpoint, base_model = Path(checkpoint), Path(base_model)
    require(checkpoint.is_dir() and not checkpoint.is_symlink(), "missing actor checkpoint")
    require(checkpoint.name == "global_step_64", "only the final step-64 actor is evaluation eligible")
    base, _ = safetensors_inventory(base_model)
    actor, files = safetensors_inventory(checkpoint)
    require(set(actor) == set(base), "checkpoint tensor keys differ from base")
    require(all(actor[name]["shape"] == base[name]["shape"] for name in base), "checkpoint tensor shapes differ from base")
    require(all(actor[name]["dtype"] in (base[name]["dtype"], "F32") for name in base),
            "checkpoint tensor dtype is incompatible with base")
    for filename in ("config.json", "tokenizer.json", "tokenizer_config.json"):
        source = _safe_child(checkpoint, filename)
        value = json.loads(source.read_text())
        require(isinstance(value, dict) and bool(value), f"empty checkpoint {filename}")
        files[filename] = {"sha256": sha256(source), "bytes": source.stat().st_size}
    expected_tokenizer = normalized_tokenizer_files(base_model)
    for filename, expected in expected_tokenizer.items():
        source = _safe_child(checkpoint, filename)
        require(json.loads(source.read_text()) == expected,
                f"checkpoint tokenizer differs from normalized pristine base: {filename}")
        files[filename] = {"sha256": sha256(source), "bytes": source.stat().st_size}
    config = json.loads((checkpoint / "config.json").read_text())
    base_config = json.loads((base_model / "config.json").read_text())
    # The unchanged actor constructor sets pad_token_id from the tokenizer;
    # the registered base tokenizer uses EOS for padding.
    base_config.setdefault("pad_token_id", base_config.get("eos_token_id"))
    config.setdefault("pad_token_id", config.get("eos_token_id"))
    ignored = {"_name_or_path", "torch_dtype", "transformers_version"}
    require({k: v for k, v in config.items() if k not in ignored} ==
            {k: v for k, v in base_config.items() if k not in ignored}, "checkpoint architecture/config changed")
    return {"checkpoint": str(checkpoint.resolve()), "complete": True,
            "tensor_count": len(actor), "files": files, "exact_resume_supported": False,
            "tokenizer_authentication": "JSON equality to same pinned runtime loader/save_pretrained normalization of pristine base"}


def normalized_tokenizer_files(base_model):
    """Account for the existing HF loader's BOS processor and EOS-pad setup.

    A normal save_pretrained rewrites the original tokenizer JSON; comparing its
    bytes with the archival file would reject an unchanged tokenizer. Normalize
    a new pristine-base tokenizer through exactly the established loader instead.
    """
    from verl.utils import hf_tokenizer
    tokenizer = hf_tokenizer(str(base_model), trust_remote_code=True, local_files_only=True)
    with tempfile.TemporaryDirectory(prefix="execution-base-tokenizer-") as temporary:
        tokenizer.save_pretrained(temporary)
        directory = Path(temporary)
        require(all((directory / filename).is_file() for filename in
                    ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")),
                "normalized pristine tokenizer is incomplete")
        return {source.name: json.loads(source.read_text()) for source in sorted(directory.glob("*.json"))}
