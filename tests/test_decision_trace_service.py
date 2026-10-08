import pytest

from src.ai_governance import (
    AuditEvent,
    DecisionTraceService,
    GovernedAction,
)
from src.auth.authorization import AuthorizationError
from src.auth.models import Role, User


def make_action() -> GovernedAction:
    return GovernedAction(
        action_id="ACT-REETHA-LEAD-0001",
        tenant_id="reetha",
        lead_id="LEAD-0001",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
    )


def make_event() -> AuditEvent:
    return AuditEvent(
        event_id="AUD-0001",
        request_id="",
        tenant_id="reetha",
        lead_id="LEAD-0001",
        event_type="action_submitted",
        actor_id="reetha-marketing",
        timestamp="2026-10-09T00:00:00+05:30",
        action_type="registration_follow_up",
        decision="pending_approval",
        recommendation="Prioritize registration conversion",
        reason="Governed action lifecycle transition.",
        evidence=("action status: pending_approval",),
    )


def reetha_analyst() -> User:
    return User(
        user_id="reetha-analyst",
        email="analyst@reetha.example",
        display_name="Reetha Analyst",
        tenant_id="reetha",
        role=Role.ANALYST,
    )


def demo_admin() -> User:
    return User(
        user_id="demo-admin",
        email="admin@demo.example",
        display_name="Demo Admin",
        tenant_id="demo",
        role=Role.ADMIN,
    )


def test_reetha_analyst_can_build_reetha_trace():
    action = make_action()
    event = make_event()

    trace = DecisionTraceService().build_trace(
        user=reetha_analyst(),
        action=action,
        events=(event,),
    )

    assert trace.tenant_id == "reetha"
    assert trace.lead_id == "LEAD-0001"
    assert trace.action_id == "ACT-REETHA-LEAD-0001"
    assert trace.events == (event,)


def test_demo_user_cannot_build_reetha_trace():
    action = make_action()
    event = make_event()

    with pytest.raises(
        AuthorizationError,
        match="Tenant access denied",
    ):
        DecisionTraceService().build_trace(
            user=demo_admin(),
            action=action,
            events=(event,),
        )


def test_viewer_without_analytics_cannot_build_trace():
    viewer = User(
        user_id="reetha-viewer",
        email="viewer@reetha.example",
        display_name="Reetha Viewer",
        tenant_id="reetha",
        role=Role.VIEWER,
    )

    with pytest.raises(AuthorizationError):
        DecisionTraceService().build_trace(
            user=viewer,
            action=make_action(),
            events=(make_event(),),
        )


def test_cross_tenant_event_is_rejected():
    event = make_event()

    cross_tenant_action = GovernedAction(
        action_id="ACT-DEMO-LEAD-0001",
        tenant_id="demo",
        lead_id="LEAD-0001",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
    )

    with pytest.raises(
        AuthorizationError,
        match="Tenant access denied",
    ):
        DecisionTraceService().build_trace(
            user=reetha_analyst(),
            action=cross_tenant_action,
            events=(event,),
        )
