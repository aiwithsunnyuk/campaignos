import pytest

from src.ai_governance import (
    ActionLifecycleEngine,
    GovernedAction,
)
from src.execution import (
    DryRunExecutionAdapter,
    ExecutionBoundaryError,
)


def make_ready_action():
    action = GovernedAction(
        action_id="ACT-0200",
        tenant_id="reetha",
        lead_id="LEAD-0200",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
    )

    engine = ActionLifecycleEngine()

    pending = engine.submit_for_approval(action)

    approved = engine.approve(
        pending,
        approved_by="reetha-director",
    )

    return engine.mark_ready_for_execution(approved)


def test_ready_action_can_enter_dry_run():
    action = make_ready_action()

    result = DryRunExecutionAdapter().execute(
        action=action,
        execution_id="EXE-0200",
    )

    assert result.execution_id == "EXE-0200"
    assert result.action_id == "ACT-0200"
    assert result.tenant_id == "reetha"
    assert result.status == "dry_run"
    assert result.action_type == "registration_follow_up"
    assert "No external system was contacted." in result.message


def test_approved_action_cannot_bypass_execution_readiness():
    action = GovernedAction(
        action_id="ACT-0201",
        tenant_id="reetha",
        lead_id="LEAD-0201",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        status="approved",
        approved_by="reetha-director",
    )

    with pytest.raises(ExecutionBoundaryError):
        DryRunExecutionAdapter().execute(
            action=action,
            execution_id="EXE-0201",
        )


def test_pending_action_cannot_execute():
    action = GovernedAction(
        action_id="ACT-0202",
        tenant_id="reetha",
        lead_id="LEAD-0202",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        status="pending_approval",
    )

    with pytest.raises(ExecutionBoundaryError):
        DryRunExecutionAdapter().execute(
            action=action,
            execution_id="EXE-0202",
        )


def test_dry_run_preserves_tenant_identity():
    action = make_ready_action()

    result = DryRunExecutionAdapter().execute(
        action=action,
        execution_id="EXE-0203",
    )

    assert result.tenant_id == action.tenant_id
    assert result.tenant_id == "reetha"
    assert result.action_id == action.action_id
