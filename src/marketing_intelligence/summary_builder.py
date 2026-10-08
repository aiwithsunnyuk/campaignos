from .card_builder import MarketingIntelligenceCardBuilder
from .engine import MarketingIntelligenceEngine
from .feed_builder import MarketingIntelligenceFeedBuilder
from .kpi_builder import MarketingIntelligenceKPIBuilder
from .models import MarketingIntelligence
from .summary import CommandCenterSummary


class CommandCenterSummaryBuilder:
    """Compose marketing intelligence into a Command Center response."""

    def build(
        self,
        intelligence: MarketingIntelligence,
    ) -> CommandCenterSummary:
        kpis = MarketingIntelligenceKPIBuilder().build(
            intelligence
        )

        cards = MarketingIntelligenceCardBuilder().build(
            intelligence
        )

        feed = MarketingIntelligenceFeedBuilder().build(
            cards
        )

        return CommandCenterSummary(
            tenant_id=intelligence.tenant_id,
            headline=intelligence.headline,
            kpis=kpis,
            intelligence_feed=feed,
        )
