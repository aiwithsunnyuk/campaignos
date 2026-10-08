import pytest

from src.data_contract import (
    DataContractValidationError,
    Lead,
    validate_leads,
)


def make_lead(
    lead_id: str = "L001",
    tenant_id: str = "reetha",
) -> Lead:
    return Lead(
        lead_id=lead_id,
        tenant_id=tenant_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="9876543210",
        source="website",
        lifecycle_stage="new",
        interest="AI",
        course_id="CRS001",
        lead_score=72.5,
        created_at="2026-10-08T10:00:00",
        updated_at="2026-10-08T10:00:00",
    )


def test_valid_leads_pass_validation():
    leads = [
        make_lead("L001", "reetha"),
        make_lead("L002", "reetha"),
    ]

    validated = validate_leads(leads, "reetha")

    assert len(validated) == 2
    assert validated[0].tenant_id == "reetha"


def test_cross_tenant_lead_is_rejected():
    leads = [
        make_lead("L001", "reetha"),
        make_lead("L002", "demo"),
    ]

    with pytest.raises(DataContractValidationError, match="Tenant mismatch"):
        validate_leads(leads, "reetha")


def test_duplicate_lead_is_rejected():
    leads = [
        make_lead("L001", "reetha"),
        make_lead("L001", "reetha"),
    ]

    with pytest.raises(DataContractValidationError, match="Duplicate lead_id"):
        validate_leads(leads, "reetha")


def test_missing_tenant_is_rejected():
    with pytest.raises(
        DataContractValidationError,
        match="tenant_id is required",
    ):
        validate_leads([make_lead()], "")
