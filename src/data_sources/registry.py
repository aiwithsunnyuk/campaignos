from .models import DataSource


class DataSourceRegistry:
    def __init__(self):
        self._sources: dict[str, DataSource] = {}

    def register(self, source: DataSource) -> None:
        if source.source_id in self._sources:
            raise ValueError(
                f"Data source already registered: {source.source_id}"
            )

        self._sources[source.source_id] = source

    def get(self, source_id: str) -> DataSource:
        try:
            return self._sources[source_id]
        except KeyError:
            raise KeyError(
                f"Unknown data source: {source_id}"
            )

    def list_for_tenant(self, tenant_id: str) -> tuple[DataSource, ...]:
        return tuple(
            source
            for source in self._sources.values()
            if source.tenant_id == tenant_id
        )
