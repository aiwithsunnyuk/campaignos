from dataclasses import dataclass
from typing import Literal


FeedPriority = Literal["critical", "high", "medium", "low"]


@dataclass(frozen=True)
class IntelligenceFeedItem:
    feed_id: str
    tenant_id: str
    priority: FeedPriority
    title: str
    metric: str
    value: str
    evidence: tuple[str, ...]
    recommendation: str
