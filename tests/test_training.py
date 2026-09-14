from src.training.engine import build_campaign_snapshot, recommend_programs, score_training_intent
from src.training.models import TrainingCampaign, TrainingLeadProfile, TrainingProgram


def sample_programs():
    return [
        TrainingProgram(
            program_id="HAC-001",
            name="Azure Data Engineer",
            category="Data & Cloud",
            audience_tags=("career switcher", "data aspirant"),
            career_paths=("data engineering", "cloud"),
        ),
        TrainingProgram(
            program_id="HAC-003",
            name="Hands-on Python Training",
            category="Development & Data",
            audience_tags=("career switcher", "developer aspirant"),
            career_paths=("Python development", "automation"),
        ),
    ]


def test_intent_score_stage():
    score, stage = score_training_intent(
        {"campaign_engaged": True, "session_registered": True, "session_attended": True}
    )
    assert score == 45
    assert stage.value == "Interested"


def test_high_intent_score():
    score, stage = score_training_intent(
        {"course_viewed": True, "session_attended": True, "counselling_requested": True}
    )
    assert score == 55
    assert stage.value == "Engaged"


def test_enquiry_ready_score():
    score, stage = score_training_intent(
        {"session_attended": True, "counselling_requested": True, "enquiry_submitted": True}
    )
    assert score == 75
    assert stage.value == "High Intent"


def test_recommendations_are_explainable():
    profile = TrainingLeadProfile(
        background="career switcher",
        career_goal="data engineering",
        interest="Azure",
        experience_level="beginner",
    )
    results = recommend_programs(profile, sample_programs())
    assert results
    assert results[0].program_id == "HAC-001"
    assert results[0].reasons


def test_campaign_snapshot():
    campaign = TrainingCampaign(
        campaign_id="CAM-HAC-001",
        campaign_name="Career Switch to Azure Data",
        program_id="HAC-001",
        region="India",
        primary_channel="WhatsApp",
    )
    snapshot = build_campaign_snapshot(
        campaign,
        sample_programs()[0],
        audience_total=1000,
        marketable_total=800,
        mql_total=120,
        high_intent_total=75,
        enquiries_total=25,
    )
    assert snapshot["program"] == "Azure Data Engineer"
    assert snapshot["marketable_rate"] == 0.8
    assert snapshot["enquiry_rate"] == 0.025
