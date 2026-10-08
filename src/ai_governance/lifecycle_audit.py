from .action_lifecycle import GovernedAction
from .audit import AuditEvent


class LifecycleAuditRecorder:
    """Creates immutable audit events for governed-action lifecycle states."""

    def record(
        self,
        action: GovernedAction,
        event_id: str,
        actor_id: str,
        timestamp: str,
    ) -> AuditEvent:
        event_type_by_status = {
            "recommended": "action_recommended",
            "pending_approval": "action_submitted",
            "approved": "action_approved",
            "rejected": "action_rejected",
            "ready_for_execution": "execution_ready",
            "executed": "action_executed",
        }

        event_type = event_type_by_status.get(action.status)

        if event_type is None:
            raise ValueError(
                f"Unsupported governed action status: {action.status}"
            )

        decision = action.status

        return AuditEvent(
            event_id=event_id,
            request_id="",
            tenant_id=action.tenant_id,
            lead_id=action.lead_id,
            event_type=event_type,
            actor_id=actor_id,
            timestamp=timestamp,
            action_type=action.action_type,
            decision=decision,
            recommendation=action.recommendation,
            reason="Governed action lifecycle transition.",
            evidence=(
                f"action status: {action.status}",
                f"action id: {action.action_id}",
            ),
        )
