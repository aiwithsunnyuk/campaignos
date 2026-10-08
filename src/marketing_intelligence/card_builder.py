from .cards import IntelligenceCard
from .models import MarketingIntelligence


class MarketingIntelligenceCardBuilder:
    """Build prioritized, explainable intelligence cards."""

    def build(
        self,
        intelligence: MarketingIntelligence,
    ) -> tuple[IntelligenceCard, ...]:
        cards: list[IntelligenceCard] = []

        if intelligence.funnel_bottleneck == "registration":
            cards.append(
                IntelligenceCard(
                    card_id="FUNNEL-REGISTRATION",
                    tenant_id=intelligence.tenant_id,
                    title="Registration Conversion Bottleneck",
                    priority="critical",
                    metric="Registration Conversion",
                    value=f"{intelligence.registration_rate:.2f}%",
                    evidence=(
                        f"{intelligence.engaged_leads} engaged leads",
                        f"{intelligence.registered_leads} registered leads",
                        (
                            f"{intelligence.registration_rate:.2f}% "
                            "engaged-to-registration conversion"
                        ),
                    ),
                    recommendation=(
                        "Prioritize registration conversion through "
                        "targeted follow-up and registration-focused journeys."
                    ),
                )
            )

        elif intelligence.funnel_bottleneck == "enrollment":
            cards.append(
                IntelligenceCard(
                    card_id="FUNNEL-ENROLLMENT",
                    tenant_id=intelligence.tenant_id,
                    title="Enrollment Conversion Bottleneck",
                    priority="high",
                    metric="Enrollment Conversion",
                    value=f"{intelligence.enrollment_rate:.2f}%",
                    evidence=(
                        f"{intelligence.registered_leads} registered leads",
                        f"{intelligence.enrolled_leads} enrolled leads",
                        (
                            f"{intelligence.enrollment_rate:.2f}% "
                            "registration-to-enrollment conversion"
                        ),
                    ),
                    recommendation=(
                        "Prioritize enrollment conversion through "
                        "targeted follow-up and enrollment journeys."
                    ),
                )
            )

        cards.append(
            IntelligenceCard(
                card_id="ENGAGEMENT-COVERAGE",
                tenant_id=intelligence.tenant_id,
                title="Engagement Coverage",
                priority="low",
                metric="Engagement Rate",
                value=f"{intelligence.engagement_rate:.2f}%",
                evidence=(
                    f"{intelligence.engaged_leads} of "
                    f"{intelligence.total_leads} leads engaged",
                ),
                recommendation=(
                    "Maintain engagement coverage while improving "
                    "down-funnel conversion."
                ),
            )
        )

        return tuple(cards)
