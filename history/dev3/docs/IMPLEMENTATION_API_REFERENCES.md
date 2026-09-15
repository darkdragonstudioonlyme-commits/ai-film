# API references checked during implementation

Checked 2026-09-14. These are external primary API references used for source authoring, not normative project design, code review or native compatibility evidence. No runtime/model/GPU/provider selection is made here.

| Primary source | Source use | Limitation |
|---|---|---|
| https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexexa | Named/global mutex, desired access and ownership; source uses the Unicode W variant | Concrete adapter authored; no Windows cross-session execution |
| https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw | Named mutex behavior and security descriptor | Does not prove project's ACL or locking contract |
| https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo | Security descriptors for handles | Actual native security enforcement NOT_RUN |
| https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation | Token identity/elevation structures | ABI/runtime behavior NOT_RUN |
| https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew | Final handle path checks | Does not replace native filesystem/path tests |
| https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-points-and-file-operations | Reparse/open behavior | Native reparse rejection NOT_RUN |
| https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw | Explicit application, mutable command line, child creation | Supervisor source tested only with fake API |
| https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute | Restricted handle inheritance via attribute list | No native proof of job/service lifecycle |
| https://learn.microsoft.com/en-us/windows/win32/termserv/kernel-object-namespaces | Global/session namespace distinction | Fixed namespace does not control unrelated admins |
| https://learn.microsoft.com/en-us/windows/wsl/basic-commands | Existing explicit WSL command family | No new WSL version choice; no command executed |

No page above is a test result, approval or qualification receipt. Source/test/host evidence remains separated.


## Narrow dev3 implementation lookups (2026-09-14)

These corroborate API usage only. They do not modify the approved design, select a version, prove native behavior, or count as code/host validation.

| Primary source | Authoring use |
|---|---|
| https://learn.microsoft.com/en-us/windows/win32/msi/-msiexecute-mutex | Installer transaction/process distinction; do not assume a client exit or missing mutex proves all work stopped |
| https://learn.microsoft.com/en-us/windows/win32/api/msi/nf-msi-msiqueryproductstatew | Product state observation source |
| https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects | Job/process accounting source |
| https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-optionalfeature | Read-only feature observation source |
| https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/dism-operating-system-package-servicing-command-line-options?view=windows-11 | Multiple feature names in an explicit DISM command; no atomic transaction claim |
| https://learn.microsoft.com/en-us/windows/wsl/build-custom-distro | Do not treat a configured default UID as actual completed first-login evidence |
| https://learn.microsoft.com/en-us/windows/win32/api/winhttp/nf-winhttp-winhttpgetieproxyconfigforcurrentuser | Read-only current-user proxy context and allocated result memory |
| https://learn.microsoft.com/en-us/windows/win32/api/winhttp/nf-winhttp-winhttpgetdefaultproxyconfiguration | Read-only WinHTTP proxy context; DIRECT refusal rather than bypass |

All sources above are external documentation, not results of a native command. No endpoint or Windows host was contacted by the authored scripts in this turn.
