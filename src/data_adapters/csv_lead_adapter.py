import csv
from pathlib import Path

from src.data_contract import Lead


class CSVLeadAdapter:
    """
    Converts a source-system CSV representation into
    CampaignOS canonical Lead objects.
    """

    REQUIRED_COLUMNS = {
        "lead_id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "source",
        "lifecycle_stage",
        "interest",
        "course_id",
        "lead_score",
        "created_at",
        "updated_at",
    }

    def __init__(self, tenant_id: str, path: str | Path):
        if not tenant_id:
            raise ValueError("tenant_id is required")

        self.tenant_id = tenant_id
        self.path = Path(path)

    def load(self) -> list[Lead]:
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        with self.path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            columns = set(reader.fieldnames or [])
            missing = self.REQUIRED_COLUMNS - columns

            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}"
                )

            return [
                self._to_lead(row)
                for row in reader
            ]

    def _to_lead(self, row: dict[str, str]) -> Lead:
        lead_score = row.get("lead_score")
        row_tenant_id = row.get("tenant_id")

        if row_tenant_id != self.tenant_id:
            raise ValueError(
                f"Tenant mismatch: adapter={self.tenant_id}, row={row_tenant_id}"
            )

        return Lead(
            lead_id=row["lead_id"],
            tenant_id=self.tenant_id,
            first_name=row["first_name"],
            last_name=row["last_name"] or None,
            email=row["email"] or None,
            phone=row["phone"] or None,
            source=row["source"],
            lifecycle_stage=row["lifecycle_stage"],
            interest=row["interest"] or None,
            course_id=row["course_id"] or None,
            lead_score=float(lead_score) if lead_score else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
