from datetime import datetime

from .models import Lead360
from .signals import IntelligenceSignals


class IntelligenceSignalBuilder:
    """Build deterministic, explainable signals from Lead360."""

    def build(self, lead: Lead360, as_of: str) -> IntelligenceSignals:
        return IntelligenceSignals(
            engagement_intensity=self._engagement_intensity(
                lead.total_engagements
            ),
            campaign_breadth=self._breadth(lead.unique_campaigns),
            course_breadth=self._breadth(lead.unique_courses),
            recency=self._recency(lead.last_engagement_at, as_of),
            registration_signal=self._registration_signal(
                lead.registration_count
            ),
            enrollment_signal=self._enrollment_signal(
                lead.enrollment_count
            ),
            funnel_progression=self._funnel_progression(
                lead.total_engagements,
                lead.registration_count,
                lead.enrollment_count,
            ),
        )

    @staticmethod
    def _engagement_intensity(count: int) -> str:
        if count == 0:
            return "none"
        if count <= 2:
            return "low"
        if count <= 6:
            return "medium"
        if count <= 10:
            return "high"
        return "very_high"

    @staticmethod
    def _breadth(count: int) -> str:
        if count == 0:
            return "none"
        if count == 1:
            return "single"
        if count <= 3:
            return "focused"
        if count <= 6:
            return "broad"
        return "very_broad"

    @staticmethod
    def _recency(last_engagement_at: str | None, as_of: str) -> str:
        if not last_engagement_at:
            return "no_activity"

        last = datetime.fromisoformat(last_engagement_at)
        reference = datetime.fromisoformat(as_of)
        days = (reference - last).days

        if days < 0:
            return "future_dated"
        if days <= 7:
            return "very_recent"
        if days <= 30:
            return "recent"
        if days <= 90:
            return "aging"
        return "stale"

    @staticmethod
    def _registration_signal(count: int) -> str:
        return "registered" if count > 0 else "not_registered"

    @staticmethod
    def _enrollment_signal(count: int) -> str:
        return "enrolled" if count > 0 else "not_enrolled"

    @staticmethod
    def _funnel_progression(
        engagements: int,
        registrations: int,
        enrollments: int,
    ) -> str:
        if enrollments > 0:
            return "enrolled"
        if registrations > 0:
            return "registered"
        if engagements > 0:
            return "engaged"
        return "new"
