from src.agent.decision_engine import CampaignDecisionEngine
from src.agent.models import AgentObservation, ObservationSeverity


def make_observation(category, title, description, severity, evidence=None):
    return AgentObservation(
        observation_id="OBS-001",
        category=category,
        title=title,
        description=description,
        severity=severity,
        evidence=evidence or {},
    )


def test_high_conversion_issue_creates_high_priority_conversion_action():
    engine = CampaignDecisionEngine()
    observations = [
        make_observation(
            "conversion",
            "Conversion is materially below benchmark",
            "Conversion rate is 1.5% against a 4.0% benchmark.",
            ObservationSeverity.HIGH,
            {"conversion_rate": 0.015, "benchmark": 0.04},
        )
    ]
    decisions = engine.decide(observations)
    assert len(decisions) == 1
    assert decisions[0].decision_id == "DEC-001"
    assert decisions[0].action.action_type == "OPTIMIZE_CONVERSION_PATH"
    assert decisions[0].action.priority == 1
    assert decisions[0].confidence == 0.92


def test_low_open_rate_creates_email_engagement_action():
    decisions = CampaignDecisionEngine().decide([
        make_observation("email", "Open rate is below expected range", "Open rate is 18%.", ObservationSeverity.MEDIUM)
    ])
    assert decisions[0].action.action_type == "OPTIMIZE_EMAIL_ENGAGEMENT"
    assert decisions[0].action.parameters["focus"] == "open_rate"
    assert decisions[0].action.priority == 2


def test_low_click_rate_creates_cta_action():
    decisions = CampaignDecisionEngine().decide([
        make_observation("engagement", "Click rate is below expected range", "Click rate is 3%.", ObservationSeverity.MEDIUM)
    ])
    assert decisions[0].action.action_type == "OPTIMIZE_CTA"


def test_low_marketable_ratio_creates_audience_action():
    decisions = CampaignDecisionEngine().decide([
        make_observation("audience", "MQL coverage is low", "MQLs represent a small share of the marketable audience.", ObservationSeverity.MEDIUM)
    ])
    assert decisions[0].action.action_type == "REFINE_AUDIENCE"


def test_high_lead_score_creates_lead_prioritization_action():
    decisions = CampaignDecisionEngine().decide([
        make_observation("lead score", "Strong intent signal detected", "Average lead score is 84.", ObservationSeverity.LOW)
    ])
    assert decisions[0].action.action_type == "PRIORITIZE_HIGH_INTENT_LEADS"
    assert decisions[0].action.priority == 3


def test_multiple_observations_produce_multiple_decisions():
    observations = [
        make_observation("conversion", "Conversion is below benchmark", "Conversion is 2%.", ObservationSeverity.MEDIUM),
        make_observation("email", "Open rate is below expected range", "Open rate is 20%.", ObservationSeverity.MEDIUM),
    ]
    decisions = CampaignDecisionEngine().decide(observations)
    assert len(decisions) == 2
    assert [d.decision_id for d in decisions] == ["DEC-001", "DEC-002"]


def test_unrecognized_observation_does_not_create_unsupported_action():
    observations = [
        make_observation("general", "No material issue detected", "The supplied signals do not indicate a material issue.", ObservationSeverity.INFO)
    ]
    assert CampaignDecisionEngine().decide(observations) == []


def test_decision_preserves_observation_evidence():
    evidence = {"conversion_rate": 0.02, "benchmark": 0.04}
    decisions = CampaignDecisionEngine().decide([
        make_observation("conversion", "Conversion is below benchmark", "Conversion is below benchmark.", ObservationSeverity.MEDIUM, evidence)
    ])
    assert decisions[0].evidence == evidence
    assert decisions[0].reason == "Conversion is below benchmark."


def test_confidence_is_bounded():
    engine = CampaignDecisionEngine()
    for severity in ObservationSeverity:
        decisions = engine.decide([
            make_observation("conversion", "Conversion issue", "Test observation.", severity)
        ])
        assert len(decisions) == 1
        assert 0.0 <= decisions[0].confidence <= 1.0
