from __future__ import annotations

from typing import Iterable, List

from .models import AgentAction, AgentDecision, AgentObservation, ObservationSeverity


class CampaignDecisionEngine:
    """Deterministic, explainable decision engine for campaign observations."""

    _SEVERITY_PRIORITY = {
        ObservationSeverity.CRITICAL: 1,
        ObservationSeverity.HIGH: 1,
        ObservationSeverity.MEDIUM: 2,
        ObservationSeverity.LOW: 3,
        ObservationSeverity.INFO: 5,
    }

    def decide(self, observations: Iterable[AgentObservation]) -> List[AgentDecision]:
        decisions: List[AgentDecision] = []

        for index, observation in enumerate(observations, start=1):
            action = self._action_for(observation)
            if action is None:
                continue

            decisions.append(
                AgentDecision(
                    decision_id=f"DEC-{index:03d}",
                    action=action,
                    reason=observation.description,
                    evidence=observation.evidence,
                    confidence=self._confidence(observation),
                )
            )

        return decisions

    def _action_for(self, observation: AgentObservation) -> AgentAction | None:
        text = " ".join(
            [
                observation.category or "",
                observation.title or "",
                observation.description or "",
            ]
        ).lower()

        priority = self._SEVERITY_PRIORITY.get(observation.severity, 3)

        if "conversion" in text:
            return AgentAction(
                action_type="OPTIMIZE_CONVERSION_PATH",
                title="Review conversion path",
                description=(
                    "Review the campaign landing page, form friction, offer, "
                    "CTA alignment, and post-click experience before increasing traffic."
                ),
                priority=priority,
                parameters={"focus": "conversion_rate"},
            )

        if "open rate" in text or "opens" in text:
            return AgentAction(
                action_type="OPTIMIZE_EMAIL_ENGAGEMENT",
                title="Optimize email engagement",
                description=(
                    "Test subject lines, sender positioning, send timing, and audience "
                    "selection before scaling the campaign."
                ),
                priority=priority,
                parameters={"focus": "open_rate"},
            )

        if "click rate" in text or "clicks" in text:
            return AgentAction(
                action_type="OPTIMIZE_CTA",
                title="Optimize CTA performance",
                description=(
                    "Review message-to-CTA alignment, CTA placement, offer clarity, "
                    "and landing-page continuity."
                ),
                priority=priority,
                parameters={"focus": "click_rate"},
            )

        if "mql" in text or "marketable" in text:
            return AgentAction(
                action_type="REFINE_AUDIENCE",
                title="Refine campaign audience",
                description=(
                    "Review segmentation, consent eligibility, lifecycle stage, and "
                    "marketable audience coverage before expanding campaign reach."
                ),
                priority=priority,
                parameters={"focus": "audience_quality"},
            )

        if "lead score" in text or "intent" in text:
            return AgentAction(
                action_type="PRIORITIZE_HIGH_INTENT_LEADS",
                title="Prioritize high-intent leads",
                description=(
                    "Route attention toward higher-scoring contacts and align follow-up "
                    "with the campaign's lifecycle and sales-handoff strategy."
                ),
                priority=priority,
                parameters={"focus": "lead_score"},
            )

        return None

    @staticmethod
    def _confidence(observation: AgentObservation) -> float:
        mapping = {
            ObservationSeverity.CRITICAL: 0.98,
            ObservationSeverity.HIGH: 0.92,
            ObservationSeverity.MEDIUM: 0.84,
            ObservationSeverity.LOW: 0.76,
            ObservationSeverity.INFO: 0.70,
        }
        return mapping.get(observation.severity, 0.70)
