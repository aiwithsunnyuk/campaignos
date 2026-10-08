from dataclasses import dataclass
from typing import Literal


ExecutionStatus = Literal[
    "dry_run",
    "executed",
    "failed",
]


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    action_id: str
    tenant_id: str
    status: ExecutionStatus
    action_type: str
    message: str
