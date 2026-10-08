from .action_lifecycle import GovernedAction
from .audit import AuditEvent
from .decision_trace import DecisionTrace


class DecisionTraceRecorder:
    """Builds an immutable decision trace for a governed action."""

    def record(
        self,
        action: GovernedAction,
        events: tuple[AuditEvent, ...],
    ) -> DecisionTrace:
        for event in events:
            if event.tenant_id != action.tenant_id:
                raise ValueError(
                    "Audit event tenant does not match governed action tenant."
                )

            if event.lead_id != action.lead_id:
                raise ValueError(
                    "Audit event lead does not match governed action lead."
                )

        return DecisionTrace(
            tenant_id=action.tenant_id,
            lead_id=action.lead_id,
            action_id=action.action_id,
            events=events,
        )
