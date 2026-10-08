from src.auth.authorization import authorize
from src.auth.models import Permission, User

from .approval_engine import ApprovalEngine
from .models import ApprovalRequest


class TenantApprovalService:
    """Applies existing RBAC and tenant isolation to approval decisions."""

    def __init__(self) -> None:
        self._approval_engine = ApprovalEngine()

    def approve(
        self,
        user: User,
        request: ApprovalRequest,
    ) -> ApprovalRequest:
        authorize(
            user=user,
            permission=Permission.APPROVE_AI_ACTION,
            resource_tenant_id=request.tenant_id,
        )

        return self._approval_engine.approve(
            request=request,
            approved_by=user.user_id,
        )

    def reject(
        self,
        user: User,
        request: ApprovalRequest,
        rejection_reason: str,
    ) -> ApprovalRequest:
        authorize(
            user=user,
            permission=Permission.APPROVE_AI_ACTION,
            resource_tenant_id=request.tenant_id,
        )

        return self._approval_engine.reject(
            request=request,
            rejection_reason=rejection_reason,
        )
