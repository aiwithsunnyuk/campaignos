from src.agent.hardening import (
    approval_count,
    clamp_confidence,
    execution_readiness,
    rejection_count,
)
from src.agent.models import AgentAction, AgentDecision, AgentPlan, DecisionStatus


def make_decision(decision_id="DEC-001", status=DecisionStatus.PROPOSED):
    return AgentDecision(
        decision_id=decision_id,
        action=AgentAction(
            action_type="OPTIMIZE_CONVERSION_PATH",
            title="Review conversion path",
            description="Review the conversion path using supplied campaign evidence.",
            priority=1,
            owner="Marketing Operations",
        ),
        reason="Observed campaign signal requires review.",
        evidence={"conversion_rate": 0.01},
        confidence=0.80,
        status=status,
    )


def make_plan(decisions):
    return AgentPlan(
        plan_id="PLAN-CMP-001",
        campaign_id="CMP-001",
        summary="Synthetic campaign agent plan.",
        decisions=decisions,
    )


def test_confidence_is_clamped_to_supported_range():
    assert clamp_confidence(-0.4) == 0.0
    assert clamp_confidence(0.45) == 0.45
    assert clamp_confidence(1.7) == 1.0


def test_proposed_plan_is_not_execution_ready():
    plan = make_plan([make_decision()])
    assert execution_readiness(plan) is False
    assert approval_count(plan) == 0
    assert rejection_count(plan) == 0


def test_fully_approved_plan_is_execution_ready():
    plan = make_plan([make_decision(status=DecisionStatus.APPROVED)])
    assert execution_readiness(plan) is True
    assert approval_count(plan) == 1
    assert rejection_count(plan) == 0


def test_mixed_approval_state_is_not_execution_ready():
    plan = make_plan([
        make_decision("DEC-001", DecisionStatus.APPROVED),
        make_decision("DEC-002", DecisionStatus.REJECTED),
    ])
    assert execution_readiness(plan) is False
    assert approval_count(plan) == 1
    assert rejection_count(plan) == 1


def test_empty_plan_is_not_execution_ready():
    plan = make_plan([])
    assert execution_readiness(plan) is False
