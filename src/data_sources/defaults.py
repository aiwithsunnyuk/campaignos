from .models import DataSource
from .registry import DataSourceRegistry


def build_default_registry() -> DataSourceRegistry:
    registry = DataSourceRegistry()

    registry.register(
        DataSource(
            source_id="reetha-leads",
            tenant_id="reetha",
            name="Reetha Leads",
            source_type="csv",
            status="active",
            description="Synthetic Reetha lead dataset.",
        )
    )

    registry.register(
        DataSource(
            source_id="reetha-engagements",
            tenant_id="reetha",
            name="Reetha Engagements",
            source_type="csv",
            status="active",
            description="Synthetic Reetha engagement dataset.",
        )
    )

    registry.register(
        DataSource(
            source_id="reetha-registrations",
            tenant_id="reetha",
            name="Reetha Registrations",
            source_type="csv",
            status="active",
            description="Synthetic Reetha registration dataset.",
        )
    )

    registry.register(
        DataSource(
            source_id="reetha-enrollments",
            tenant_id="reetha",
            name="Reetha Enrollments",
            source_type="csv",
            status="active",
            description="Synthetic Reetha enrollment dataset.",
        )
    )

    return registry
