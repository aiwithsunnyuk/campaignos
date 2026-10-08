import csv
from pathlib import Path


class ReethaDataIntegrityError(ValueError):
    """Raised when the Reetha synthetic dataset is inconsistent."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def _ids(rows: list[dict[str, str]], field: str) -> set[str]:
    return {
        row[field]
        for row in rows
        if row.get(field)
    }


def validate_reetha_dataset(
    data_dir: str | Path,
) -> None:
    """
    Validate tenant ownership and referential integrity
    across the complete Reetha synthetic dataset.
    """

    data_dir = Path(data_dir)

    required_files = {
        "courses.csv",
        "campaigns.csv",
        "leads.csv",
        "engagements.csv",
        "registrations.csv",
        "enrollments.csv",
    }

    missing = [
        filename
        for filename in required_files
        if not (data_dir / filename).exists()
    ]

    if missing:
        raise ReethaDataIntegrityError(
            f"Missing dataset files: {sorted(missing)}"
        )

    courses = _read_csv(data_dir / "courses.csv")
    campaigns = _read_csv(data_dir / "campaigns.csv")
    leads = _read_csv(data_dir / "leads.csv")
    engagements = _read_csv(data_dir / "engagements.csv")
    registrations = _read_csv(data_dir / "registrations.csv")
    enrollments = _read_csv(data_dir / "enrollments.csv")

    # ---------------------------------------------------------
    # Tenant isolation
    # ---------------------------------------------------------

    all_rows = (
        courses
        + campaigns
        + leads
        + engagements
        + registrations
        + enrollments
    )

    for row in all_rows:
        if row.get("tenant_id") != "reetha":
            raise ReethaDataIntegrityError(
                "All Reetha records must have tenant_id='reetha'"
            )

    # ---------------------------------------------------------
    # Primary-key uniqueness
    # ---------------------------------------------------------

    entities = [
        ("course_id", courses),
        ("campaign_id", campaigns),
        ("lead_id", leads),
        ("engagement_id", engagements),
        ("registration_id", registrations),
        ("enrollment_id", enrollments),
    ]

    for field, rows in entities:
        values = [row[field] for row in rows]

        if len(values) != len(set(values)):
            raise ReethaDataIntegrityError(
                f"Duplicate values detected for {field}"
            )

    # ---------------------------------------------------------
    # Foreign-key references
    # ---------------------------------------------------------

    course_ids = _ids(courses, "course_id")
    campaign_ids = _ids(campaigns, "campaign_id")
    lead_ids = _ids(leads, "lead_id")

    for row in engagements:
        if row["lead_id"] not in lead_ids:
            raise ReethaDataIntegrityError(
                f"Engagement references unknown lead: "
                f"{row['lead_id']}"
            )

        if row["campaign_id"] not in campaign_ids:
            raise ReethaDataIntegrityError(
                f"Engagement references unknown campaign: "
                f"{row['campaign_id']}"
            )

        if row["course_id"] not in course_ids:
            raise ReethaDataIntegrityError(
                f"Engagement references unknown course: "
                f"{row['course_id']}"
            )

    for row in registrations:
        if row["lead_id"] not in lead_ids:
            raise ReethaDataIntegrityError(
                f"Registration references unknown lead: "
                f"{row['lead_id']}"
            )

        if row["course_id"] not in course_ids:
            raise ReethaDataIntegrityError(
                f"Registration references unknown course: "
                f"{row['course_id']}"
            )

    for row in enrollments:
        if row["lead_id"] not in lead_ids:
            raise ReethaDataIntegrityError(
                f"Enrollment references unknown lead: "
                f"{row['lead_id']}"
            )

        if row["course_id"] not in course_ids:
            raise ReethaDataIntegrityError(
                f"Enrollment references unknown course: "
                f"{row['course_id']}"
            )
