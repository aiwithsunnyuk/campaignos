from src.agent.models import (
    AgentAction,
    AgentDecision,
    AgentObservation,
    AgentPlan,
    AgentRequest,
    DecisionStatus,
    ObservationSeverity,
)


def test_agent_request_validates_required_fields():
    request = AgentRequest(
        campaign_id="CMP-001",
        campaign_name="APAC Leadership Campaign",
        business_type="Training & Education",
        region="APAC",
        objective="Increase qualified registrations",
    )

    assert request.validate() == []


def test_agent_request_detects_missing_fields():
    request = AgentRequest(
        campaign_id="",
        campaign_name="",
        business_type="",
        region="",
        objective="",
    )

    errors = request.validate()

    assert len(errors) == 5
    assert "Campaign ID is required." in errors
    assert "Campaign objective is required." in errors


def test_observation_supports_severity_and_evidence():
    observation = AgentObservation(
        observation_id="OBS-001",
        category="Conversion",
        title="Conversion requires review",
        description="Conversion performance is below the selected benchmark.",
        severity=ObservationSeverity.MEDIUM,
        evidence={"conversion_rate": 0.021, "benchmark": 0.034},
    )

    assert observation.validate() == []
    assert observation.severity == ObservationSeverity.MEDIUM
    assert observation.evidence["conversion_rate"] == 0.021


def test_action_validates_priority():
    action = AgentAction(
        action_type="REFINE_AUDIENCE",
        title="Refine APAC audience",
        description="Tighten the audience using lifecycle and engagement signals.",
        priority=1,
    )

    assert action.validate() == []


def test_action_rejects_invalid_priority():
    action = AgentAction(
        action_type="REFINE_AUDIENCE",
        title="Refine audience",
        description="Tighten audience criteria.",
        priority=6,
    )

    assert "Action priority must be between 1 and 5." in action.validate()


def test_decision_validates_confidence():
    action = AgentAction(
        action_type="REVIEW_CONVERSION",
        title="Review conversion",
        description="Investigate conversion performance.",
        priority=2,
    )

    decision = AgentDecision(
        decision_id="DEC-001",
        action=action,
        reason="Conversion is below benchmark.",
        evidence=["Conversion rate is below benchmark."],
        confidence=0.87,
    )

    assert decision.validate() == []
    assert decision.status == DecisionStatus.PROPOSED


def test_decision_rejects_invalid_confidence():
    action = AgentAction(
        action_type="NO_ACTION",
        title="No action",
        description="No material intervention required.",
    )

    decision = AgentDecision(
        decision_id="DEC-002",
        action=action,
        reason="Campaign is performing as expected.",
        confidence=1.2,
    )

    assert "Decision confidence must be between 0 and 1." in decision.validate()


def test_plan_requires_human_approval_by_default():
    action = AgentAction(
        action_type="CREATE_NURTURE",
        title="Create nurture",
        description="Place lower-intent contacts into a nurture path.",
    )

    decision = AgentDecision(
        decision_id="DEC-003",
        action=action,
        reason="Audience requires continued nurturing.",
        confidence=0.78,
    )

    plan = AgentPlan(
        plan_id="PLAN-001",
        campaign_id="CMP-001",
        summary="Recommended campaign optimization plan.",
        decisions=[decision],
    )

    assert plan.validate() == []
    assert plan.action_count == 1
    assert plan.requires_human_approval is True


def test_plan_can_contain_multiple_decisions():
    actions = [
        AgentAction(
            action_type="REFINE_AUDIENCE",
            title="Refine audience",
            description="Tighten audience criteria.",
            priority=1,
        ),
        AgentAction(
            action_type="ADJUST_MESSAGE",
            title="Adjust message",
            description="Improve message-to-CTA alignment.",
            priority=2,
        ),
    ]

    decisions = [
        AgentDecision(
            decision_id=f"DEC-{index}",
            action=action,
            reason="Evidence supports this action.",
            confidence=0.8,
        )
        for index, action in enumerate(actions, start=1)
    ]

    plan = AgentPlan(
        plan_id="PLAN-002",
        campaign_id="CMP-002",
        summary="Two-step optimization plan.",
        decisions=decisions,
    )

    assert plan.validate() == []
    assert plan.action_count == 2
