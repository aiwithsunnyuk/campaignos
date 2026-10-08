from .cards import IntelligenceCard
from .feed import IntelligenceFeedItem


_PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


class MarketingIntelligenceFeedBuilder:
    """Build an ordered intelligence feed from prioritized cards."""

    def build(
        self,
        cards: tuple[IntelligenceCard, ...],
    ) -> tuple[IntelligenceFeedItem, ...]:
        ordered = sorted(
            cards,
            key=lambda card: (
                _PRIORITY_ORDER[card.priority],
                card.card_id,
            ),
        )

        return tuple(
            IntelligenceFeedItem(
                feed_id=f"FEED-{card.card_id}",
                tenant_id=card.tenant_id,
                priority=card.priority,
                title=card.title,
                metric=card.metric,
                value=card.value,
                evidence=card.evidence,
                recommendation=card.recommendation,
            )
            for card in ordered
        )
