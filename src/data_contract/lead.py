from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Lead:
    """
    Canonical CampaignOS representation of a lead.

    Source systems such as CRM, website forms, spreadsheets,
    advertising platforms, or APIs must map into this contract.
    """

    lead_id: str
    tenant_id: str

    first_name: str
    last_name: Optional[str]

    email: Optional[str]
    phone: Optional[str]

    source: str
    lifecycle_stage: str

    interest: Optional[str]
    course_id: Optional[str]

    lead_score: Optional[float]

    created_at: str
    updated_at: str
