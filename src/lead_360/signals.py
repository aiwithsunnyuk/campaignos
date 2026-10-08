from dataclasses import dataclass


@dataclass(frozen=True)
class IntelligenceSignals:
    """Explainable behavioral signals derived from a Lead360 record."""

    engagement_intensity: str
    campaign_breadth: str
    course_breadth: str
    recency: str
    registration_signal: str
    enrollment_signal: str
    funnel_progression: str
