from src.reetha_campaign_planner import build_campaign_plans, _normalise_domain


def test_normalise_domain_handles_common_sap_variants():
    assert _normalise_domain("FICO") == "SAP Finance / FICO"
    assert _normalise_domain("SAP MM") == "SAP Procurement / MM"
    assert _normalise_domain("SAP BTP") == "SAP BTP / Cloud"


def test_build_campaign_plans_returns_approval_ready_plans():
    plans = build_campaign_plans(max_plans=10)
    assert plans
    plan = plans[0]
    assert plan.campaign_name
    assert plan.objective
    assert plan.audience_size >= 1
    assert plan.primary_offering
    assert plan.secondary_offering
    assert plan.channels
    assert plan.cta


def test_campaign_plans_are_ranked_by_explainable_score():
    plans = build_campaign_plans(max_plans=10)
    scores = [p.engagement_rate * 0.55 + p.registration_gap_rate * 0.45 for p in plans]
    assert scores == sorted(scores, reverse=True)


def test_campaign_planner_reads_m13_4_1_normalized_audience_contract():
    plans = build_campaign_plans(max_plans=10)
    assert plans
    assert all(p.audience_size > 0 for p in plans)
