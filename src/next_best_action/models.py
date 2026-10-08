from dataclasses import dataclass
from typing import Literal


ActionType = Literal[
    "registration_follow_up",
    "enrollment_follow_up",
    "re_engagement",
    "nurture",
    "monitor",
]

Priority = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class NextBestAction:
    lead_id: str
    tenant_id: str
    action_type: ActionType
    priority: Priority
    recommendation: str
    reason: str
    evidence: tuple[str, ...]
