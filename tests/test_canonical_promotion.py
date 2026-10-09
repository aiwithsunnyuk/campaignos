import pytest

from src.data_ingestion import (
    CanonicalDatasetPromotionService,
    CanonicalLeadTransformer,
    DatasetPromotionService,
    DatasetVersionService,
    ColumnMappingService,
    DataQualityReport,
)


def build_flow():
    dataset_id = "LEADS"
    tenant_id = "reetha"

    mapping = ColumnMappingService().create_decision(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        dataset_type="lead",
        suggested_column_mapping=(
            ("lead_id", "Lead ID"),
            ("email", "Email Address"),
            ("name", "Full Name"),
            ("phone", "Mobile"),
        ),
    )

    mapping = ColumnMappingService().approve(
        mapping,
        approved_by="reetha-marketing",
    )

    report = DataQualityReport(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        total_rows=2,
        valid_rows=2,
        duplicate_rows=0,
        quality_score=100.0,
        issues=(),
    )

    promotion = DatasetPromotionService().create(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        report=report,
    )

    promotion = DatasetPromotionService().promote(
        promotion,
        approved_by="reetha-marketing",
    )

    version = DatasetVersionService().create_version(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        dataset_type="lead",
        file_name="leads_oct.xlsx",
    )

    return mapping, promotion, version


def test_transform_leads():
    rows = [
        {
            "Lead ID": "L1",
            "Email Address": "one@example.com",
            "Full Name": "One User",
            "Mobile": "9999999999",
        },
        {
            "Lead ID": "L2",
            "Email Address": "two@example.com",
            "Full Name": "Two User",
            "Mobile": "8888888888",
        },
    ]

    records = CanonicalLeadTransformer().transform(
        tenant_id="reetha",
        rows=rows,
        mapping={
            "lead_id": "Lead ID",
            "email": "Email Address",
            "name": "Full Name",
            "phone": "Mobile",
        },
    )

    assert len(records) == 2
    assert records[0].lead_id == "L1"
    assert records[0].tenant_id == "reetha"
    assert records[0].email == "one@example.com"


def test_canonical_promotion():
    mapping, promotion, version = build_flow()

    leads = CanonicalLeadTransformer().transform(
        tenant_id="reetha",
        rows=[
            {
                "Lead ID": "L1",
                "Email Address": "one@example.com",
                "Full Name": "One User",
            },
            {
                "Lead ID": "L2",
                "Email Address": "two@example.com",
                "Full Name": "Two User",
            },
        ],
        mapping={
            "lead_id": "Lead ID",
            "email": "Email Address",
            "name": "Full Name",
        },
    )

    result = CanonicalDatasetPromotionService().promote_leads(
        promotion=promotion,
        version=version,
        mapping=mapping,
        leads=leads,
    )

    assert result.dataset_id == "LEADS"
    assert result.tenant_id == "reetha"
    assert result.version == 1
    assert result.record_count == 2


def test_unapproved_mapping_cannot_promote():
    mapping, promotion, version = build_flow()

    unapproved = ColumnMappingService().create_decision(
        dataset_id="LEADS",
        tenant_id="reetha",
        dataset_type="lead",
        suggested_column_mapping=(
            ("lead_id", "Lead ID"),
            ("email", "Email Address"),
        ),
    )

    leads = CanonicalLeadTransformer().transform(
        tenant_id="reetha",
        rows=[
            {
                "Lead ID": "L1",
                "Email Address": "one@example.com",
            }
        ],
        mapping={
            "lead_id": "Lead ID",
            "email": "Email Address",
        },
    )

    with pytest.raises(ValueError, match="mapping must be approved"):
        CanonicalDatasetPromotionService().promote_leads(
            promotion=promotion,
            version=version,
            mapping=unapproved,
            leads=leads,
        )


def test_non_promoted_dataset_cannot_promote():
    dataset_id = "LEADS"
    tenant_id = "reetha"

    mapping = ColumnMappingService().create_decision(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        dataset_type="lead",
        suggested_column_mapping=(
            ("lead_id", "Lead ID"),
            ("email", "Email Address"),
        ),
    )

    mapping = ColumnMappingService().approve(
        mapping,
        approved_by="reetha-marketing",
    )

    report = DataQualityReport(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        total_rows=1,
        valid_rows=1,
        duplicate_rows=0,
        quality_score=100.0,
        issues=(),
    )

    promotion = DatasetPromotionService().create(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        report=report,
    )

    version = DatasetVersionService().create_version(
        dataset_id=dataset_id,
        tenant_id=tenant_id,
        dataset_type="lead",
        file_name="leads.xlsx",
    )

    leads = CanonicalLeadTransformer().transform(
        tenant_id=tenant_id,
        rows=[
            {
                "Lead ID": "L1",
                "Email Address": "one@example.com",
            }
        ],
        mapping={
            "lead_id": "Lead ID",
            "email": "Email Address",
        },
    )

    with pytest.raises(ValueError, match="must be promoted"):
        CanonicalDatasetPromotionService().promote_leads(
            promotion=promotion,
            version=version,
            mapping=mapping,
            leads=leads,
        )


def test_tenant_mismatch_is_blocked():
    mapping, promotion, version = build_flow()

    wrong_tenant_version = DatasetVersionService().create_version(
        dataset_id="LEADS",
        tenant_id="demo",
        dataset_type="lead",
        file_name="demo.xlsx",
    )

    leads = CanonicalLeadTransformer().transform(
        tenant_id="reetha",
        rows=[
            {
                "Lead ID": "L1",
                "Email Address": "one@example.com",
            }
        ],
        mapping={
            "lead_id": "Lead ID",
            "email": "Email Address",
        },
    )

    with pytest.raises(ValueError, match="Version tenant"):
        CanonicalDatasetPromotionService().promote_leads(
            promotion=promotion,
            version=wrong_tenant_version,
            mapping=mapping,
            leads=leads,
        )
