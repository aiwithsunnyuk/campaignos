import pytest

from src.ai_governance import (
    ActionLifecycleEngine,
    ActionLifecycleError,
    GovernedAction,
)


def make_action():
    return GovernedAction(
        action_id="ACT-0001",
        tenant_id="reetha",
        lead_id="LEAD-0001",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
    )


def test_action_starts_as_recommended():
    action = make_action()

    assert action.status == "recommended"


def test_recommended_action_can_be_submitted_for_approval():
    action = make_action()

    pending = ActionLifecycleEngine().submit_for_approval(action)

    assert action.status == "recommended"
    assert pending.status == "pending_approval"


def test_pending_action_can_be_approved():
    action = make_action()
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(action)
    approved = engine.approve(
        pending,
        approved_by="reetha-director",
    )

    assert approved.status == "approved"
    assert approved.approved_by == "reetha-director"


def test_pending_action_can_be_rejected():
    action = make_action()
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(action)
    rejected = engine.reject(pending)

    assert rejected.status == "rejected"


def test_approved_action_becomes_ready_for_execution():
    action = make_action()
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(action)
    approved = engine.approve(
        pending,
        approved_by="reetha-director",
    )
    ready = engine.mark_ready_for_execution(approved)

    assert ready.status == "ready_for_execution"


def test_ready_action_can_be_marked_executed():
    action = make_action()
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(action)
    approved = engine.approve(
        pending,
        approved_by="reetha-director",
    )
    ready = engine.mark_ready_for_execution(approved)
    executed = engine.mark_executed(
        ready,
        executed_by="campaignos-system",
    )

    assert executed.status == "executed"
    assert executed.executed_by == "campaignos-system"


def test_approved_does_not_mean_executed():
    action = make_action()
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(action)
    approved = engine.approve(
        pending,
        approved_by="reetha-director",
    )

    assert approved.status == "approved"
    assert approved.executed_by is None


def test_rejected_action_cannot_execute():
    action = make_action()
    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(action)
    rejected = engine.reject(pending)

    with pytest.raises(ActionLifecycleError):
        engine.mark_executed(
            rejected,
            executed_by="campaignos-system",
        )
