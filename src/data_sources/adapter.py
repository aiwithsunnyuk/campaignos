from abc import ABC, abstractmethod
from typing import Any


class DataSourceAdapter(ABC):
    """Common contract for tenant data sources."""

    @abstractmethod
    def load(self) -> list[dict[str, Any]]:
        """Load records from the configured source."""
        raise NotImplementedError
