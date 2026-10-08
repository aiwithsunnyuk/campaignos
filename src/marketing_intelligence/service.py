from typing import Iterable

from src.auth.authorization import authorize
from src.auth.models import Permission, User
from src.gtm_intelligence.builder import GTMIntelligenceSnapshotBuilder
from src.lead_360.models import Lead360

from .engine import MarketingIntelligenceEngine
from .models import MarketingIntelligence


class MarketingIntelligenceService:
    """Tenant-safe application service for marketing intelligence."""

    def get_intelligence(
        self,
        user: User,
        tenant_id: str,
        records: Iterable[Lead360],
        as_of: str | None = None,
    ) -> MarketingIntelligence:
        authorize(
            user=user,
            permission=Permission.VIEW_ANALYTICS,
            resource_tenant_id=tenant_id,
        )

        snapshot = GTMIntelligenceSnapshotBuilder(
            tenant_id=tenant_id,
        ).build(
            records=records,
            as_of=as_of,
        )

        return MarketingIntelligenceEngine().build(snapshot)
