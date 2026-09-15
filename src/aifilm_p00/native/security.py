"""ACL policy shared by concrete handle checks and adversarial workspace fixtures."""
from dataclasses import dataclass
import re
from ..errors import require

SYSTEM = 'S-1-5-18'
ADMINISTRATORS = 'S-1-5-32-544'
TRUSTED_INSTALLER = 'S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464'
ADMIN_OWNERS = frozenset({SYSTEM, ADMINISTRATORS, TRUSTED_INSTALLER})
# Rights which may change bytes, namespace, ownership or permissions. Directory
# FILE_DELETE_CHILD is included; registry CREATE_SUB_KEY/SET_VALUE are separate.
FILE_MUTATION = 0x40000000 | 0x10000000 | 0x000D0156
REGISTRY_MUTATION = 0x40000000 | 0x10000000 | 0x000D0026


def sid(value: str) -> str:
    require(type(value) is str and re.fullmatch(r'S-1-\d+(?:-\d+){1,15}', value) is not None,
            10, 'INVALID_SID')
    require(all(int(x) <= 0xffffffff for x in value.split('-')[3:]), 10, 'INVALID_SID')
    return value


@dataclass(frozen=True)
class Ace:
    kind: int  # ACCESS_ALLOWED_ACE=0, ACCESS_DENIED_ACE=1
    flags: int
    mask: int
    trustee: str


@dataclass(frozen=True)
class Security:
    owner: str
    dacl_present: bool
    dacl_null: bool
    protected: bool
    aces: tuple[Ace, ...]


def check_security(value: Security, *, owners: frozenset[str],
                   writers: frozenset[str], confidential: bool,
                   readers: frozenset[str] = frozenset(), registry: bool = False,
                   require_protected: bool = False) -> None:
    """Conservative allowlist; unsupported ACEs fail instead of being ignored.

    Inherit-only ACEs still count: a broad inheritable write grant is unsafe for
    the protected children even if it does not affect this directory itself.
    Denies never excuse a dangerous broad allow (no incorrect ACL simulation).
    """
    require(value.owner in owners, 12, 'UNTRUSTED_OBJECT_OWNER')
    require(value.dacl_present and not value.dacl_null, 12, 'UNRESTRICTED_DACL')
    require(not require_protected or value.protected, 12, 'INHERITED_TRUST_BOUNDARY')
    mutation = REGISTRY_MUTATION if registry else FILE_MUTATION
    for ace in value.aces:
        sid(ace.trustee)
        require(ace.kind in (0, 1), 12, 'UNSUPPORTED_ACE')
        if ace.kind == 1:
            continue
        if ace.mask & mutation:
            require(ace.trustee in writers, 12, 'UNAUTHORIZED_WRITER')
        if confidential and ace.mask:
            require(ace.trustee in readers | writers, 12, 'UNAUTHORIZED_READER')


def metadata_sddl(operators: frozenset[str]) -> str:
    """Explicit protected metadata ACL; never BUILTIN Users or Everyone."""
    for item in operators:
        sid(item)
    principals = sorted(operators | {SYSTEM, ADMINISTRATORS})
    # Owner/group are assigned by Windows to the actual creator. Verified after
    # creation; no privilege-dependent implicit owner change is attempted.
    return 'D:P' + ''.join('(A;OICI;FA;;;' + item + ')' for item in principals)


def mutex_sddl(operators: frozenset[str]) -> str:
    for item in operators:
        sid(item)
    return 'D:P' + ''.join('(A;;0x001F0001;;;' + item + ')'
                          for item in sorted(operators | {SYSTEM, ADMINISTRATORS}))
