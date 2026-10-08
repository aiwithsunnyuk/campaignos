from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Enrollment:
    """Canonical CampaignOS representation of a course enrollment."""

    enrollment_id: str
    tenant_id: str

    lead_id: str
    course_id: str

    enrollment_status: str
    enrollment_date: str

    amount: float
    payment_status: str

    registration_id: Optional[str] = None
