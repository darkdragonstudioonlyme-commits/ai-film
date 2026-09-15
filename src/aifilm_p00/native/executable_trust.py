"""Exact native executable trust bound by the authenticated site binding.

The reviewed build digest authenticates project source/config. Native child
executables are outside that build and therefore need an independent, pinned
byte identity. A successful path lookup or CreateProcess is never sufficient.

Policy documents are stored in the existing ACL-anchored NativeStore and are
referenced by the native binding. Nothing in this module enrolls a binary or
learns a digest from the bytes it is about to execute.
"""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass

from .. import CONTRACT_DIGEST
from ..codec import hash_value, windows_path
from ..errors import require


@dataclass(frozen=True)
class ExecutablePin:
    pinned: object
    policy_ref: str
    sha256: str
    bytes: int
    kind: str

    @property
    def identity(self):
        return self.pinned.identity


class ExecutableTrust:
    """Read-only exact-byte executable policy.

    Expected schema (the outer ``role`` field is added by NativeStore):

    {
      "schema_version": 1,
      "host_id": "...",
      "build_digest": "...",
      "contract_digest": "...",
      "withdrawn": false,
      "executables": [
        {"path":"C:\\...\\wsl.exe", "bytes":123, "sha256":"...",
         "kind":"SYSTEM"}
      ]
    }

    The policy is site/build scoped. Paths are exact and duplicate aliases are
    forbidden case-insensitively. Hashes must be supplied by trusted authority;
    this class never self-pins the bytes it observes.
    """

    def __init__(self, paths, policy_ref: str, policy: dict, *, host_id: str,
                 build_digest: str):
        hash_value(policy_ref)
        require(type(policy) is dict and policy.get('schema_version') == 1,
                15, 'EXECUTABLE_POLICY_SCHEMA')
        require(policy.get('withdrawn') is False, 11,
                'EXECUTABLE_POLICY_WITHDRAWN')
        require(policy.get('host_id') == host_id and
                policy.get('build_digest') == build_digest,
                16, 'EXECUTABLE_POLICY_SCOPE')
        require(policy.get('contract_digest') == CONTRACT_DIGEST,
                15, 'EXECUTABLE_POLICY_CONTRACT')
        rows = policy.get('executables')
        require(type(rows) is list and bool(rows), 15,
                'EXECUTABLE_POLICY_EMPTY')
        normalized = {}
        for row in rows:
            require(type(row) is dict and set(row) ==
                    {'path', 'bytes', 'sha256', 'kind'},
                    15, 'EXECUTABLE_POLICY_ROW')
            path = windows_path(row['path'])
            key = path.casefold()
            require(key not in normalized, 15,
                    'EXECUTABLE_POLICY_DUPLICATE')
            require(type(row['bytes']) is int and 0 < row['bytes'] <= 256*1024**2,
                    15, 'EXECUTABLE_POLICY_BYTES')
            hash_value(row['sha256'])
            require(row['kind'] in ('SYSTEM', 'PINNED_DEPENDENCY'),
                    15, 'EXECUTABLE_POLICY_KIND')
            normalized[key] = {
                'path': path, 'bytes': row['bytes'],
                'sha256': row['sha256'], 'kind': row['kind']}
        self.paths = paths
        self.policy_ref = policy_ref
        self.rows = normalized
        self.host_id = host_id
        self.build_digest = build_digest

    @classmethod
    def from_store(cls, paths, store, policy_ref: str, *, host_id: str,
                   build_digest: str):
        policy = store.get('executable_policy', policy_ref)
        return cls(paths, policy_ref, policy, host_id=host_id,
                   build_digest=build_digest)

    @contextmanager
    def pin(self, path: str):
        path = windows_path(path)
        row = self.rows.get(path.casefold())
        require(row is not None and row['path'] == path,
                15, 'EXECUTABLE_NOT_TRUSTED')
        with self.paths.pinned_executable(path, row['sha256'],
                                          row['bytes']) as pinned:
            yield ExecutablePin(pinned, self.policy_ref, row['sha256'],
                                row['bytes'], row['kind'])
