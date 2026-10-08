from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Course:
    """Canonical CampaignOS representation of a course or offering."""

    course_id: str
    tenant_id: str

    name: str
    category: Optional[str]

    delivery_mode: Optional[str]
    duration: Optional[str]

    price: Optional[float]

    status: str

    created_at: str
    updated_at: str
