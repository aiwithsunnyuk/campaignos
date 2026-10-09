from pathlib import Path

from .factory import DataSourceAdapterFactory
from .reetha import ReethaDataSourceLoader
from .canonical import canonicalize_records
from .registry import DataSourceRegistry


class TenantDataService:
    """
    Tenant-scoped entry point for canonical GTM source records.

    The intelligence layer should consume this service rather than
    knowing how a tenant's underlying data is stored.
    """

    def __init__(
        self,
        registry: DataSourceRegistry,
        factory: DataSourceAdapterFactory,
        base_path: Path,
    ):
        self._registry = registry
        self._factory = factory
        self._base_path = base_path

    def load_reetha(self):
        loader = ReethaDataSourceLoader(
            registry=self._registry,
            factory=self._factory,
            base_path=self._base_path,
        )

        return {
            "leads": canonicalize_records(loader.load_leads()),
            "engagements": canonicalize_records(loader.load_engagements()),
            "registrations": canonicalize_records(loader.load_registrations()),
            "enrollments": canonicalize_records(loader.load_enrollments()),
        }
