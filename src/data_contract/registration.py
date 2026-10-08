from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Registration:
    """Canonical representation of a course/demo registration."""

    registration_id: str
    tenant_id: str
    lead_id: str
    course_id: str

    registration_type: str
    status: str

    registered_at: str
    converted_at: Optional[str] = None
