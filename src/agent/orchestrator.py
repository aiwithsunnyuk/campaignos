from __future__ import annotations

from typing import Mapping

from .analyzer import CampaignIntelligenceAnalyzer
from .decision_engine import CampaignDecisionEngine
from .models import AgentPlan, AgentRequest


class CampaignAgentOrchestrator:
    """Coordinate campaign analysis and decision generation into one agent plan."""

    def __init__(
        self,
        analyzer: CampaignIntelligenceAnalyzer | None = None,
        decision_engine: CampaignDecisionEngine | None = None,
    ) -> None:
        self.analyzer = analyzer or CampaignIntelligenceAnalyzer()
        self.decision_engine = decision_engine or CampaignDecisionEngine()

    def run(
        self,
        request: AgentRequest,
        context: Mapping[str, object],
    ) -> AgentPlan:
        request.validate()

        observations = self.analyzer.analyze(
            request.campaign_id,
            dict(context),
        )
        decisions = self.decision_engine.decide(observations)

        plan = AgentPlan(
            plan_id=f"PLAN-{request.campaign_id}",
            campaign_id=request.campaign_id,
            summary=self._build_summary(
                request,
                len(observations),
                len(decisions),
            ),
            decisions=decisions,
            generated_by="CampaignOS Agent",
            requires_human_approval=True,
        )
        plan.validate()
        return plan

    @staticmethod
    def _build_summary(
        request: AgentRequest,
        observation_count: int,
        decision_count: int,
    ) -> str:
        if decision_count == 0:
            outcome = "No actionable decisions were generated from the supplied signals."
        elif decision_count == 1:
            outcome = "One actionable decision was generated for human review."
        else:
            outcome = (
                f"{decision_count} actionable decisions were generated "
                "for human review."
            )

        return (
            f"Campaign '{request.campaign_name}' was analyzed using supplied "
            f"CampaignOS signals. {observation_count} observation(s) were evaluated. "
            f"{outcome}"
        )
