from src.auth.models import Permission
from src.session import AuthenticatedSession, AuthenticationService
from src.tenancy.registry import get_tenant

from .models import TenantWorkspace, workspace_from_session


class TenantWorkspaceService:
    def __init__(
        self,
        authentication_service: AuthenticationService | None = None,
    ):
        self.authentication_service = (
            authentication_service
            or AuthenticationService()
        )

    def resolve(
        self,
        session: AuthenticatedSession,
    ) -> TenantWorkspace:
        if not session.authenticated:
            raise PermissionError("Workspace requires authentication.")

        tenant = get_tenant(session.tenant_id)

        if tenant.status != "active":
            raise PermissionError("Tenant is inactive.")

        return workspace_from_session(
            session=session,
            tenant_name=tenant.name,
        )

    def require_permission(
        self,
        workspace: TenantWorkspace,
        permission: Permission,
    ) -> bool:
        session = self.authentication_service.authenticate(
            workspace.user_id
        )

        self.authentication_service.authorize_tenant_access(
            session,
            workspace.tenant_id,
        )

        return self.authentication_service.authorize_permission(
            session,
            permission,
        )


def workspace_from_identity_session(identity_session):
    from src.workspace.models import TenantWorkspace

    return TenantWorkspace(
        tenant_id=identity_session.tenant_id,
        tenant_name=identity_session.tenant_id,
        user_id=identity_session.user_id,
        display_name=identity_session.display_name,
        role=identity_session.role,
        authenticated=True,
    )
