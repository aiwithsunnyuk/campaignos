from dataclasses import dataclass
from typing import Tuple

from .models import GTMIntelligenceSnapshot


@dataclass(frozen=True)
class GTMExplainableSignal:
    signal_id: str
    name: str
    category: str
    level: str
    value: str
    evidence: str


class GTMExplainableSignalBuilder:
    """Derives explainable GTM signals from an existing factual snapshot."""

    def __init__(self, snapshot: GTMIntelligenceSnapshot):
        self.snapshot = snapshot

    def build(self) -> Tuple[GTMExplainableSignal, ...]:
        signals = [
            self._engagement_signal(),
            self._registration_signal(),
            self._enrollment_signal(),
            self._recency_signal(),
            self._channel_signal(),
            self._funnel_signal(),
        ]

        return tuple(signals)

    def _engagement_signal(self) -> GTMExplainableSignal:
        total = self.snapshot.total_leads
        engaged = self.snapshot.leads_with_engagement
        rate = (engaged / total * 100) if total else 0.0

        if rate >= 80:
            level = "strong"
        elif rate >= 50:
            level = "moderate"
        else:
            level = "weak"

        return GTMExplainableSignal(
            signal_id="ENGAGEMENT_COVERAGE",
            name="Engagement coverage",
            category="engagement",
            level=level,
            value=f"{rate:.1f}%",
            evidence=f"{engaged} of {total} leads have engagement activity",
        )

    def _registration_signal(self) -> GTMExplainableSignal:
        total = self.snapshot.total_leads
        registered = self.snapshot.leads_with_registration
        rate = (registered / total * 100) if total else 0.0

        if rate >= 40:
            level = "strong"
        elif rate >= 20:
            level = "moderate"
        else:
            level = "weak"

        return GTMExplainableSignal(
            signal_id="REGISTRATION_CONVERSION",
            name="Registration conversion",
            category="funnel",
            level=level,
            value=f"{rate:.1f}%",
            evidence=f"{registered} of {total} leads have registered",
        )

    def _enrollment_signal(self) -> GTMExplainableSignal:
        total = self.snapshot.total_leads
        enrolled = self.snapshot.leads_with_enrollment
        rate = (enrolled / total * 100) if total else 0.0

        if rate >= 20:
            level = "strong"
        elif rate >= 10:
            level = "moderate"
        else:
            level = "weak"

        return GTMExplainableSignal(
            signal_id="ENROLLMENT_CONVERSION",
            name="Enrollment conversion",
            category="funnel",
            level=level,
            value=f"{rate:.1f}%",
            evidence=f"{enrolled} of {total} leads have enrolled",
        )

    def _recency_signal(self) -> GTMExplainableSignal:
        distribution = dict(self.snapshot.recency_distribution)

        recent = distribution.get("recent", 0)
        aging = distribution.get("aging", 0)
        stale = distribution.get("stale", 0)
        never = distribution.get("never", 0)

        active = recent + aging

        if active > stale + never:
            level = "strong"
        elif recent > 0:
            level = "moderate"
        else:
            level = "weak"

        return GTMExplainableSignal(
            signal_id="ENGAGEMENT_RECENCY",
            name="Engagement recency",
            category="recency",
            level=level,
            value=f"{recent} recent",
            evidence=(
                f"{recent} recent, {aging} aging, "
                f"{stale} stale, {never} never engaged"
            ),
        )

    def _channel_signal(self) -> GTMExplainableSignal:
        channels = dict(self.snapshot.channel_coverage)
        count = len(channels)

        if count >= 4:
            level = "strong"
        elif count >= 2:
            level = "moderate"
        else:
            level = "weak"

        return GTMExplainableSignal(
            signal_id="CHANNEL_BREADTH",
            name="Channel breadth",
            category="reach",
            level=level,
            value=str(count),
            evidence=f"{count} engagement channels are represented",
        )

    def _funnel_signal(self) -> GTMExplainableSignal:
        funnel = dict(self.snapshot.funnel_progression)

        engaged = funnel.get("Engaged", 0)
        registered = funnel.get("Registered", 0)
        enrolled = funnel.get("Enrolled", 0)

        if engaged:
            registration_rate = registered / engaged * 100
        else:
            registration_rate = 0.0

        if registered:
            enrollment_rate = enrolled / registered * 100
        else:
            enrollment_rate = 0.0

        if registration_rate <= enrollment_rate:
            bottleneck = "registration"
        else:
            bottleneck = "enrollment"

        return GTMExplainableSignal(
            signal_id="FUNNEL_BOTTLENECK",
            name="Funnel bottleneck",
            category="funnel",
            level="attention",
            value=bottleneck,
            evidence=(
                f"Engaged→Registered: {registration_rate:.1f}%; "
                f"Registered→Enrolled: {enrollment_rate:.1f}%"
            ),
        )
