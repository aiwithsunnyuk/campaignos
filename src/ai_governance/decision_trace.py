from dataclasses import dataclass

from .audit import AuditEvent


@dataclass(frozen=True)
class DecisionTrace:
    """Immutable chronological trace for a governed lead action."""

    tenant_id: str
    lead_id: str
    action_id: str
    events: tuple[AuditEvent, ...]

    def __post_init__(self) -> None:
        for event in self.events:
            if event.tenant_id != self.tenant_id:
                raise ValueError(
                    "Audit event tenant does not match decision trace tenant."
                )

            if event.lead_id != self.lead_id:
                raise ValueError(
                    "Audit event lead does not match decision trace lead."
                )
