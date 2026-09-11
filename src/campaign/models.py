from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Campaign:
    """Core CampaignOS campaign definition."""

    campaign_id: str
    campaign_name: str
    business_type: str
    product_name: str
    region: str
    objective: str
    status: str
    start_date: date
    end_date: date
    target_mqls: int
    budget: float
    channels: List[str] = field(default_factory=list)
    owner: str = ""

    def is_active(self, as_of: date | None = None) -> bool:
        """Return True when the campaign is active on the supplied date."""
        check_date = as_of or date.today()
        return (
            self.status.lower() == "running"
            and self.start_date <= check_date <= self.end_date
        )

    @property
    def duration_days(self) -> int:
        """Return campaign duration in calendar days."""
        return (self.end_date - self.start_date).days + 1

    @property
    def budget_per_target_mql(self) -> float:
        """Return planned budget allocated per target MQL."""
        if self.target_mqls <= 0:
            return 0.0
        return self.budget / self.target_mqls
