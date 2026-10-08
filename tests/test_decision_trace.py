import pytest

from src.ai_governance.audit import AuditEvent
from src.ai_governance.decision_trace import DecisionTrace


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


def test_decision_trace_preserves_governed_action_context():
    event = make_event()

    trace = DecisionTrace(
        tenant_id="reetha",
        lead_id="LEAD-0001",
        action_id="ACT-REETHA-LEAD-0001",
        events=(event,),
    )

    assert trace.tenant_id == "reetha"
    assert trace.lead_id == "LEAD-0001"
    assert trace.action_id == "ACT-REETHA-LEAD-0001"
    assert trace.events == (event,)


def test_decision_trace_rejects_cross_tenant_event():
    event = make_event(tenant_id="demo")

    with pytest.raises(
        ValueError,
        match="Audit event tenant does not match",
    ):
        DecisionTrace(
            tenant_id="reetha",
            lead_id="LEAD-0001",
            action_id="ACT-REETHA-LEAD-0001",
            events=(event,),
        )


def test_decision_trace_rejects_cross_lead_event():
    event = make_event(lead_id="LEAD-0002")

    with pytest.raises(
        ValueError,
        match="Audit event lead does not match",
    ):
        DecisionTrace(
            tenant_id="reetha",
            lead_id="LEAD-0001",
            action_id="ACT-REETHA-LEAD-0001",
            events=(event,),
        )
