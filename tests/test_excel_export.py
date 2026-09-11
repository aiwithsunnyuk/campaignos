from pathlib import Path

import pandas as pd

from src.reporting.excel_export import (
    build_campaign_performance,
    build_executive_summary,
    build_lead_export,
    build_regional_performance,
    export_campaignos_workbook,
)


def sample_campaigns():
    return pd.DataFrame(
        [
            {
                "campaign_id": "CMP-001",
                "campaign_name": "Campaign One",
                "business_type": "Training & Education",
                "region": "APAC",
                "objective": "Engagement",
                "status": "Completed",
                "budget": 10000,
                "start_date": "2026-01-01",
            },
            {
                "campaign_id": "CMP-002",
                "campaign_name": "Campaign Two",
                "business_type": "Professional Information Services",
                "region": "Europe",
                "objective": "Lead Generation",
                "status": "Running",
                "budget": 15000,
                "start_date": "2026-02-01",
            },
        ]
    )


def sample_activities():
    return pd.DataFrame(
        [
            {
                "activity_id": "ACT-001",
                "contact_id": "CNT-001",
                "campaign_id": "CMP-001",
                "activity_type": "Email Sent",
            },
            {
                "activity_id": "ACT-002",
                "contact_id": "CNT-001",
                "campaign_id": "CMP-001",
                "activity_type": "Email Opened",
            },
            {
                "activity_id": "ACT-003",
                "contact_id": "CNT-001",
                "campaign_id": "CMP-001",
                "activity_type": "Email Clicked",
            },
            {
                "activity_id": "ACT-004",
                "contact_id": "CNT-001",
                "campaign_id": "CMP-001",
                "activity_type": "Form Submitted",
            },
        ]
    )


def sample_contacts():
    return pd.DataFrame(
        [
            {
                "contact_id": "CNT-001",
                "first_name": "Sunny",
                "last_name": "Test",
                "email": "sunny@example.com",
                "region": "APAC",
                "lead_score": 90,
                "lifecycle_stage": "MQL",
            }
        ]
    )


def test_campaign_performance():
    result = build_campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    assert len(result) == 2
    assert result.loc[0, "sent"] == 1
    assert result.loc[0, "opened"] == 1
    assert result.loc[0, "clicked"] == 1
    assert result.loc[0, "converted"] == 1
    assert result.loc[0, "conversion_rate"] == 100.0


def test_regional_performance():
    performance = build_campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    result = build_regional_performance(
        performance
    )

    assert set(result["region"]) == {
        "APAC",
        "Europe",
    }


def test_executive_summary():
    performance = build_campaign_performance(
        sample_campaigns(),
        sample_activities(),
    )

    result = build_executive_summary(
        performance
    )

    assert "metric" in result.columns
    assert "value" in result.columns
    assert len(result) == 9


def test_lead_export():
    result = build_lead_export(
        sample_contacts()
    )

    assert len(result) == 1
    assert result.iloc[0]["contact_id"] == "CNT-001"


def test_excel_workbook(tmp_path):
    output = tmp_path / "campaignos_test.xlsx"

    result = export_campaignos_workbook(
        output,
        sample_campaigns(),
        sample_activities(),
        sample_contacts(),
    )

    assert Path(result).exists()

    workbook = pd.ExcelFile(result)

    assert "Executive Summary" in workbook.sheet_names
    assert "Campaign Performance" in workbook.sheet_names
    assert "Regional Performance" in workbook.sheet_names
    assert "Lead Export" in workbook.sheet_names
