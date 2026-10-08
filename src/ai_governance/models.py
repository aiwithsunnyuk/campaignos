from dataclasses import dataclass
from typing import Literal


ApprovalStatus = Literal[
    "pending",
    "approved",
    "rejected",
]


@dataclass(frozen=True)
class ApprovalRequest:
    request_id: str
    tenant_id: str
    lead_id: str
    action_type: str
    recommendation: str
    reason: str
    evidence: tuple[str, ...]
    status: ApprovalStatus = "pending"
    approved_by: str | None = None
    rejection_reason: str | None = None
