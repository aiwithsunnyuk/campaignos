from dataclasses import dataclass
from typing import Any


@dataclass
class LeadScoreResult:
    contact_id: str
    lead_score: int
    score_band: str
    lifecycle_stage: str
    qualification: str
    recommended_action: str
    score_breakdown: dict[str, int]


@dataclass
class ScoringWeights:
    engagement_weight: int = 40
    profile_weight: int = 30
    lifecycle_weight: int = 20
    consent_weight: int = 10


@dataclass
class LifecycleRule:
    minimum_score: int
    lifecycle_stage: str


DEFAULT_LIFECYCLE_RULES = [
    LifecycleRule(80, "MQL"),
    LifecycleRule(60, "Engaged"),
    LifecycleRule(40, "Marketing Qualified Prospect"),
    LifecycleRule(0, "Lead"),
]