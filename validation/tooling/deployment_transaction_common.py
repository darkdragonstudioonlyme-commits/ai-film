#!/usr/bin/env python3
"""Fail-closed helpers for reviewed prodlike/LAB execution transactions."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Iterable, Sequence

class TxnError(RuntimeError):
    pass

class UnknownCommandCompletion(TxnError):
    pass

def req(condition: bool, reason: str) -> None:
    if not condition:
        raise TxnError(reason)

def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")

def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def sha_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise TxnError("DUPLICATE_JSON_KEY:" + key)
        out[key] = value
    return out

def load_json(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_pairs,
                          parse_constant=lambda x: (_ for _ in ()).throw(TxnError("NONFINITE_JSON")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TxnError("JSON_UNREADABLE:" + str(path)) from exc

def atomic_bytes(path: str | Path, raw: bytes, mode: int = 0o600) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    os.chmod(tmp, mode)
    os.replace(tmp, path)
    dfd = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)

def atomic_json(path: str | Path, value: Any, mode: int = 0o600) -> None:
    atomic_bytes(path, json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                                  allow_nan=False).encode("utf-8") + b"\n", mode)

def path_within(path: str | Path, root: str | Path) -> bool:
    p = Path(path).expanduser().resolve(strict=False)
    r = Path(root).expanduser().resolve(strict=False)
    try:
        p.relative_to(r)
        return True
    except ValueError:
        return False

def require_within(path: str | Path, roots: Iterable[str | Path], reason: str = "PATH_OUTSIDE_AUTHORIZED_ROOT") -> None:
    req(any(path_within(path, root) for root in roots), reason + ":" + str(path))

def safe_relative(name: str) -> bool:
    p = Path(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts and "\\" not in name

AUTH_KEYS = {
    "schema_version", "kind", "status", "transaction_id", "transaction_kind",
    "main_commit", "validation_commit", "executor_commit", "executor_tree", "candidate_id",
    "candidate_binding_sha256", "input_sha256", "mutation_roots",
    "allowed_command_prefixes", "attempt", "authorized", "expires_at",
    "native_execution_authorized", "signing_authorized", "hklm_authorized",
    "site_authorized", "qualification_authorized", "host_ready_authorized",
}

def _hex(value: Any, n: int, reason: str) -> str:
    req(isinstance(value, str) and len(value) == n and
        all(c in "0123456789abcdef" for c in value), reason)
    return value

def load_authorization(path: str | Path, expected_sha256: str, transaction_kind: str,
                       *, candidate_id: str, binding_sha256: str,
                       main_commit: str | None = None, validation_commit: str | None = None,
                       executor_commit: str | None = None, executor_tree: str | None = None,
                       now_unix: int | None = None) -> tuple[dict, str]:
    p = Path(path)
    req(p.is_file() and not p.is_symlink(), "AUTHORIZATION_UNSAFE")
    raw = p.read_bytes()
    actual = sha_bytes(raw)
    req(actual == expected_sha256, "AUTHORIZATION_SHA256_MISMATCH")
    value = load_json(p)
    req(type(value) is dict and set(value) == AUTH_KEYS, "AUTHORIZATION_SCHEMA")
    req(type(value["schema_version"]) is int and value["schema_version"] == 1, "AUTHORIZATION_VERSION")
    req(value["kind"] == "AIFILM_P00_TRANSACTION_AUTHORIZATION_V1" and
        value["status"] == "AUTHORIZED" and value["authorized"] is True,
        "AUTHORIZATION_STATUS")
    req(value["transaction_kind"] == transaction_kind, "AUTHORIZATION_KIND")
    req(value["candidate_id"] == candidate_id and
        value["candidate_binding_sha256"] == binding_sha256, "AUTHORIZATION_CANDIDATE")
    _hex(value["main_commit"], 40, "AUTHORIZATION_MAIN_COMMIT")
    _hex(value["validation_commit"], 40, "AUTHORIZATION_VALIDATION_COMMIT")
    _hex(value["executor_commit"], 40, "AUTHORIZATION_EXECUTOR_COMMIT")
    _hex(value["executor_tree"], 40, "AUTHORIZATION_EXECUTOR_TREE")
    if main_commit is not None:
        req(value["main_commit"] == main_commit, "AUTHORIZATION_MAIN_DRIFT")
    if validation_commit is not None:
        req(value["validation_commit"] == validation_commit, "AUTHORIZATION_VALIDATION_DRIFT")
    if executor_commit is not None:
        req(value["executor_commit"] == executor_commit, "AUTHORIZATION_EXECUTOR_DRIFT")
    if executor_tree is not None:
        req(value["executor_tree"] == executor_tree, "AUTHORIZATION_EXECUTOR_TREE_DRIFT")
    req(type(value["attempt"]) is int and value["attempt"] == 1, "AUTHORIZATION_ATTEMPT")
    req(type(value["transaction_id"]) is str and value["transaction_id"], "AUTHORIZATION_TRANSACTION_ID")
    req(type(value["input_sha256"]) is dict and value["input_sha256"], "AUTHORIZATION_INPUTS")
    for key, digest in value["input_sha256"].items():
        req(isinstance(key, str) and key, "AUTHORIZATION_INPUT_KEY")
        _hex(digest, 64, "AUTHORIZATION_INPUT_HASH")
    roots = value["mutation_roots"]
    req(type(roots) is list and roots and len(roots) == len(set(roots)) and
        all(isinstance(x, str) and Path(x).is_absolute() for x in roots),
        "AUTHORIZATION_MUTATION_ROOTS")
    resolved_roots = [Path(x).resolve(strict=False) for x in roots]
    req(all(str(x) not in ('/', '/home', '/home/dragon') for x in resolved_roots),
        "AUTHORIZATION_ROOT_TOO_BROAD")
    sensitive = [Path('/home/dragon/.ssh'), Path('/home/dragon/.gnupg'), Path('/home/dragon/.config'),
                 Path('/home/dragon/ai-film-dev/local-authority'), Path('/home/dragon/ai-film-dev/root-ops')]
    def overlaps(a: Path, b: Path) -> bool:
        try:
            a.relative_to(b); return True
        except ValueError:
            try:
                b.relative_to(a); return True
            except ValueError:
                return False
    req(all(not any(overlaps(root, secret) for secret in sensitive) for root in resolved_roots),
        "AUTHORIZATION_ROOT_SENSITIVE")
    prefixes = value["allowed_command_prefixes"]
    req(type(prefixes) is list and prefixes and all(type(x) is list and x and all(isinstance(y, str) and y for y in x)
                                      for x in prefixes), "AUTHORIZATION_COMMANDS")
    forbidden = {'sudo','su','bash','sh','dash','zsh','cmd.exe','powershell.exe','pwsh','curl','wget','pip','pip3','apt','apt-get','claude'}
    for prefix in prefixes:
        req(Path(prefix[0]).is_absolute(), "AUTHORIZATION_COMMAND_NOT_ABSOLUTE:" + prefix[0])
        req(Path(prefix[0]).name.lower() not in forbidden, "AUTHORIZATION_COMMAND_FORBIDDEN:" + prefix[0])
    for field in ("native_execution_authorized", "signing_authorized", "hklm_authorized",
                  "site_authorized", "qualification_authorized", "host_ready_authorized"):
        req(value[field] is False, "AUTHORIZATION_FORBIDDEN_CAPABILITY:" + field)
    expires = value["expires_at"]
    req(type(expires) is int and expires > 0, "AUTHORIZATION_EXPIRY")
    if now_unix is None:
        now_unix = int(time.time())
    req(now_unix <= expires, "AUTHORIZATION_EXPIRED")
    return value, actual

class Runner:
    def run(self, argv: Sequence[str], *, input_bytes: bytes | None = None,
            input_path: str | Path | None = None) -> subprocess.CompletedProcess:
        raise NotImplementedError

class SubprocessRunner(Runner):
    """Production runner. Callers must validate argv against internal + authorized allowlists first."""
    def __init__(self, env: dict[str, str] | None = None):
        self.env = env or {
            "HOME": os.environ.get("HOME", "/home/dragon"),
            "USER": os.environ.get("USER", "dragon"),
            "LOGNAME": os.environ.get("LOGNAME", "dragon"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PATH": "/usr/bin:/bin:/mnt/c/Windows/System32",
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }

    def run(self, argv: Sequence[str], *, input_bytes: bytes | None = None,
            input_path: str | Path | None = None) -> subprocess.CompletedProcess:
        req(not (input_bytes is not None and input_path is not None), "COMMAND_STDIN_AMBIGUOUS")
        try:
            if input_path is not None:
                p = Path(input_path)
                req(p.is_file() and not p.is_symlink(), "COMMAND_STDIN_FILE_UNSAFE")
                with p.open("rb") as fh:
                    return subprocess.run(list(argv), stdin=fh, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, env=self.env, check=False)
            return subprocess.run(list(argv), input=input_bytes, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=self.env, check=False)
        except OSError as exc:
            raise UnknownCommandCompletion("COMMAND_OS_ERROR:" + repr(list(argv))) from exc

def command_allowed(argv: Sequence[str], internal_prefixes: Sequence[Sequence[str]],
                    authorized_prefixes: Sequence[Sequence[str]]) -> bool:
    if not argv or not all(isinstance(x, str) for x in argv):
        return False
    def matches(prefix):
        return len(argv) >= len(prefix) and list(argv[:len(prefix)]) == list(prefix)
    return any(matches(x) for x in internal_prefixes) and any(matches(x) for x in authorized_prefixes)

def run_checked(runner: Runner, argv: Sequence[str], *, internal_prefixes: Sequence[Sequence[str]],
                authorized_prefixes: Sequence[Sequence[str]], input_bytes: bytes | None = None,
                input_path: str | Path | None = None,
                allowed_returncodes: Sequence[int] = (0,)) -> subprocess.CompletedProcess:
    req(command_allowed(argv, internal_prefixes, authorized_prefixes),
        "COMMAND_NOT_ALLOWED:" + json.dumps(list(argv)))
    result = runner.run(argv, input_bytes=input_bytes, input_path=input_path)
    if result.returncode not in allowed_returncodes:
        raise UnknownCommandCompletion(
            "COMMAND_NONZERO_OR_UNKNOWN:" + json.dumps(list(argv)) + ":" + str(result.returncode)
        )
    return result

def begin_transaction(receipt_path: str | Path, *, transaction_id: str,
                      transaction_kind: str, authorization_sha256: str,
                      candidate_id: str, candidate_binding_sha256: str) -> tuple[dict, bool]:
    path = Path(receipt_path)
    lock_path = path.with_name(path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if path.exists():
            existing = load_json(path)
            req(existing.get("transaction_id") == transaction_id, "TRANSACTION_RECEIPT_IDENTITY")
            # One authorization = one attempt. Existing receipt is never re-executed implicitly.
            req(existing.get("authorization_sha256") == authorization_sha256, "TRANSACTION_AUTHORIZATION_IDENTITY")
            return existing, False
        receipt = {
            "schema_version": 1,
            "kind": "AIFILM_P00_TRANSACTION_RECEIPT_V1",
            "transaction_id": transaction_id,
            "transaction_kind": transaction_kind,
            "authorization_sha256": authorization_sha256,
            "candidate_id": candidate_id,
            "candidate_binding_sha256": candidate_binding_sha256,
            "state": "PREPARED",
            "phase": "PREMUTATION",
            "mutation_started": False,
            "rollback_attempted": False,
            "rollback_verified": False,
            "unknown_completion": False,
            "events": [],
            "native_execution_started": False,
            "signing_performed": False,
            "hklm_touched": False,
            "site_entered": False,
            "qualification_issued": False,
            "host_ready": False,
        }
        atomic_json(path, receipt)
        return receipt, True

def append_event(receipt_path: str | Path, event: str, **fields: Any) -> dict:
    value = load_json(receipt_path)
    row = {"event": event, **fields}
    value["events"].append(row)
    atomic_json(receipt_path, value)
    return value

def set_receipt(receipt_path: str | Path, **fields: Any) -> dict:
    value = load_json(receipt_path)
    value.update(fields)
    atomic_json(receipt_path, value)
    return value

def assert_input_hashes(auth: dict, named_paths: dict[str, str | Path]) -> None:
    req(set(named_paths) <= set(auth["input_sha256"]), "AUTHORIZATION_INPUT_MISSING")
    for name, path in named_paths.items():
        req(sha_file(path) == auth["input_sha256"][name], "INPUT_HASH_DRIFT:" + name)

def snapshot_file(path: str | Path) -> dict:
    p = Path(path)
    req(p.is_file() and not p.is_symlink(), "SNAPSHOT_FILE_UNSAFE:" + str(path))
    return {"path": str(p), "sha256": sha_file(p), "bytes": p.stat().st_size,
            "mode": format(p.stat().st_mode & 0o777, "o")}

def snapshot_symlink(path: str | Path) -> dict:
    p = Path(path)
    req(p.is_symlink(), "SNAPSHOT_SYMLINK_REQUIRED:" + str(path))
    return {"path": str(p), "target": os.readlink(p)}

def atomic_symlink(target: str, link: str | Path) -> None:
    p = Path(link)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    if tmp.exists() or tmp.is_symlink():
        tmp.unlink()
    os.symlink(target, tmp)
    os.replace(tmp, p)

def copy_file_exact(src: str | Path, dst: str | Path, mode: int) -> None:
    src, dst = Path(src), Path(dst)
    req(src.is_file() and not src.is_symlink(), "COPY_SOURCE_UNSAFE:" + str(src))
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".tmp")
    with src.open("rb") as inp, tmp.open("wb") as out:
        while True:
            chunk = inp.read(4 * 1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
        out.flush(); os.fsync(out.fileno())
    os.chmod(tmp, mode); os.replace(tmp, dst)
    req(sha_file(dst) == sha_file(src), "COPY_READBACK_HASH:" + str(dst))
    req((dst.stat().st_mode & 0o777) == mode, "COPY_READBACK_MODE:" + str(dst))
