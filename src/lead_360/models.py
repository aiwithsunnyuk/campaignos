from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Lead360:
    lead_id: str
    tenant_id: str

    # Identity
    first_name: str
    last_name: str
    email: str
    phone: str

    # Lead profile
    source: str
    lifecycle_stage: str
    interest: str
    course_id: Optional[str]

    # Existing lead score
    lead_score: float

    # Behavioral summary
    total_engagements: int
    unique_campaigns: int
    unique_courses: int
    last_engagement_at: Optional[str]

    # Funnel summary
    registration_count: int
    enrollment_count: int

    # Derived intelligence signals
    engagement_channels: tuple[str, ...]
    engagement_event_types: tuple[str, ...]
