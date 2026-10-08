
from src.data_adapters import CSVLeadAdapter


def test_reetha_leads_load_into_canonical_contract():
    adapter = CSVLeadAdapter(
        tenant_id="reetha",
        path="data/reetha/leads.csv",
    )

    leads = adapter.load()

    assert len(leads) == 250
    assert all(lead.tenant_id == "reetha" for lead in leads)
    assert all(lead.lead_id for lead in leads)

    first = leads[0]

    assert first.lead_id == "LEAD-0001"
    assert first.tenant_id == "reetha"
    assert first.first_name == "Aditya"
    assert first.last_name == "Patel"
    assert first.email == "aditya.patel1@example.com"


def test_reetha_adapter_rejects_wrong_tenant():
    from pathlib import Path

    csv_file = Path("data/reetha/wrong_tenant_leads.csv")

    csv_file.write_text(
        """lead_id,tenant_id,first_name,last_name,email,phone,source,lifecycle_stage,interest,course_id,lead_score,created_at,updated_at
LEAD-X001,demo,Test,User,test@example.com,9000000000,Website,new,AI,CRS001,50.0,2026-10-08T10:00:00,2026-10-08T10:00:00
""",
        encoding="utf-8",
    )

    adapter = CSVLeadAdapter(
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
