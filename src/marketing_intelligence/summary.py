from dataclasses import dataclass

from .feed import IntelligenceFeedItem
from .kpis import IntelligenceKPI


@dataclass(frozen=True)
class CommandCenterSummary:
    """Tenant-level response contract for the CampaignOS Command Center."""

    tenant_id: str
    headline: str
    kpis: tuple[IntelligenceKPI, ...]
    intelligence_feed: tuple[IntelligenceFeedItem, ...]
