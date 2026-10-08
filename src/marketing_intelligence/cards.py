from dataclasses import dataclass
from typing import Literal


CardPriority = Literal["critical", "high", "medium", "low"]


@dataclass(frozen=True)
class IntelligenceCard:
    card_id: str
    tenant_id: str
    title: str
    priority: CardPriority
    metric: str
    value: str
    evidence: tuple[str, ...]
    recommendation: str
