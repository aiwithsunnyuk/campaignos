import pandas as pd

from src.reetha_demand_intelligence import build_demand_summary


def test_build_demand_summary_resolves_opaque_course_ids_to_catalogue_names():
    leads = pd.DataFrame(
        [
            {"lead_id": "L1", "interest": "CRS-008", "course_id": "CRS-008"},
            {"lead_id": "L2", "interest": "CRS-008", "course_id": "CRS-008"},
            {"lead_id": "L3", "interest": "CRS-010", "course_id": "CRS-010"},
        ]
    )
    courses = pd.DataFrame(
        [
            {"course_id": "CRS-008", "name": "SAP S/4HANA Practice"},
            {"course_id": "CRS-010", "name": "SAP BTP Practice"},
        ]
    )

    result = build_demand_summary(leads, courses)

    rows = dict(zip(result["demand_signal"], result["interested_leads"]))

    assert rows["SAP S/4HANA Practice"] == 2
    assert rows["SAP BTP Practice"] == 1
    assert "CRS-008" not in rows
    assert "CRS-010" not in rows


def test_build_demand_summary_preserves_real_interest_labels():
    leads = pd.DataFrame(
        [
            {"lead_id": "L1", "interest": "SAP MM", "course_id": "CRS-008"},
            {"lead_id": "L2", "interest": "SAP MM", "course_id": "CRS-008"},
        ]
    )
    courses = pd.DataFrame(
        [{"course_id": "CRS-008", "name": "Some Course"}]
    )

    result = build_demand_summary(leads, courses)

    assert result.iloc[0]["demand_signal"] == "SAP MM"
    assert result.iloc[0]["interested_leads"] == 2
