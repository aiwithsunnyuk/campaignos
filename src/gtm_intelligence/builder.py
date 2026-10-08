from collections import Counter
from datetime import datetime
from typing import Iterable

from src.lead_360.models import Lead360
from .models import GTMIntelligenceSnapshot


class GTMIntelligenceSnapshotBuilder:
    """Build factual tenant-level GTM intelligence from Lead 360 records."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def build(
        self,
        records: Iterable[Lead360],
        as_of: str | None = None,
    ) -> GTMIntelligenceSnapshot:
        records = list(records)

        self._validate_tenant_scope(records)

        total_leads = len(records)

        leads_with_engagement = sum(
            record.total_engagements > 0 for record in records
        )
        leads_with_registration = sum(
            record.registration_count > 0 for record in records
        )
        leads_with_enrollment = sum(
            record.enrollment_count > 0 for record in records
        )

        engagement_intensity = Counter(
            self._engagement_band(record.total_engagements)
            for record in records
        )

        campaign_breadth = Counter(
            record.unique_campaigns for record in records
        )

        course_breadth = Counter(
            record.unique_courses for record in records
        )

        recency = Counter(
            self._recency_band(record.last_engagement_at, as_of)
            for record in records
        )

        top_engaged = tuple(
            (
                record.lead_id,
                f"{record.first_name} {record.last_name}",
                record.total_engagements,
            )
            for record in sorted(
                records,
                key=lambda item: (-item.total_engagements, item.lead_id),
            )[:10]
        )

        channels = Counter()
        event_types = Counter()

        for record in records:
            channels.update(record.engagement_channels)
            event_types.update(record.engagement_event_types)

        funnel = (
            ("Lead", total_leads),
            ("Engaged", leads_with_engagement),
            ("Registered", leads_with_registration),
            ("Enrolled", leads_with_enrollment),
        )

        return GTMIntelligenceSnapshot(
            tenant_id=self.tenant_id,
            total_leads=total_leads,
            leads_with_engagement=leads_with_engagement,
            leads_with_registration=leads_with_registration,
            leads_with_enrollment=leads_with_enrollment,
            engagement_intensity_distribution=tuple(
                sorted(engagement_intensity.items())
            ),
            campaign_breadth_distribution=tuple(
                sorted(campaign_breadth.items())
            ),
            course_breadth_distribution=tuple(
                sorted(course_breadth.items())
            ),
            recency_distribution=tuple(
                sorted(recency.items())
            ),
            top_engaged_leads=top_engaged,
            channel_coverage=tuple(
                sorted(channels.items())
            ),
            event_type_coverage=tuple(
                sorted(event_types.items())
            ),
            funnel_progression=funnel,
        )

    def _validate_tenant_scope(self, records: list[Lead360]) -> None:
        for record in records:
            if record.tenant_id != self.tenant_id:
                raise ValueError(
                    f"Tenant mismatch: builder={self.tenant_id}, "
                    f"record={record.tenant_id}"
                )

    @staticmethod
    def _engagement_band(count: int) -> str:
        if count == 0:
            return "none"
        if count <= 3:
            return "low"
        if count <= 7:
            return "medium"
        return "high"

    @staticmethod
    def _recency_band(
        last_engagement_at: str | None,
        as_of: str | None,
    ) -> str:
        if not last_engagement_at:
            return "never"

        if not as_of:
            return "known"

        last = datetime.fromisoformat(last_engagement_at)
        reference = datetime.fromisoformat(as_of)

        days = (reference - last).days

        if days <= 7:
            return "recent"
        if days <= 30:
            return "aging"
        return "stale"
