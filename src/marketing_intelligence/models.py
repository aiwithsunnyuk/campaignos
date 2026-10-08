from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class MarketingIntelligence:
    """Interpreted tenant-level marketing intelligence."""

    tenant_id: str

    total_leads: int
    engaged_leads: int
    registered_leads: int
    enrolled_leads: int

    engagement_rate: float
    registration_rate: float
    enrollment_rate: float

    top_channels: Tuple[Tuple[str, int], ...]
    top_event_types: Tuple[Tuple[str, int], ...]

    funnel_bottleneck: str
    headline: str
