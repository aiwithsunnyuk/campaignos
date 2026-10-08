from pathlib import Path
from typing import Callable

from .adapter import DataSourceAdapter
from .csv_adapter import CSVDataSourceAdapter
from .models import DataSource


class DataSourceAdapterFactory:
    """Creates adapters for registered data source types."""

    def create(
        self,
        source: DataSource,
        *,
        csv_loader: Callable[[], list] | None = None,
        path: Path | None = None,
    ) -> DataSourceAdapter:

        if source.source_type == "csv":

            if csv_loader is None:
                raise ValueError(
                    "csv_loader is required for CSV data sources."
                )

            return CSVDataSourceAdapter(csv_loader)

        raise NotImplementedError(
            f"Adapter not implemented for source type: "
            f"{source.source_type}"
        )
