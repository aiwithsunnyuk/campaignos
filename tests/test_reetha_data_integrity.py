from pathlib import Path

import pytest

from src.reetha_data import (
    ReethaDataIntegrityError,
    generate_reetha_dataset,
    validate_reetha_dataset,
)


def generate_test_dataset(path: Path) -> None:
    generate_reetha_dataset(
        output_dir=path,
        seed=42,
        lead_count=25,
        campaign_count=5,
        engagement_count=50,
        registration_count=10,
        enrollment_count=5,
    )


def test_reetha_dataset_has_valid_references(tmp_path: Path):
    data_dir = tmp_path / "reetha"

    generate_test_dataset(data_dir)

    validate_reetha_dataset(data_dir)


def test_reetha_dataset_rejects_cross_tenant_record(
    tmp_path: Path,
):
    data_dir = tmp_path / "reetha"

    generate_test_dataset(data_dir)

    leads_file = data_dir / "leads.csv"
    content = leads_file.read_text(encoding="utf-8")
    content = content.replace(
        ",reetha,",
        ",demo,",
        1,
    )
    leads_file.write_text(content, encoding="utf-8")

    with pytest.raises(
        ReethaDataIntegrityError,
        match="tenant_id='reetha'",
    ):
        validate_reetha_dataset(data_dir)


def test_reetha_dataset_rejects_unknown_lead(
    tmp_path: Path,
):
    data_dir = tmp_path / "reetha"

    generate_test_dataset(data_dir)

    engagements_file = data_dir / "engagements.csv"
    content = engagements_file.read_text(encoding="utf-8")

    lines = content.splitlines()
    header = lines[0]
    first_data = lines[1].split(",")

    lead_index = header.split(",").index("lead_id")
    first_data[lead_index] = "LEAD-9999"

    lines[1] = ",".join(first_data)
    engagements_file.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ReethaDataIntegrityError,
        match="unknown lead",
    ):
        validate_reetha_dataset(data_dir)
