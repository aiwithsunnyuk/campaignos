from dataclasses import dataclass


AuditEventType = str


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    request_id: str
    tenant_id: str
    lead_id: str
    event_type: AuditEventType
    actor_id: str
    timestamp: str
    action_type: str
    decision: str
    recommendation: str
    reason: str
    evidence: tuple[str, ...]
