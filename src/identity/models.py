from dataclasses import dataclass
from typing import Literal


IdentityProvider = Literal[
    "work_email",
    "google",
    "apple",
    "github",
]

MembershipStatus = Literal[
    "invited",
    "active",
    "suspended",
]


@dataclass(frozen=True)
class Identity:
    identity_id: str
    email: str
    display_name: str
    provider: IdentityProvider
    provider_subject: str
    verified: bool


@dataclass(frozen=True)
class TenantMembership:
    identity_id: str
    tenant_id: str
    role: str
    status: MembershipStatus
    invited_by: str | None = None
