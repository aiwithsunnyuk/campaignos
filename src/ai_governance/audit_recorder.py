from .audit import AuditEvent
from .models import ApprovalRequest


class AuditRecorder:
    """Creates immutable audit events from approval decisions."""

    def record(
        self,
        request: ApprovalRequest,
        event_id: str,
        actor_id: str,
        timestamp: str,
    ) -> AuditEvent:
        if request.status not in {"approved", "rejected"}:
            raise ValueError(
                "Only approved or rejected requests can be audited."
            )

        decision = request.status

        return AuditEvent(
            event_id=event_id,
            request_id=request.request_id,
            tenant_id=request.tenant_id,
            lead_id=request.lead_id,
            event_type=f"approval_{decision}",
            actor_id=actor_id,
            timestamp=timestamp,
            action_type=request.action_type,
            decision=decision,
            recommendation=request.recommendation,
            reason=request.reason,
            evidence=request.evidence,
        )
