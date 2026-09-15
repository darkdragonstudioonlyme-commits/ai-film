"""D00-09 normalized failures; exception text must never include raw input."""
from enum import IntEnum
import re

class Exit(IntEnum):
    OK=0
    PARTIAL_OPTIONAL=2
    INPUT=10
    PREREQUISITE=11
    PERMISSION=12
    RESOURCE=13
    NETWORK=14
    INTEGRITY=15
    DRIFT=16
    TIMEOUT=17
    IO=18
    ASSERTION=19
    OPERATOR=20
    BUSY=21
    INCOMPLETE=22
    REDACTION=23

class P00Error(Exception):
    def __init__(self, code: int, reason: str):
        self.code=Exit(code)
        if not re.fullmatch(r'[A-Z][A-Z0-9_]{0,79}',reason):
            raise ValueError('INVALID_INTERNAL_REASON_CODE')
        self.reason=reason
        super().__init__(reason)
    def safe(self) -> dict:
        return {'exit':int(self.code),'reason':self.reason,'host_ready':False}

def require(condition: bool, code: int, reason: str) -> None:
    if not condition:
        raise P00Error(code,reason)
