# API-reference checks during implementation

Checked 2026-09-14. Đây là tham khảo API bên ngoài, phân biệt với normative project contracts. Không research/chọn runtime version, model hoặc GPU mới; không chứng minh Windows compatibility.

| Primary source | Phạm vi tham khảo | Giới hạn |
|---|---|---|
| Microsoft CreateMutexW: https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw | Named mutex, security descriptor và ownership behavior | Native mutex adapter chưa được implement hoặc test |
| Microsoft kernel namespaces: https://learn.microsoft.com/en-us/windows/win32/termserv/kernel-object-namespaces | Global/session namespaces | Không dùng MemoryGuard/POSIX workspace để claim cross-session/SID proof |
| Python 3.13 subprocess: https://docs.python.org/3.13/library/subprocess.html | argv boundaries, timeout và child lifecycle distinctions | Native supervisor chưa implement; workspace subprocess chỉ launch Python CLI tests |
| Microsoft WSL basic commands: https://learn.microsoft.com/en-us/windows/wsl/basic-commands | Explicit target/import/export/terminate command family | Command compiler chưa có locked-runtime behavioral proof; không execute từ tài liệu |

Căn cứ behavior, acceptance và mode vẫn là Blueprint và approved normative V2. No citation above is a lab qualification receipt.
