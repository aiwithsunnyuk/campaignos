from src.auth.authorization import authorize
from src.auth.models import Permission, User

from .audit import AuditEvent
from .audit_recorder import AuditRecorder
from .models import ApprovalRequest


class TenantAuditService:
    """Creates audit events only within an authorized tenant boundary."""

    def __init__(self) -> None:
        self._recorder = AuditRecorder()

    def record(
        self,
        user: User,
        request: ApprovalRequest,
        event_id: str,
        timestamp: str,
    ) -> AuditEvent:
        authorize(
            user=user,
            permission=Permission.APPROVE_AI_ACTION,
            resource_tenant_id=request.tenant_id,
        )

        return self._recorder.record(
            request=request,
            event_id=event_id,
            actor_id=user.user_id,
            timestamp=timestamp,
        )
