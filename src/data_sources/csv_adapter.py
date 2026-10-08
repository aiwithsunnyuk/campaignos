from pathlib import Path
from typing import Any, Callable

from .adapter import DataSourceAdapter


class CSVDataSourceAdapter(DataSourceAdapter):
    """
    Generic adapter wrapper around an existing CSV loader.

    The existing domain adapter remains responsible for:
    tenant validation,
    schema validation,
    and canonical record construction.
    """

    def __init__(
        self,
        loader: Callable[[], list[Any]],
    ):
        self._loader = loader

    def load(self) -> list[dict[str, Any]]:
        records = self._loader()

        return [
            record.__dict__
            if hasattr(record, "__dict__")
            else dict(record)
            for record in records
        ]
