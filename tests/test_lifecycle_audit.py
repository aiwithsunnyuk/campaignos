from src.ai_governance import ActionLifecycleEngine, GovernedAction
from src.ai_governance.lifecycle_audit import LifecycleAuditRecorder


def make_action() -> GovernedAction:
    return GovernedAction(
        action_id="ACT-REETHA-LEAD-0001",
        tenant_id="reetha",
        lead_id="LEAD-0001",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
    )


def test_pending_action_creates_submission_audit_event():
    engine = ActionLifecycleEngine()

    action = engine.submit_for_approval(make_action())

    event = LifecycleAuditRecorder().record(
        action=action,
        event_id="AUD-SUBMIT-0001",
        actor_id="reetha-marketing",
        timestamp="2026-10-09T00:00:00+05:30",
    )

    assert event.event_id == "AUD-SUBMIT-0001"
    assert event.event_type == "action_submitted"
    assert event.tenant_id == "reetha"
    assert event.lead_id == "LEAD-0001"
    assert event.actor_id == "reetha-marketing"
    assert event.decision == "pending_approval"
    assert any(
        "ACT-REETHA-LEAD-0001" in evidence
        for evidence in event.evidence
    )


def test_approved_action_creates_approval_audit_event():
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(make_action())
    approved = engine.approve(
        pending,
        approved_by="reetha-director",
    )

    event = LifecycleAuditRecorder().record(
        action=approved,
        event_id="AUD-APPROVE-0001",
        actor_id="reetha-director",
        timestamp="2026-10-09T00:01:00+05:30",
    )

    assert event.event_type == "action_approved"
    assert event.actor_id == "reetha-director"
    assert event.decision == "approved"


def test_ready_action_creates_execution_ready_event():
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(make_action())
    approved = engine.approve(
        pending,
        approved_by="reetha-director",
    )
    ready = engine.mark_ready_for_execution(approved)

    event = LifecycleAuditRecorder().record(
        action=ready,
        event_id="AUD-READY-0001",
        actor_id="reetha-director",
        timestamp="2026-10-09T00:02:00+05:30",
    )

    assert event.event_type == "execution_ready"
    assert event.decision == "ready_for_execution"
