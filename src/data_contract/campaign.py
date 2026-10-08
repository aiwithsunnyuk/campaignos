from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Campaign:
    """Canonical CampaignOS representation of a campaign."""

    campaign_id: str
    tenant_id: str

    name: str
    channel: str
    campaign_type: str

    status: str

    start_date: str
    end_date: Optional[str]

    budget: Optional[float]

    created_at: str
    updated_at: str
