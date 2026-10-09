from dataclasses import dataclass

from src.auth.models import Role


@dataclass(frozen=True)
class AuthenticatedSession:
    user_id: str
    email: str
    display_name: str
    tenant_id: str
    role: Role
    authenticated: bool = True
