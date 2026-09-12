"""M10.7 safety and validation helpers for CampaignOS agent plans."""
from __future__ import annotations

from typing import Iterable
from .models import AgentDecision, AgentPlan, DecisionStatus


def clamp_confidence(value: float) -> float:
    """Constrain confidence to the supported 0..1 range."""
    return max(0.0, min(1.0, float(value)))


def validate_decisions(decisions: Iterable[AgentDecision]) -> list[AgentDecision]:
    """Validate decisions using the existing domain model."""
    validated = list(decisions)
    for decision in validated:
        decision.validate()
    return validated


def execution_readiness(plan: AgentPlan) -> bool:
    """True only when every decision has been explicitly approved."""
    plan.validate()
    if not plan.decisions:
        return False
    return all(
        decision.status == DecisionStatus.APPROVED
        for decision in plan.decisions
    )


def rejection_count(plan: AgentPlan) -> int:
    plan.validate()
    return sum(
        decision.status == DecisionStatus.REJECTED
        for decision in plan.decisions
    )


def approval_count(plan: AgentPlan) -> int:
    plan.validate()
    return sum(
        decision.status == DecisionStatus.APPROVED
        for decision in plan.decisions
    )
