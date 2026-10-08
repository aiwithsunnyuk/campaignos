import pytest

from src.ai_governance.action_lifecycle import GovernedAction
from src.ai_governance.execution_audit import ExecutionAuditRecorder
from src.execution.models import ExecutionResult


def make_action() -> GovernedAction:
    return GovernedAction(
        action_id="ACT-REETHA-LEAD-0001",
        tenant_id="reetha",
        lead_id="LEAD-0001",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        status="ready_for_execution",
    )


def make_result(
    action_id: str = "ACT-REETHA-LEAD-0001",
    tenant_id: str = "reetha",
) -> ExecutionResult:
    return ExecutionResult(
        execution_id="EXEC-REETHA-0001",
        action_id=action_id,
        tenant_id=tenant_id,
        status="dry_run",
        action_type="registration_follow_up",
        message="Dry-run only. No external system was contacted.",
    )


def test_dry_run_result_creates_execution_audit_event():
    action = make_action()
    result = make_result()

    event = ExecutionAuditRecorder().record(
        action=action,
        result=result,
        event_id="AUD-EXEC-0001",
        actor_id="reetha-director",
        timestamp="2026-10-09T00:03:00+05:30",
    )

    assert event.event_id == "AUD-EXEC-0001"
    assert event.event_type == "dry_run_completed"
    assert event.tenant_id == "reetha"
    assert event.lead_id == "LEAD-0001"
    assert event.actor_id == "reetha-director"
    assert event.decision == "dry_run"
    assert event.action_type == "registration_follow_up"
    assert any(
        "EXEC-REETHA-0001" in evidence
        for evidence in event.evidence
    )
    assert any(
        "No external system was contacted" in evidence
        for evidence in event.evidence
    )


def test_execution_result_for_different_action_is_rejected():
    action = make_action()
    result = make_result(
        action_id="ACT-REETHA-LEAD-0002",
    )

    with pytest.raises(
        ValueError,
        match="Execution result action does not match",
    ):
        ExecutionAuditRecorder().record(
            action=action,
            result=result,
            event_id="AUD-EXEC-0002",
            actor_id="reetha-director",
            timestamp="2026-10-09T00:03:00+05:30",
        )


def test_execution_result_for_different_tenant_is_rejected():
    action = make_action()
    result = make_result(
        tenant_id="demo",
    )

    with pytest.raises(
        ValueError,
        match="Execution result tenant does not match",
    ):
        ExecutionAuditRecorder().record(
            action=action,
            result=result,
            event_id="AUD-EXEC-0003",
            actor_id="reetha-director",
            timestamp="2026-10-09T00:03:00+05:30",
        )
