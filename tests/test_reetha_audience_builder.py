import pandas as pd

from src.reetha_audience_builder import build_audience_segments, summarize_audience_segments


def test_audience_builder_is_not_limited_to_direct_module_interest():
    leads = pd.DataFrame([
        {"lead_id": "L1", "interest": "SAP BTP", "lifecycle_stage": "experienced"},
        {"lead_id": "L2", "interest": "Python", "lifecycle_stage": "career transformation"},
        {"lead_id": "L3", "interest": "None", "lifecycle_stage": "fresher"},
        {"lead_id": "L4", "interest": "Cybersecurity", "lifecycle_stage": "professional"},
    ])
    courses = pd.DataFrame(columns=["course_id", "name"])

    audience = build_audience_segments(
        leads,
        courses,
        pd.DataFrame(columns=["lead_id"]),
        pd.DataFrame(columns=["lead_id"]),
        pd.DataFrame(columns=["lead_id"]),
        opportunity_signal="SAP BTP",
    )

    assert len(audience) == 4
    assert set(audience["audience_segment"]) >= {
        "Direct Fit",
        "Career Transformation",
        "Fresher / Career Entry",
        "Adjacent Fit",
    }


def test_audience_summary_has_no_fixed_size_ceiling_and_preserves_explanation():
    leads = pd.DataFrame([
        {"lead_id": f"L{i}", "interest": "SAP BTP", "lifecycle_stage": "experienced"}
        for i in range(1, 21)
    ])

    audience = build_audience_segments(
        leads,
        pd.DataFrame(columns=["course_id", "name"]),
        pd.DataFrame(columns=["lead_id"]),
        pd.DataFrame(columns=["lead_id"]),
        pd.DataFrame(columns=["lead_id"]),
        opportunity_signal="SAP BTP",
    )
    summary = summarize_audience_segments(audience)

    assert int(summary["audience_size"].sum()) == 20
    assert int(summary.iloc[0]["audience_size"]) == 20
    assert audience["audience_rationale"].notna().all()
    assert "Direct Fit" in set(summary["audience_segment"])
