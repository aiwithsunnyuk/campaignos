import pandas as pd

from src.agent.campaign_context import build_campaign_context


def make_campaign():
    return pd.Series(
        {
            "campaign_id": "CMP-001",
            "campaign_name": "Test Campaign",
            "region": "APAC",
        }
    )


def test_campaign_context_calculates_funnel_rates():
    activities = pd.DataFrame(
        [
            {"campaign_id": "CMP-001", "activity_type": "Sent"},
            {"campaign_id": "CMP-001", "activity_type": "Sent"},
            {"campaign_id": "CMP-001", "activity_type": "Opened"},
            {"campaign_id": "CMP-001", "activity_type": "Clicked"},
            {"campaign_id": "CMP-001", "activity_type": "Submitted"},
        ]
    )
    contacts = pd.DataFrame(
        [
            {
                "region": "APAC",
                "consent_status": "Opted In",
                "lifecycle_stage": "MQL",
                "lead_score": 80,
            },
            {
                "region": "APAC",
                "consent_status": "Not Subscribed",
                "lifecycle_stage": "Known",
                "lead_score": 60,
            },
        ]
    )

    context = build_campaign_context(make_campaign(), contacts, activities)

    assert context["sent"] == 2
    assert context["opened"] == 1
    assert context["clicked"] == 1
    assert context["converted"] == 1
    assert context["open_rate"] == 0.5
    assert context["click_rate"] == 0.5
    assert context["conversion_rate"] == 0.5
    assert context["marketable_contacts"] == 1
    assert context["mql_count"] == 1
    assert context["average_lead_score"] == 70


def test_campaign_context_is_scoped_to_selected_campaign_and_region():
    activities = pd.DataFrame(
        [
            {"campaign_id": "CMP-001", "activity_type": "Sent"},
            {"campaign_id": "CMP-002", "activity_type": "Sent"},
        ]
    )
    contacts = pd.DataFrame(
        [
            {
                "region": "APAC",
                "consent_status": "Opted In",
                "lifecycle_stage": "MQL",
                "lead_score": 90,
            },
            {
                "region": "Europe",
                "consent_status": "Opted In",
                "lifecycle_stage": "MQL",
                "lead_score": 10,
            },
        ]
    )

    context = build_campaign_context(make_campaign(), contacts, activities)

    assert context["sent"] == 1
    assert context["marketable_contacts"] == 1
    assert context["mql_count"] == 1
    assert context["average_lead_score"] == 90


def test_campaign_context_handles_zero_activity():
    activities = pd.DataFrame(
        columns=["campaign_id", "activity_type"]
    )
    contacts = pd.DataFrame(
        [
            {
                "region": "APAC",
                "consent_status": "Opted In",
                "lifecycle_stage": "Known",
                "lead_score": 50,
            }
        ]
    )

    context = build_campaign_context(make_campaign(), contacts, activities)

    assert context["sent"] == 0
    assert context["open_rate"] == 0.0
    assert context["click_rate"] == 0.0
    assert context["conversion_rate"] == 0.0
