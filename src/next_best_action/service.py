from src.auth.authorization import authorize
from src.auth.models import Permission, User
from src.gtm_intelligence.models import GTMIntelligenceSnapshot
from src.gtm_intelligence.signals import GTMExplainableSignalBuilder

from .engine import NextBestActionEngine
from .models import NextBestAction


class NextBestActionService:
    """Tenant-safe service for generating explainable NBA recommendations."""

    def recommend(
        self,
        user: User,
        tenant_id: str,
        lead_id: str,
        snapshot: GTMIntelligenceSnapshot,
    ) -> NextBestAction:
        authorize(
            user=user,
            permission=Permission.GENERATE_AI_RECOMMENDATION,
            resource_tenant_id=tenant_id,
        )

        if snapshot.tenant_id != tenant_id:
            raise ValueError(
                "Snapshot tenant does not match the requested tenant."
            )

        signals = GTMExplainableSignalBuilder(snapshot).build()

        return NextBestActionEngine().recommend(
            lead_id=lead_id,
            tenant_id=tenant_id,
            signals=signals,
        )
