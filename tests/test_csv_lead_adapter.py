from pathlib import Path

from src.data_adapters import CSVLeadAdapter


def test_csv_lead_adapter(tmp_path: Path):
    csv_file = tmp_path / "leads.csv"

    csv_file.write_text(
        """lead_id,tenant_id,first_name,last_name,email,phone,source,lifecycle_stage,interest,course_id,lead_score,created_at,updated_at
L001,reetha,John,Doe,john@example.com,9876543210,website,new,AI,CRS001,72.5,2026-10-08T10:00:00,2026-10-08T10:00:00
""",
        encoding="utf-8",
    )

    adapter = CSVLeadAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    leads = adapter.load()

    assert len(leads) == 1
    assert leads[0].lead_id == "L001"
    assert leads[0].tenant_id == "reetha"
    assert leads[0].lead_score == 72.5


def test_csv_adapter_rejects_missing_columns(tmp_path: Path):
    csv_file = tmp_path / "invalid.csv"

    csv_file.write_text(
        """lead_id,first_name
L001,John
""",
        encoding="utf-8",
    )

    adapter = CSVLeadAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    try:
        adapter.load()
        assert False, "Expected missing-column validation error"
    except ValueError as exc:
        assert "Missing required columns" in str(exc)
