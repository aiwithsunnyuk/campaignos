from src.gtm_intelligence.signals import GTMExplainableSignal


class NextBestActionEngine:
    """Deterministic, explainable NBA recommendation engine."""

    def recommend(
        self,
        lead_id: str,
        tenant_id: str,
        signals: list[GTMExplainableSignal],
    ):
        signal_map = {signal.signal_id: signal for signal in signals}

        bottleneck = signal_map.get("FUNNEL_BOTTLENECK")
        engagement = signal_map.get("ENGAGEMENT_COVERAGE")

        evidence = []
        action_type = "monitor"
        priority = "low"
        recommendation = "Monitor lead activity"
        reason = "No strong actionable funnel signal was detected."

        if bottleneck and bottleneck.value == "registration":
            action_type = "registration_follow_up"
            priority = "high"
            recommendation = "Prioritize registration conversion"
            reason = (
                "Registration is the current funnel bottleneck "
                "and should be prioritized for follow-up."
            )
            evidence.append(
                "registration is the current funnel bottleneck"
            )

        elif bottleneck and bottleneck.value == "enrollment":
            action_type = "enrollment_follow_up"
            priority = "high"
            recommendation = "Prioritize enrollment conversion"
            reason = (
                "Enrollment is the current funnel bottleneck "
                "and should be prioritized for follow-up."
            )
            evidence.append(
                "enrollment is the current funnel bottleneck"
            )

        if engagement:
            evidence.append(
                f"engagement coverage is {engagement.level}"
            )

        from .models import NextBestAction

        return NextBestAction(
            lead_id=lead_id,
            tenant_id=tenant_id,
            action_type=action_type,
            priority=priority,
            recommendation=recommendation,
            reason=reason,
            evidence=tuple(evidence),
        )
