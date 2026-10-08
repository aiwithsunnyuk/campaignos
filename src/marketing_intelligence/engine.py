from src.gtm_intelligence.models import GTMIntelligenceSnapshot
from src.marketing_intelligence.models import MarketingIntelligence


class MarketingIntelligenceEngine:
    """Interpret an existing GTM intelligence snapshot."""

    def build(
        self,
        snapshot: GTMIntelligenceSnapshot,
    ) -> MarketingIntelligence:
        total_leads = snapshot.total_leads
        engaged_leads = snapshot.leads_with_engagement
        registered_leads = snapshot.leads_with_registration
        enrolled_leads = snapshot.leads_with_enrollment

        engagement_rate = (
            engaged_leads / total_leads * 100
            if total_leads
            else 0.0
        )

        registration_rate = (
            registered_leads / engaged_leads * 100
            if engaged_leads
            else 0.0
        )

        enrollment_rate = (
            enrolled_leads / registered_leads * 100
            if registered_leads
            else 0.0
        )

        if registration_rate < enrollment_rate:
            funnel_bottleneck = "registration"
        else:
            funnel_bottleneck = "enrollment"

        top_channels = tuple(
            sorted(
                snapshot.channel_coverage,
                key=lambda item: (-item[1], item[0]),
            )[:5]
        )

        top_event_types = tuple(
            sorted(
                snapshot.event_type_coverage,
                key=lambda item: (-item[1], item[0]),
            )[:5]
        )

        headline = (
            f"{snapshot.tenant_id}: "
            f"{engaged_leads} of {total_leads} leads are engaged; "
            f"{registered_leads} registered and "
            f"{enrolled_leads} enrolled. "
            f"Primary funnel bottleneck: {funnel_bottleneck}."
        )

        return MarketingIntelligence(
            tenant_id=snapshot.tenant_id,
            total_leads=total_leads,
            engaged_leads=engaged_leads,
            registered_leads=registered_leads,
            enrolled_leads=enrolled_leads,
            engagement_rate=round(engagement_rate, 2),
            registration_rate=round(registration_rate, 2),
            enrollment_rate=round(enrollment_rate, 2),
            top_channels=top_channels,
            top_event_types=top_event_types,
            funnel_bottleneck=funnel_bottleneck,
            headline=headline,
        )
