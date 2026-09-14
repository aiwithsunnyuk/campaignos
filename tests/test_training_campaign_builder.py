from src.training.campaign_builder import build_training_campaign, campaign_to_dict, render_training_message
from src.training.models import TrainingProgram


def sample_program():
    return TrainingProgram(
        program_id="P-001", name="AI/ML with Gen AI", category="AI",
        audience_tags=("career switcher", "IT professional"),
        career_paths=("AI", "data analytics"),
    )


def test_build_training_campaign():
    campaign = build_training_campaign(
        campaign_id="M11-001", program=sample_program(), region="India",
        session_label="14 Sep 2026 • 6:30 AM • 60 minutes",
    )
    assert campaign.status == "Draft"
    assert campaign.primary_channel == "WhatsApp"
    assert campaign.program_id == "P-001"


def test_campaign_requires_session():
    try:
        build_training_campaign(campaign_id="M11-001", program=sample_program(), region="India", session_label="")
    except ValueError as exc:
        assert "session_label" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_message_preview_is_synthetic_safe():
    campaign = build_training_campaign(
        campaign_id="M11-001", program=sample_program(), region="India",
        session_label="14 Sep 2026 • 6:30 AM • 60 minutes",
    )
    message = render_training_message(campaign, sample_program())
    assert "AI/ML with Gen AI" in message
    assert "Synthetic session details" in message
    assert "password" not in message.lower()


def test_campaign_serializes():
    campaign = build_training_campaign(
        campaign_id="M11-001", program=sample_program(), region="India",
        session_label="14 Sep 2026 • 6:30 AM • 60 minutes",
    )
    payload = campaign_to_dict(campaign)
    assert payload["campaign_id"] == "M11-001"
    assert payload["region"] == "India"
