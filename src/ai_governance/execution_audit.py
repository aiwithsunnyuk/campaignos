from src.execution.models import ExecutionResult

from .action_lifecycle import GovernedAction
from .audit import AuditEvent


class ExecutionAuditRecorder:
    """Creates audit events from governed execution results."""

    def record(
        self,
        action: GovernedAction,
        result: ExecutionResult,
        event_id: str,
        actor_id: str,
        timestamp: str,
    ) -> AuditEvent:
        if result.action_id != action.action_id:
            raise ValueError(
                "Execution result action does not match governed action."
            )

        if result.tenant_id != action.tenant_id:
            raise ValueError(
                "Execution result tenant does not match governed action."
            )

        return AuditEvent(
            event_id=event_id,
            request_id="",
            tenant_id=action.tenant_id,
            lead_id=action.lead_id,
            event_type=f"{result.status}_completed",
            actor_id=actor_id,
            timestamp=timestamp,
            action_type=result.action_type,
            decision=result.status,
            recommendation=action.recommendation,
            reason="Governed execution boundary result.",
            evidence=(
                f"execution id: {result.execution_id}",
                f"execution status: {result.status}",
                result.message,
            ),
        )
