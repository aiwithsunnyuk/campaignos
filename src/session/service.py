from src.auth.authorization import authorize
from src.auth.models import Permission
from src.auth.users import get_user

from .models import AuthenticatedSession


class AuthenticationService:
    def authenticate(self, user_id: str) -> AuthenticatedSession:
        user = get_user(user_id)

        if not user.active:
            raise PermissionError("User is inactive.")

        return AuthenticatedSession(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name,
            tenant_id=user.tenant_id,
            role=user.role,
        )

    def authorize_tenant_access(
        self,
        session: AuthenticatedSession,
        tenant_id: str,
    ) -> bool:
        if not session.authenticated:
            raise PermissionError("User is not authenticated.")

        if session.tenant_id != tenant_id:
            raise PermissionError(
                "Authenticated user cannot access another tenant."
            )

        return True

    def authorize_permission(
        self,
        session: AuthenticatedSession,
        permission: Permission,
    ) -> bool:
        user = get_user(session.user_id)

        authorize(
            user=user,
            permission=permission,
            resource_tenant_id=session.tenant_id,
        )

        return True
