from src.data_adapters import CSVCampaignAdapter


def test_reetha_campaigns_load_into_canonical_contract():
    adapter = CSVCampaignAdapter(
        tenant_id="reetha",
        path="data/reetha/campaigns.csv",
    )

    campaigns = adapter.load()

    assert len(campaigns) == 20
    assert all(campaign.tenant_id == "reetha" for campaign in campaigns)

    first = campaigns[0]

    assert first.campaign_id == "CMP-001"
    assert first.tenant_id == "reetha"
    assert first.name == "Reetha Campaign 001"
    assert first.channel == "LinkedIn"
    assert first.campaign_type == "webinar"
    assert first.status == "draft"
    assert first.budget == 50000.0


def test_reetha_campaign_adapter_rejects_wrong_tenant():
    from pathlib import Path

    csv_file = Path("data/reetha/wrong_tenant_campaigns.csv")

    csv_file.write_text(
        """campaign_id,tenant_id,name,channel,campaign_type,status,start_date,end_date,budget,created_at,updated_at
CMP-X01,demo,Wrong Tenant Campaign,Email,webinar,draft,2026-10-08,2026-10-18,10000,2026-10-08T00:00:00,2026-10-18T00:00:00
""",
        encoding="utf-8",
    )

    adapter = CSVCampaignAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    try:
        adapter.load()
        assert False, "Expected tenant mismatch validation error"
    except ValueError as exc:
        assert "tenant" in str(exc).lower()
    finally:
        csv_file.unlink(missing_ok=True)


def test_reetha_campaign_adapter_rejects_missing_columns():
    from pathlib import Path

    csv_file = Path("data/reetha/invalid_campaigns.csv")

    csv_file.write_text(
        """campaign_id,tenant_id,name
CMP-X02,reetha,Incomplete Campaign
""",
        encoding="utf-8",
    )

    adapter = CSVCampaignAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    try:
        adapter.load()
        assert False, "Expected missing-column validation error"
    except ValueError as exc:
        assert "missing required columns" in str(exc).lower()
    finally:
        csv_file.unlink(missing_ok=True)
