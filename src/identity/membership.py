from __future__ import annotations

from .models import Identity, TenantMembership


class TenantMembershipService:
    """
    Resolves tenant access independently from authentication.

    Authentication answers:
        Who is this person?

    Membership answers:
        Which tenant can this person access?

    Role answers:
        What can they do there?
    """

    def __init__(self, memberships: list[TenantMembership] | None = None):
        self._memberships = memberships or []

    def add_membership(self, membership: TenantMembership) -> None:
        self._memberships.append(membership)

    def get_memberships(
        self,
        identity: Identity,
    ) -> list[TenantMembership]:
        identity_ids = {
            identity.identity_id,
            f"email:{identity.email}",
        }

        return [
            membership
            for membership in self._memberships
            if membership.identity_id in identity_ids
            and membership.status == "active"
        ]

    def resolve(
        self,
        identity: Identity,
        tenant_id: str,
    ) -> TenantMembership:
        if not identity.verified:
            raise PermissionError(
                "Identity must be verified before tenant access."
            )

        matches = [
            membership
            for membership in self.get_memberships(identity)
            if membership.tenant_id == tenant_id
        ]

        if not matches:
            raise PermissionError(
                f"Identity has no active membership for tenant '{tenant_id}'."
            )

        if len(matches) > 1:
            raise ValueError(
                "Multiple active memberships found for the same tenant."
            )

        return matches[0]
