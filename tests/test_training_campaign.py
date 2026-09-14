from datetime import date

import pytest

from src.training.campaign_builder import (
    CAMPAIGN_TYPES,
    CHANNELS,
    OBJECTIVES,
    build_training_campaign,
    campaign_brief,
    execution_plan,
    render_training_message,
)
from src.training.models import TrainingProgram


def sample_program() -> TrainingProgram:
    return TrainingProgram(
        program_id="HAC-ADE",
        name="Azure Data Engineer",
        category="Data",
        career_paths=["DATA_SWITCHER"],
        audience_tags=["azure", "data", "cloud"],
        delivery_mode="Verify with client",
    )


def sample_campaign():
    return build_training_campaign(
        campaign_id="M11-6-001",
        program=sample_program(),
        region="India",
        session_label="Live Session Promotion",
        objective="Course Interest",
        audience="Career switchers interested in data and cloud",
        career_persona="DATA_SWITCHER",
        session_date="2026-09-15",
        session_time="06:30",
        channel="WhatsApp Community",
        secondary_channel="Email",
        cta="Join the introductory training session",
    )


def test_campaign_builds_and_validates():
    campaign = sample_campaign()

    assert campaign.program_id == "HAC-ADE"
    assert campaign.program_name == "Azure Data Engineer"
    assert campaign.region == "India"
    assert campaign.session_date == "2026-09-15"
    assert campaign.session_time == "06:30"


def test_campaign_brief_is_deterministic():
    brief = campaign_brief(sample_campaign())

    assert brief.program_name == "Azure Data Engineer"
    assert brief.region == "India"
    assert brief.primary_channel == "WhatsApp Community"
    assert brief.secondary_channel == "Email"


def test_execution_plan_has_six_areas():
    plan = execution_plan(sample_campaign())

    assert len(plan) == 6
    assert [item["area"] for item in plan] == [
        "Audience",
        "Message",
        "Channel",
        "CTA",
        "Follow-up",
        "Measurement",
    ]
    assert "Azure Data Engineer" in plan[1]["action"]


def test_message_contains_no_real_credentials():
    message = render_training_message(
        sample_campaign(),
        contact_name="there",
        join_details="Synthetic session details",
    )

    assert "Synthetic session details" in message
    assert "Azure Data Engineer" in message
    assert "India" in message
    assert "06:30" in message
    assert "password" not in message.lower()
    assert "passcode" not in message.lower()


def test_invalid_required_field_is_rejected():
    with pytest.raises(ValueError, match="session_label is required"):
        build_training_campaign(
            campaign_id="M11-6-002",
            program=sample_program(),
            region="India",
            session_label="",
        )


def test_invalid_controlled_values_are_rejected():
    with pytest.raises(ValueError, match="Unsupported primary channel"):
        build_training_campaign(
            campaign_id="M11-6-003",
            program=sample_program(),
            region="India",
            session_label="Test Session",
            channel="Unknown Channel",
        )

    with pytest.raises(ValueError, match="Unsupported objective"):
        build_training_campaign(
            campaign_id="M11-6-004",
            program=sample_program(),
            region="India",
            session_label="Test Session",
            objective="Unknown Objective",
        )
