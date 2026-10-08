from src.auth.authorization import authorize
from src.auth.models import Permission, User

from .action_lifecycle import GovernedAction
from .audit import AuditEvent
from .decision_trace import DecisionTrace
from .decision_trace_recorder import DecisionTraceRecorder


class DecisionTraceService:
    """Tenant-safe service for retrieving a governed action decision trace."""

    def __init__(self) -> None:
        self._recorder = DecisionTraceRecorder()

    def build_trace(
        self,
        user: User,
        action: GovernedAction,
        events: tuple[AuditEvent, ...],
    ) -> DecisionTrace:
        authorize(
            user=user,
            permission=Permission.VIEW_ANALYTICS,
            resource_tenant_id=action.tenant_id,
        )

        if action.tenant_id != user.tenant_id:
            raise ValueError(
                "Action tenant does not match the authorized user tenant."
            )

        return self._recorder.record(
            action=action,
            events=events,
        )
