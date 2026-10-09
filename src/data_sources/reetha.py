from pathlib import Path

from src.data_adapters.csv_campaign_adapter import CSVCampaignAdapter
from src.data_adapters.csv_course_adapter import CSVCourseAdapter
from src.data_adapters.csv_engagement_adapter import CSVEngagementAdapter
from src.data_adapters.csv_enrollment_adapter import CSVEnrollmentAdapter
from src.data_adapters.csv_lead_adapter import CSVLeadAdapter
from src.data_adapters.csv_registration_adapter import CSVRegistrationAdapter


class ReethaDataSourceLoader:
    """
    Canonical Reetha tenant loader.

    The generic DataSourceAdapter layer is intentionally allowed to
    return ingestion dictionaries. This loader is the canonical
    domain boundary used by CampaignOS intelligence services.
    """

    def __init__(
        self,
        registry,
        factory,
        base_path: str | Path,
    ):
        self._registry = registry
        self._factory = factory
        self._base_path = Path(base_path)

    def load_leads(self):
        return CSVLeadAdapter(
            self._base_path / "leads.csv"
        ).load()

    def load_campaigns(self):
        return CSVCampaignAdapter(
            self._base_path / "campaigns.csv"
        ).load()

    def load_courses(self):
        return CSVCourseAdapter(
            self._base_path / "courses.csv"
        ).load()

    def load_engagements(self):
        return CSVEngagementAdapter(
            self._base_path / "engagements.csv"
        ).load()

    def load_registrations(self):
        return CSVRegistrationAdapter(
            self._base_path / "registrations.csv"
        ).load()

    def load_enrollments(self):
        return CSVEnrollmentAdapter(
            self._base_path / "enrollments.csv"
        ).load()
