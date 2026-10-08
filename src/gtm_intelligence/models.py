from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GTMIntelligenceSnapshot:
    """Tenant-level factual GTM intelligence derived from Lead 360."""

    tenant_id: str

    total_leads: int
    leads_with_engagement: int
    leads_with_registration: int
    leads_with_enrollment: int

    engagement_intensity_distribution: Tuple[Tuple[str, int], ...]
    campaign_breadth_distribution: Tuple[Tuple[int, int], ...]
    course_breadth_distribution: Tuple[Tuple[int, int], ...]
    recency_distribution: Tuple[Tuple[str, int], ...]

    top_engaged_leads: Tuple[Tuple[str, str, int], ...]

    channel_coverage: Tuple[Tuple[str, int], ...]
    event_type_coverage: Tuple[Tuple[str, int], ...]

    funnel_progression: Tuple[Tuple[str, int], ...]
