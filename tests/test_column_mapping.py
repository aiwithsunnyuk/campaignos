import pytest

from src.data_ingestion import ColumnMappingService


def test_create_mapping_decision():
    decision = ColumnMappingService().create_decision(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        dataset_type="lead",
        suggested_column_mapping=(
            ("lead_id", "Lead ID"),
            ("email", "Email Address"),
        ),
    )

    assert decision.dataset_id == "DATASET-001"
    assert decision.tenant_id == "reetha"
    assert decision.dataset_type == "lead"
    assert decision.approved is False
    assert decision.approved_by is None
    assert len(decision.mappings) == 2


def test_approve_mapping():
    service = ColumnMappingService()

    decision = service.create_decision(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        dataset_type="lead",
        suggested_column_mapping=(
            ("lead_id", "Lead ID"),
            ("email", "Email Address"),
        ),
    )

    approved = service.approve(
        decision,
        approved_by="reetha-marketing",
    )

    assert approved.approved is True
    assert approved.approved_by == "reetha-marketing"
    assert approved.mappings == decision.mappings


def test_approval_requires_user():
    service = ColumnMappingService()

    decision = service.create_decision(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        dataset_type="lead",
        suggested_column_mapping=(("lead_id", "Lead ID"),),
    )

    with pytest.raises(ValueError, match="approved_by is required"):
        service.approve(decision, " ")


def test_empty_mapping_cannot_be_approved():
    service = ColumnMappingService()

    decision = service.create_decision(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        dataset_type="unknown",
        suggested_column_mapping=(),
    )

    with pytest.raises(ValueError, match="empty column mapping"):
        service.approve(decision, "reetha-marketing")


def test_mapping_cannot_be_approved_twice():
    service = ColumnMappingService()

    decision = service.create_decision(
        dataset_id="DATASET-001",
        tenant_id="reetha",
        dataset_type="lead",
        suggested_column_mapping=(("lead_id", "Lead ID"),),
    )

    approved = service.approve(decision, "reetha-marketing")

    with pytest.raises(ValueError, match="already approved"):
        service.approve(approved, "reetha-marketing")
