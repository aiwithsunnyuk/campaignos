from src.agent.models import AgentRequest
from src.agent.orchestrator import CampaignAgentOrchestrator


def make_request() -> AgentRequest:
    return AgentRequest(
        campaign_id="CMP-001",
        campaign_name="APAC Product Launch",
        business_type="Professional Information",
        region="APAC",
        objective="Generate qualified leads",
        context={},
    )


def test_orchestrator_builds_plan_from_analysis_and_decisions():
    plan = CampaignAgentOrchestrator().run(
        make_request(),
        {"conversion_rate": 0.015, "conversion_benchmark": 0.04, "open_rate": 0.20},
    )

    assert plan.plan_id == "PLAN-CMP-001"
    assert plan.campaign_id == "CMP-001"
    assert plan.generated_by == "CampaignOS Agent"
    assert plan.requires_human_approval is True
    assert plan.action_count >= 1


def test_orchestrator_preserves_explainability_chain():
    plan = CampaignAgentOrchestrator().run(
        make_request(),
        {"conversion_rate": 0.01, "conversion_benchmark": 0.04},
    )

    decision = plan.decisions[0]

    assert decision.decision_id == "DEC-001"
    assert decision.reason
    assert decision.evidence["conversion_rate"] == 0.01
    assert decision.evidence["benchmark"] == 0.04
    assert decision.evidence["gap"] == 0.03
    assert decision.action.action_type == "OPTIMIZE_CONVERSION_PATH"
    assert 0 <= decision.confidence <= 1


def test_orchestrator_retains_positive_info_decision_when_performance_meets_benchmark():
    plan = CampaignAgentOrchestrator().run(
        make_request(),
        {"conversion_rate": 0.05, "conversion_benchmark": 0.04},
    )

    assert len(plan.decisions) == 1
    assert plan.action_count == 1
    assert plan.decisions[0].action.action_type == "OPTIMIZE_CONVERSION_PATH"
    assert plan.decisions[0].confidence == 0.70
    assert "One actionable decision" in plan.summary


def test_orchestrator_passes_campaign_id_to_analyzer():
    class RecordingAnalyzer:
        def __init__(self):
            self.campaign_id = None
            self.context = None

        def analyze(self, campaign_id, context):
            self.campaign_id = campaign_id
            self.context = context
            return []

    analyzer = RecordingAnalyzer()
    context = {"conversion_rate": 0.05, "conversion_benchmark": 0.04}

    plan = CampaignAgentOrchestrator(analyzer=analyzer).run(
        make_request(),
        context,
    )

    assert analyzer.campaign_id == "CMP-001"
    assert analyzer.context == context
    assert plan.action_count == 0
    assert "No actionable decisions" in plan.summary


def test_orchestrator_accepts_multiple_signal_types():
    plan = CampaignAgentOrchestrator().run(
        make_request(),
        {
            "conversion_rate": 0.01,
            "conversion_benchmark": 0.04,
            "open_rate": 0.18,
            "click_rate": 0.03,
            "average_lead_score": 84,
        },
    )

    action_types = {d.action.action_type for d in plan.decisions}

    assert "OPTIMIZE_CONVERSION_PATH" in action_types
    assert "OPTIMIZE_EMAIL_ENGAGEMENT" in action_types
    assert "OPTIMIZE_CTA" in action_types
    assert "PRIORITIZE_HIGH_INTENT_LEADS" in action_types


def test_orchestrator_does_not_execute_actions():
    plan = CampaignAgentOrchestrator().run(
        make_request(),
        {"conversion_rate": 0.01, "conversion_benchmark": 0.04},
    )

    for decision in plan.decisions:
        assert decision.status.name == "PROPOSED"
