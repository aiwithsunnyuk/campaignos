from dataclasses import dataclass

from src.auth.models import Role
from src.session.models import AuthenticatedSession


@dataclass(frozen=True)
class TenantWorkspace:
    tenant_id: str
    tenant_name: str
    user_id: str
    display_name: str
    role: Role
    authenticated: bool


def workspace_from_session(
    session: AuthenticatedSession,
    tenant_name: str,
) -> TenantWorkspace:
    if not session.authenticated:
        raise PermissionError("Workspace requires authentication.")

    return TenantWorkspace(
        tenant_id=session.tenant_id,
        tenant_name=tenant_name,
        user_id=session.user_id,
        display_name=session.display_name,
        role=session.role,
        authenticated=True,
    )
