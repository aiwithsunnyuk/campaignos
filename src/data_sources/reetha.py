from pathlib import Path

from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter
from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter

from .factory import DataSourceAdapterFactory
from .registry import DataSourceRegistry


class ReethaDataSourceLoader:
    """Loads authorized Reetha sources through the data-source layer."""

    def __init__(
        self,
        registry: DataSourceRegistry,
        factory: DataSourceAdapterFactory,
        base_path: Path,
    ):
        self.registry = registry
        self.factory = factory
        self.base_path = base_path

    def load_leads(self) -> list[dict]:
        source = self.registry.get("reetha-leads")

        adapter = self.factory.create(
            source,
            csv_loader=lambda: CSVLeadAdapter(
                "reetha",
                self.base_path / "leads.csv",
            ).load(),
        )

        return adapter.load()

    def load_engagements(self) -> list[dict]:
        source = self.registry.get("reetha-engagements")

        adapter = self.factory.create(
            source,
            csv_loader=lambda: CSVEngagementAdapter(
                "reetha",
                self.base_path / "engagements.csv",
            ).load(),
        )

        return adapter.load()

    def load_registrations(self) -> list[dict]:
        source = self.registry.get("reetha-registrations")

        adapter = self.factory.create(
            source,
            csv_loader=lambda: CSVRegistrationAdapter(
                "reetha",
                self.base_path / "registrations.csv",
            ).load(),
        )

        return adapter.load()

    def load_enrollments(self) -> list[dict]:
        source = self.registry.get("reetha-enrollments")

        adapter = self.factory.create(
            source,
            csv_loader=lambda: CSVEnrollmentAdapter(
                "reetha",
                self.base_path / "enrollments.csv",
            ).load(),
        )

        return adapter.load()
