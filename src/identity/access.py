from __future__ import annotations

from pathlib import Path

from .membership_config import MembershipConfigService
from .models import Identity, TenantMembership


class IdentityAccessError(PermissionError):
    """Raised when an authenticated identity cannot access CampaignOS."""


ROLE_TO_DEMO_USER = {
    ("reetha", "director"): "reetha-director",
    ("reetha", "marketing_manager"): "reetha-marketing",
    ("reetha", "sales_user"): "reetha-sales",
}


class IdentityAccessService:
    def __init__(
        self,
        membership_config_path: str | Path = "config/identity_memberships.yaml",
    ):
        self.membership_service = MembershipConfigService(
            membership_config_path
        )

    def resolve_membership(
        self,
        identity: Identity,
        tenant_id: str,
    ) -> TenantMembership:
        memberships = self.membership_service.load()

        matching = [
            membership
            for membership in memberships
            if membership.identity_id == f"email:{identity.email}"
            and membership.tenant_id == tenant_id
            and membership.status == "active"
        ]

        if not matching:
            raise IdentityAccessError(
                "Your Google account is authenticated, "
                "but it is not authorized for this CampaignOS workspace."
            )

        if len(matching) > 1:
            raise IdentityAccessError(
                "Multiple active memberships were found for this identity."
            )

        return matching[0]

    def resolve_campaignos_user(
        self,
        identity: Identity,
        tenant_id: str,
    ) -> tuple[str, TenantMembership]:
        membership = self.resolve_membership(identity, tenant_id)

        user_id = ROLE_TO_DEMO_USER.get(
            (membership.tenant_id, membership.role)
        )

        if user_id is None:
            raise IdentityAccessError(
                f"No CampaignOS user mapping exists for role "
                f"'{membership.role}'."
            )

        return user_id, membership
