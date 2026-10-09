from __future__ import annotations

from src.next_best_action.lead_service import LeadNextBestActionService
from src.session.identity_session import IdentitySession


class IdentityLeadNextBestActionService:
    """Tenant-scoped Lead NBA access using an authenticated identity session."""

    def __init__(
        self,
        lead_service: LeadNextBestActionService | None = None,
    ) -> None:
        self._lead_service = lead_service or LeadNextBestActionService()

    def get_next_best_action(
        self,
        identity_session: IdentitySession,
        lead,
    ):
        """Resolve Lead NBA using the tenant carried by the authenticated identity."""
        return self._lead_service.get_next_best_action(
            lead=lead,
            tenant_id=identity_session.tenant_id,
        )
