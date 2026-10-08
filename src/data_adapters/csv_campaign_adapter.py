import csv
from pathlib import Path

from src.data_contract import Campaign


class CSVCampaignAdapter:
    """Convert a CampaignOS-compatible campaign CSV into canonical Campaign objects."""

    REQUIRED_COLUMNS = {
        "campaign_id",
        "tenant_id",
        "name",
        "channel",
        "campaign_type",
        "status",
        "start_date",
        "end_date",
        "budget",
        "created_at",
        "updated_at",
    }

    def __init__(self, tenant_id: str, path: str | Path):
        self.tenant_id = tenant_id
        self.path = Path(path)

    def load(self) -> list[Campaign]:
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
                self._to_campaign(row)
                for row in reader
            ]

    def _to_campaign(self, row: dict[str, str]) -> Campaign:
        row_tenant_id = row.get("tenant_id")

        if row_tenant_id != self.tenant_id:
            raise ValueError(
                f"Tenant mismatch: adapter={self.tenant_id}, "
                f"row={row_tenant_id}"
            )

        budget = row.get("budget")

        return Campaign(
            campaign_id=row["campaign_id"],
            tenant_id=self.tenant_id,
            name=row["name"],
            channel=row["channel"],
            campaign_type=row["campaign_type"],
            status=row["status"],
            start_date=row["start_date"],
            end_date=row["end_date"] or None,
            budget=float(budget) if budget else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
