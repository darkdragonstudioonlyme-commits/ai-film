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
