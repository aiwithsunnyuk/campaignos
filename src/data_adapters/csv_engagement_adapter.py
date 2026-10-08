import csv
import json
from pathlib import Path

from src.data_contract import Engagement


class CSVEngagementAdapter:
    REQUIRED_COLUMNS = {
        "engagement_id",
        "tenant_id",
        "lead_id",
        "channel",
        "event_type",
        "campaign_id",
        "course_id",
        "occurred_at",
        "metadata",
    }

    def __init__(self, tenant_id: str, path: str | Path):
        self.tenant_id = tenant_id
        self.path = Path(path)

    def load(self) -> list[Engagement]:
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

            return [self._to_engagement(row) for row in reader]

    def _to_engagement(
        self,
        row: dict[str, str],
    ) -> Engagement:
        row_tenant_id = row.get("tenant_id")

        if row_tenant_id != self.tenant_id:
            raise ValueError(
                f"Tenant mismatch: adapter={self.tenant_id}, "
                f"row={row_tenant_id}"
            )

        metadata_raw = row.get("metadata", "").strip()

        if metadata_raw:
            try:
                metadata = json.loads(metadata_raw)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid metadata JSON for engagement "
                    f"{row.get('engagement_id')}"
                ) from exc

            if not isinstance(metadata, dict):
                raise ValueError(
                    f"Engagement metadata must be a JSON object: "
                    f"{row.get('engagement_id')}"
                )
        else:
            metadata = None

        return Engagement(
            engagement_id=row["engagement_id"],
            tenant_id=self.tenant_id,
            lead_id=row["lead_id"],
            channel=row["channel"],
            event_type=row["event_type"],
            campaign_id=row.get("campaign_id") or None,
            course_id=row.get("course_id") or None,
            occurred_at=row["occurred_at"],
            metadata=metadata,
        )
