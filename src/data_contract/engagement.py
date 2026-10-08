from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Engagement:
    """Canonical representation of a lead/customer interaction."""

    engagement_id: str
    tenant_id: str
    lead_id: str

    channel: str
    event_type: str

    campaign_id: Optional[str]
    course_id: Optional[str]

    occurred_at: str

    metadata: Optional[dict] = None
