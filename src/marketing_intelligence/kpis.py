from dataclasses import dataclass
from typing import Literal


Priority = Literal["critical", "high", "medium", "low"]


@dataclass(frozen=True)
class IntelligenceKPI:
    key: str
    label: str
    value: float | int | str
    unit: str
    priority: Priority
    explanation: str
