from typing import Protocol

from src.data_contract import Lead


class LeadAdapter(Protocol):
    """
    Standard interface for converting external lead sources
    into CampaignOS canonical Lead objects.
    """

    def load(self) -> list[Lead]:
        """Load and transform source data into canonical leads."""
        ...
