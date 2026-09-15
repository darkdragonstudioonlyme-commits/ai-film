"""Operation executor port and synthetic implementation used by workspace tests only."""
from dataclasses import dataclass
from typing import Protocol
from .errors import require

class Executor(Protocol):
    def execute(self,operation:dict)->dict: ...

@dataclass
class FakeExecutor:
    """Workspace fixture. Production factory never constructs this class."""
    outcomes:dict
    calls:list
    def execute(self,operation):
        require(type(operation) is dict and 'action' in operation,10,'OPERATION_SCHEMA')
        self.calls.append(operation['action'])
        return self.outcomes.get(operation['action'],{'terminal_observed':False,'postconditions_observed':False,'no_pending_writer':True,'evidence_digest':None,'native_witness':None,'action':operation['action']})
