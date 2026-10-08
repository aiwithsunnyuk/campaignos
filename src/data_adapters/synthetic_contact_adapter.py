import csv
from pathlib import Path

from src.data_contract import Lead


class SyntheticContactLeadAdapter:
    """
    Maps CampaignOS M1-M11 synthetic contacts into
    the M12 canonical Lead contract.
    """

    REQUIRED_COLUMNS = {
        "contact_id",
        "first_name",
        "last_name",
        "email",
        "lifecycle_stage",
        "lead_score",
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

        return Lead(
            lead_id=row["contact_id"],
            tenant_id=self.tenant_id,
            first_name=row["first_name"],
            last_name=row["last_name"] or None,
            email=row["email"] or None,
            phone=None,
            source="synthetic_contacts",
            lifecycle_stage=row["lifecycle_stage"],
            interest=None,
            course_id=None,
            lead_score=float(lead_score) if lead_score else None,
            created_at="",
            updated_at="",
        )
