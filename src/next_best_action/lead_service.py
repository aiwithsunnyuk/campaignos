from src.auth.authorization import authorize
from src.auth.models import Permission, User
from src.lead_360.models import Lead360

from .lead_engine import LeadNextBestActionEngine
from .models import NextBestAction


class LeadNextBestActionService:
    """Tenant-safe service for lead-level next best action."""

    def recommend(
        self,
        user: User,
        tenant_id: str,
        lead: Lead360,
    ) -> NextBestAction:
        authorize(
            user=user,
            permission=Permission.GENERATE_AI_RECOMMENDATION,
            resource_tenant_id=tenant_id,
        )

        if lead.tenant_id != tenant_id:
            raise ValueError(
                "Lead tenant does not match the requested tenant."
            )

        return LeadNextBestActionEngine().recommend(lead)
