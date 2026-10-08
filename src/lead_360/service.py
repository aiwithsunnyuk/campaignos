from typing import Sequence

from src.auth.authorization import authorize
from src.auth.models import Permission, User

from .builder import Lead360Builder
from .models import Lead360


class Lead360Service:
    """Tenant-safe service for retrieving Lead 360 intelligence."""

    def get_lead(
        self,
        user: User,
        tenant_id: str,
        lead_id: str,
        leads: Sequence,
        engagements: Sequence,
        registrations: Sequence,
        enrollments: Sequence,
    ) -> Lead360:
        authorize(
            user=user,
            permission=Permission.VIEW_LEADS,
            resource_tenant_id=tenant_id,
        )

        records = (
            *leads,
            *engagements,
            *registrations,
            *enrollments,
        )

        for record in records:
            if record.tenant_id != tenant_id:
                raise ValueError(
                    "Record tenant does not match the requested tenant."
                )

        lead_360_records = Lead360Builder(
            tenant_id=tenant_id,
        ).build(
            leads=leads,
            engagements=engagements,
            registrations=registrations,
            enrollments=enrollments,
        )

        for record in lead_360_records:
            if record.lead_id == lead_id:
                return record

        raise ValueError(f"Lead '{lead_id}' was not found.")
