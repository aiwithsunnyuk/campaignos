from .kpis import IntelligenceKPI
from .models import MarketingIntelligence


class MarketingIntelligenceKPIBuilder:
    """Convert marketing intelligence into Command Center KPIs."""

    def build(
        self,
        intelligence: MarketingIntelligence,
    ) -> tuple[IntelligenceKPI, ...]:
        bottleneck_priority = (
            "critical"
            if intelligence.funnel_bottleneck == "registration"
            else "high"
        )

        return (
            IntelligenceKPI(
                key="total_leads",
                label="Total Leads",
                value=intelligence.total_leads,
                unit="leads",
                priority="low",
                explanation="Total leads available in the tenant intelligence snapshot.",
            ),
            IntelligenceKPI(
                key="engaged_leads",
                label="Engaged Leads",
                value=intelligence.engaged_leads,
                unit="leads",
                priority="low",
                explanation="Leads with at least one recorded engagement.",
            ),
            IntelligenceKPI(
                key="registered_leads",
                label="Registered Leads",
                value=intelligence.registered_leads,
                unit="leads",
                priority="medium",
                explanation="Leads that have progressed to registration.",
            ),
            IntelligenceKPI(
                key="enrolled_leads",
                label="Enrolled Leads",
                value=intelligence.enrolled_leads,
                unit="leads",
                priority="medium",
                explanation="Leads that have progressed to enrollment.",
            ),
            IntelligenceKPI(
                key="engagement_rate",
                label="Engagement Rate",
                value=intelligence.engagement_rate,
                unit="%",
                priority="low",
                explanation="Percentage of total leads with recorded engagement.",
            ),
            IntelligenceKPI(
                key="registration_rate",
                label="Registration Conversion",
                value=intelligence.registration_rate,
                unit="%",
                priority=bottleneck_priority,
                explanation="Conversion from engaged leads to registered leads.",
            ),
            IntelligenceKPI(
                key="enrollment_rate",
                label="Enrollment Conversion",
                value=intelligence.enrollment_rate,
                unit="%",
                priority="medium",
                explanation="Conversion from registered leads to enrolled leads.",
            ),
            IntelligenceKPI(
                key="funnel_bottleneck",
                label="Funnel Bottleneck",
                value=intelligence.funnel_bottleneck,
                unit="stage",
                priority=bottleneck_priority,
                explanation="Current weakest conversion stage in the marketing funnel.",
            ),
        )
