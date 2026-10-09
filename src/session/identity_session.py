from __future__ import annotations

from dataclasses import dataclass

from src.identity.models import Identity, TenantMembership


@dataclass(frozen=True)
class IdentitySession:
    identity: Identity
    membership: TenantMembership

    @property
    def tenant_id(self) -> str:
        return self.membership.tenant_id

    @property
    def role(self) -> str:
        return self.membership.role

    @property
    def user_id(self) -> str:
        return self.identity.identity_id

    @property
    def email(self) -> str:
        return self.identity.email

    @property
    def display_name(self) -> str:
        return self.identity.display_name


def identity_session_from_context(identity, membership):
    return IdentitySession(
        identity=identity,
        membership=membership,
    )


def identity_session_from_context(identity, membership):
    return IdentitySession(
        identity=identity,
        membership=membership,
    )
