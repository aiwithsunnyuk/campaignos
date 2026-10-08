from pathlib import Path

from src.reetha_data import generate_reetha_dataset


def test_reetha_dataset_generation(tmp_path: Path):
    output = tmp_path / "reetha"

    generate_reetha_dataset(
        output_dir=output,
        seed=42,
        lead_count=25,
        campaign_count=5,
        engagement_count=50,
        registration_count=10,
        enrollment_count=5,
    )

    expected_files = {
        "courses.csv",
        "campaigns.csv",
        "leads.csv",
        "engagements.csv",
        "registrations.csv",
        "enrollments.csv",
    }

    assert {
        path.name
        for path in output.iterdir()
    } == expected_files


def test_reetha_dataset_is_deterministic(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"

    generate_reetha_dataset(
        first,
        seed=42,
        lead_count=10,
        campaign_count=3,
        engagement_count=20,
        registration_count=5,
        enrollment_count=3,
    )

    generate_reetha_dataset(
        second,
        seed=42,
        lead_count=10,
        campaign_count=3,
        engagement_count=20,
        registration_count=5,
        enrollment_count=3,
    )

    assert (
        (first / "leads.csv").read_text()
        == (second / "leads.csv").read_text()
    )
