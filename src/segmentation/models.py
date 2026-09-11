from dataclasses import dataclass, field
from typing import Any


@dataclass
class SegmentRule:
    field: str
    operator: str
    value: Any


@dataclass
class SegmentDefinition:
    segment_id: str
    segment_name: str
    description: str = ""
    rules: list[SegmentRule] = field(default_factory=list)
    logic: str = "AND"

    def validate(self) -> None:
        if not self.segment_id.strip():
            raise ValueError("Segment ID is required.")

        if not self.segment_name.strip():
            raise ValueError("Segment name is required.")

        if not self.rules:
            raise ValueError("At least one segmentation rule is required.")

        if self.logic not in {"AND", "OR"}:
            raise ValueError("Logic must be either AND or OR.")


@dataclass
class SegmentResult:
    segment_id: str
    segment_name: str
    audience_count: int
    audience_percentage: float
    contacts: Any