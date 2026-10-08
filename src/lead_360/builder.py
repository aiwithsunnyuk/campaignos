from collections import defaultdict
from typing import Iterable

from src.data_contract import (
    Engagement,
    Enrollment,
    Lead,
    Registration,
)

from .models import Lead360


class Lead360Builder:
    """Build tenant-scoped Lead360 views from canonical GTM records."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def build(
        self,
        leads: Iterable[Lead],
        engagements: Iterable[Engagement],
        registrations: Iterable[Registration],
        enrollments: Iterable[Enrollment],
    ) -> list[Lead360]:
        leads = list(leads)
        engagements = list(engagements)
        registrations = list(registrations)
        enrollments = list(enrollments)

        self._validate_tenant_scope(leads)
        self._validate_tenant_scope(engagements)
        self._validate_tenant_scope(registrations)
        self._validate_tenant_scope(enrollments)

        lead_by_id = {
            lead.lead_id: lead
            for lead in leads
        }

        self._validate_references(
            engagements,
            lead_by_id,
            "engagement",
        )

        self._validate_references(
            registrations,
            lead_by_id,
            "registration",
        )

        self._validate_references(
            enrollments,
            lead_by_id,
            "enrollment",
        )

        engagements_by_lead: dict[str, list[Engagement]] = defaultdict(list)
        registrations_by_lead: dict[str, list[Registration]] = defaultdict(list)
        enrollments_by_lead: dict[str, list[Enrollment]] = defaultdict(list)

        for engagement in engagements:
            engagements_by_lead[engagement.lead_id].append(engagement)

        for registration in registrations:
            registrations_by_lead[registration.lead_id].append(registration)

        for enrollment in enrollments:
            enrollments_by_lead[enrollment.lead_id].append(enrollment)

        result: list[Lead360] = []

        for lead in leads:
            lead_engagements = engagements_by_lead.get(
                lead.lead_id,
                [],
            )

            lead_registrations = registrations_by_lead.get(
                lead.lead_id,
                [],
            )

            lead_enrollments = enrollments_by_lead.get(
                lead.lead_id,
                [],
            )

            campaign_ids = {
                engagement.campaign_id
                for engagement in lead_engagements
                if engagement.campaign_id
            }

            course_ids = {
                engagement.course_id
                for engagement in lead_engagements
                if engagement.course_id
            }

            channels = {
                engagement.channel
                for engagement in lead_engagements
                if engagement.channel
            }

            event_types = {
                engagement.event_type
                for engagement in lead_engagements
                if engagement.event_type
            }

            engagement_dates = [
                engagement.occurred_at
                for engagement in lead_engagements
                if engagement.occurred_at
            ]

            result.append(
                Lead360(
                    lead_id=lead.lead_id,
                    tenant_id=lead.tenant_id,
                    first_name=lead.first_name,
                    last_name=lead.last_name,
                    email=lead.email,
                    phone=lead.phone,
                    source=lead.source,
                    lifecycle_stage=lead.lifecycle_stage,
                    interest=lead.interest,
                    course_id=lead.course_id,
                    lead_score=lead.lead_score,
                    total_engagements=len(lead_engagements),
                    unique_campaigns=len(campaign_ids),
                    unique_courses=len(course_ids),
                    last_engagement_at=(
                        max(engagement_dates)
                        if engagement_dates
                        else None
                    ),
                    registration_count=len(lead_registrations),
                    enrollment_count=len(lead_enrollments),
                    engagement_channels=tuple(
                        sorted(channels)
                    ),
                    engagement_event_types=tuple(
                        sorted(event_types)
                    ),
                )
            )

        return result

    def _validate_tenant_scope(self, records: list) -> None:
        for record in records:
            if record.tenant_id != self.tenant_id:
                raise ValueError(
                    f"Tenant mismatch: builder={self.tenant_id}, "
                    f"record={record.tenant_id}"
                )

    @staticmethod
    def _validate_references(
        records: list,
        lead_by_id: dict[str, Lead],
        record_type: str,
    ) -> None:
        for record in records:
            if record.lead_id not in lead_by_id:
                raise ValueError(
                    f"{record_type} references unknown lead: "
                    f"{record.lead_id}"
                )
