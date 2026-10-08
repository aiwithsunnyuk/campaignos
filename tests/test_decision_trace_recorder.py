import pytest

from src.ai_governance.action_lifecycle import GovernedAction
from src.ai_governance.audit import AuditEvent
from src.ai_governance.decision_trace_recorder import DecisionTraceRecorder


def make_action() -> GovernedAction:
    return GovernedAction(
        action_id="ACT-REETHA-LEAD-0001",
        tenant_id="reetha",
        lead_id="LEAD-0001",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
    )


def make_event(
    event_id: str = "AUD-0001",
    tenant_id: str = "reetha",
    lead_id: str = "LEAD-0001",
) -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        request_id="APR-0001",
        tenant_id=tenant_id,
        lead_id=lead_id,
        event_type="approval_approved",
        actor_id="reetha-director",
        timestamp="2026-10-09T00:00:00+05:30",
        action_type="registration_follow_up",
        decision="approved",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=("registration bottleneck",),
    )


def test_recorder_builds_trace_for_governed_action():
    action = make_action()
    event = make_event()

    trace = DecisionTraceRecorder().record(
        action=action,
        events=(event,),
    )

    assert trace.action_id == action.action_id
    assert trace.tenant_id == action.tenant_id
    assert trace.lead_id == action.lead_id
    assert trace.events == (event,)


def test_recorder_rejects_cross_tenant_event():
    action = make_action()
    event = make_event(tenant_id="demo")

    with pytest.raises(
        ValueError,
        match="Audit event tenant does not match governed action tenant",
    ):
        DecisionTraceRecorder().record(
            action=action,
            events=(event,),
        )


def test_recorder_rejects_cross_lead_event():
    action = make_action()
    event = make_event(lead_id="LEAD-0002")

    with pytest.raises(
        ValueError,
        match="Audit event lead does not match governed action lead",
    ):
        DecisionTraceRecorder().record(
            action=action,
            events=(event,),
        )
