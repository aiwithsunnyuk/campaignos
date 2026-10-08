from dataclasses import dataclass
from typing import Literal


ActionStatus = Literal[
    "recommended",
    "pending_approval",
    "approved",
    "rejected",
    "ready_for_execution",
    "executed",
]


@dataclass(frozen=True)
class GovernedAction:
    action_id: str
    tenant_id: str
    lead_id: str
    action_type: str
    recommendation: str
    status: ActionStatus = "recommended"
    approved_by: str | None = None
    executed_by: str | None = None
