from src.next_best_action import NextBestAction


def test_next_best_action_model():
    action = NextBestAction(
        lead_id="LEAD-0001",
        tenant_id="reetha",
        action_type="registration_follow_up",
        priority="high",
        recommendation="Prioritize registration conversion",
        reason="Lead is highly engaged but has not registered.",
        evidence=(
            "high engagement intensity",
            "not registered",
            "registration is the current funnel bottleneck",
        ),
    )

    assert action.lead_id == "LEAD-0001"
    assert action.tenant_id == "reetha"
    assert action.action_type == "registration_follow_up"
    assert action.priority == "high"
    assert len(action.evidence) == 3


def test_next_best_action_engine_prioritizes_registration():
    from src.gtm_intelligence.signals import GTMExplainableSignal
    from src.next_best_action import NextBestActionEngine

    signals = [
        GTMExplainableSignal(
            signal_id="ENGAGEMENT_COVERAGE",
            name="Engagement Coverage",
            category="engagement",
            level="strong",
            value="strong",
            evidence=("249 of 250 leads engaged",),
        ),
        GTMExplainableSignal(
            signal_id="FUNNEL_BOTTLENECK",
            name="Funnel Bottleneck",
            category="funnel",
            level="moderate",
            value="registration",
            evidence=("Engaged to registered conversion is weakest",),
        ),
    ]

    action = NextBestActionEngine().recommend(
        lead_id="LEAD-0001",
        tenant_id="reetha",
        signals=signals,
    )

    assert action.action_type == "registration_follow_up"
    assert action.priority == "high"
    assert action.recommendation == "Prioritize registration conversion"
    assert "registration is the current funnel bottleneck" in action.evidence
