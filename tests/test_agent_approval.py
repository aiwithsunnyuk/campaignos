from src.agent.approval import (
    ApprovalStatus,
    HumanApprovalService,
)
from src.agent.models import (
    AgentAction,
    AgentDecision,
    AgentPlan,
    DecisionStatus,
)


def make_decision(decision_id="DEC-001", priority=2):
    return AgentDecision(
        decision_id=decision_id,
        action=AgentAction(
            action_type="OPTIMIZE_CONVERSION_PATH",
            title="Review conversion path",
            description="Review the conversion path and improve the next step.",
            priority=priority,
            owner="Marketing Operations",
            parameters={"channel": "email"},
        ),
        reason="Conversion is below benchmark.",
        evidence={"conversion_rate": 0.01, "conversion_benchmark": 0.04},
        confidence=0.8,
    )


def make_plan(decisions=None):
    return AgentPlan(
        plan_id="PLAN-CMP-001",
        campaign_id="CMP-001",
        summary="Campaign performance requires optimization.",
        decisions=decisions or [make_decision()],
    )


def test_review_approves_decision_and_creates_audit_record():
    decision, record = HumanApprovalService().review(
        make_decision(),
        approve=True,
        reviewer="Marketing Manager",
        comment="Approved for controlled execution.",
    )

    assert decision.status == DecisionStatus.APPROVED
    assert record.status == ApprovalStatus.APPROVED
    assert record.reviewer == "Marketing Manager"
    assert record.decision_id == "DEC-001"
    assert record.reviewed_at


def test_review_rejects_decision():
    decision, record = HumanApprovalService().review(
        make_decision(),
        approve=False,
        reviewer="Marketing Manager",
        comment="Reject until audience quality is reviewed.",
    )

    assert decision.status == DecisionStatus.REJECTED
    assert record.status == ApprovalStatus.REJECTED


def test_build_action_plan_with_all_approved_decisions_is_execution_ready():
    plan = make_plan()
    approved, _ = HumanApprovalService().review(
        plan.decisions[0],
        approve=True,
        reviewer="Marketing Manager",
    )

    action_plan = HumanApprovalService().build_action_plan(
        plan,
        [approved],
        reviewer="Marketing Manager",
    )

    assert action_plan.status == ApprovalStatus.APPROVED
    assert action_plan.ready_for_execution is True
    assert action_plan.action_count == 1
    assert action_plan.actions[0].decision_id == "DEC-001"
    assert action_plan.source_plan_id == "PLAN-CMP-001"


def test_build_action_plan_with_rejection_is_not_execution_ready():
    plan = make_plan()
    rejected, _ = HumanApprovalService().review(
        plan.decisions[0],
        approve=False,
        reviewer="Marketing Manager",
    )

    action_plan = HumanApprovalService().build_action_plan(
        plan,
        [rejected],
        reviewer="Marketing Manager",
    )

    assert action_plan.status == ApprovalStatus.REJECTED
    assert action_plan.ready_for_execution is False
    assert action_plan.action_count == 0
    assert action_plan.rejected_decision_ids == ["DEC-001"]


def test_mixed_approval_creates_pending_partial_plan():
    decisions = [make_decision("DEC-001"), make_decision("DEC-002", priority=4)]
    plan = make_plan(decisions)

    first, _ = HumanApprovalService().review(
        decisions[0], True, "Marketing Manager"
    )
    second, _ = HumanApprovalService().review(
        decisions[1], False, "Marketing Manager"
    )

    action_plan = HumanApprovalService().build_action_plan(
        plan,
        [first, second],
        reviewer="Marketing Manager",
    )

    assert action_plan.status == ApprovalStatus.PENDING
    assert action_plan.ready_for_execution is False
    assert action_plan.action_count == 1
    assert action_plan.rejected_decision_ids == ["DEC-002"]


def test_build_action_plan_requires_complete_review_set():
    plan = make_plan(
        [make_decision("DEC-001"), make_decision("DEC-002")]
    )

    approved, _ = HumanApprovalService().review(
        plan.decisions[0], True, "Marketing Manager"
    )

    try:
        HumanApprovalService().build_action_plan(
            plan,
            [approved],
            reviewer="Marketing Manager",
        )
    except ValueError as exc:
        assert "exactly match" in str(exc)
    else:
        raise AssertionError("Expected incomplete review set to raise ValueError")


def test_review_requires_reviewer():
    try:
        HumanApprovalService().review(
            make_decision(),
            True,
            "",
        )
    except ValueError as exc:
        assert "reviewer" in str(exc)
    else:
        raise AssertionError("Expected missing reviewer to raise ValueError")


def test_execution_action_copies_parameters_without_external_execution():
    plan = make_plan()
    approved, _ = HumanApprovalService().review(
        plan.decisions[0], True, "Marketing Manager"
    )

    action_plan = HumanApprovalService().build_action_plan(
        plan,
        [approved],
        reviewer="Marketing Manager",
    )

    assert action_plan.actions[0].parameters == {"channel": "email"}
    assert action_plan.actions[0].owner == "Marketing Operations"
