"""Small error vocabulary shared by all interfaces."""
from enum import IntEnum

class Exit(IntEnum):
    OK=0; OPTIONAL=2; INPUT=10; BLOCKED=11; AUTH=12; TRUST=15; DRIFT=16; OUTPUT=18; STATE=19; ACTION=20; LOCK=21; MANDATORY=22; REDACTION=23

class P00Error(Exception):
    def __init__(self,code:int,reason:str):
        super().__init__(reason);self.code=int(code);self.reason=reason
    def safe(self): return {'exit':self.code,'reason':self.reason,'host_ready':False}

def require(condition,code,reason):
    if not condition: raise P00Error(code,reason)
