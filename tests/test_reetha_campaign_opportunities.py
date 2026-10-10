import pandas as pd

from src.reetha_campaign_opportunities import build_campaign_opportunities


def test_build_campaign_opportunities_creates_explainable_opportunity():
    leads = pd.DataFrame([
        {"lead_id": "L1", "interest": "SAP BTP", "course_id": "C1"},
        {"lead_id": "L2", "interest": "SAP BTP", "course_id": "C1"},
        {"lead_id": "L3", "interest": "SAP BTP", "course_id": "C1"},
    ])
    courses = pd.DataFrame([
        {"course_id": "C1", "name": "SAP BTP Practice"}
    ])
    engagements = pd.DataFrame([
        {"lead_id": "L1"},
        {"lead_id": "L2"},
    ])
    campaigns = pd.DataFrame()
    registrations = pd.DataFrame([
        {"lead_id": "L1"}
    ])
    enrollments = pd.DataFrame([
        {"lead_id": "L1"}
    ])

    result = build_campaign_opportunities(
        leads,
        courses,
        engagements,
        campaigns,
        registrations,
        enrollments,
    )

    assert len(result) == 1
    assert result.iloc[0]["demand_signal"] == "SAP BTP"
    assert result.iloc[0]["interested_leads"] == 3
    assert result.iloc[0]["engaged_leads"] == 2
    assert result.iloc[0]["registered_leads"] == 1
    assert result.iloc[0]["registration_gap"] == 2
    assert result.iloc[0]["recommended_action"] == "Prioritize registration conversion"


def test_build_campaign_opportunities_resolves_opaque_course_interest():
    leads = pd.DataFrame([
        {"lead_id": "L1", "interest": "CRS-008", "course_id": "CRS-008"},
        {"lead_id": "L2", "interest": "CRS-008", "course_id": "CRS-008"},
    ])
    courses = pd.DataFrame([
        {"course_id": "CRS-008", "name": "SAP S/4HANA Practice"}
    ])

    result = build_campaign_opportunities(
        leads,
        courses,
        pd.DataFrame(columns=["lead_id"]),
        pd.DataFrame(),
        pd.DataFrame(columns=["lead_id"]),
        pd.DataFrame(columns=["lead_id"]),
    )

    assert result.iloc[0]["demand_signal"] == "SAP S/4HANA Practice"
    assert result.iloc[0]["recommended_action"] == "Launch targeted campaign"
