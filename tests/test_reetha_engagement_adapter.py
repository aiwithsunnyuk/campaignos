from pathlib import Path

import pytest

from src.data_adapters import CSVEngagementAdapter


ENGAGEMENTS_PATH = "data/reetha/engagements.csv"


def test_reetha_engagements_load_into_canonical_contract():
    adapter = CSVEngagementAdapter(
        tenant_id="reetha",
        path=ENGAGEMENTS_PATH,
    )

    engagements = adapter.load()

    assert len(engagements) == 1500
    assert all(
        engagement.tenant_id == "reetha"
        for engagement in engagements
    )

    first = engagements[0]

    assert first.engagement_id == "ENG-00001"
    assert first.tenant_id == "reetha"
    assert first.lead_id == "LEAD-0173"
    assert first.channel == "Organic Search"
    assert first.event_type == "form_started"
    assert first.campaign_id == "CMP-006"
    assert first.course_id == "CRS-010"
    assert first.occurred_at == "2026-06-01T18:00:00"
    assert first.metadata == {}


def test_engagement_adapter_rejects_wrong_tenant(tmp_path: Path):
    csv_file = tmp_path / "wrong_tenant_engagements.csv"

    csv_file.write_text(
        "engagement_id,tenant_id,lead_id,channel,event_type,"
        "campaign_id,course_id,occurred_at,metadata\n"
        "ENG-00001,demo,LEAD-0001,Email,email_opened,"
        "CMP-001,CRS-001,2026-01-01T10:00:00,{}\n",
        encoding="utf-8",
    )

    adapter = CSVEngagementAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    with pytest.raises(ValueError, match="Tenant mismatch"):
        adapter.load()


def test_engagement_adapter_rejects_missing_required_columns(
    tmp_path: Path,
):
    csv_file = tmp_path / "invalid_engagements.csv"

    csv_file.write_text(
        "engagement_id,tenant_id,lead_id,event_type\n"
        "ENG-00001,reetha,LEAD-0001,email_opened\n",
        encoding="utf-8",
    )

    adapter = CSVEngagementAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        adapter.load()


def test_engagement_adapter_rejects_invalid_metadata_json(
    tmp_path: Path,
):
    csv_file = tmp_path / "invalid_metadata.csv"

    csv_file.write_text(
        "engagement_id,tenant_id,lead_id,channel,event_type,"
        "campaign_id,course_id,occurred_at,metadata\n"
        "ENG-00001,reetha,LEAD-0001,Email,email_opened,"
        "CMP-001,CRS-001,2026-01-01T10:00:00,{invalid}\n",
        encoding="utf-8",
    )

    adapter = CSVEngagementAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    with pytest.raises(
        ValueError,
        match="Invalid metadata JSON",
    ):
        adapter.load()
