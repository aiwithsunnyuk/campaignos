from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ObservationSeverity(str, Enum):
    INFO = "Info"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DecisionStatus(str, Enum):
    PROPOSED = "Proposed"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXECUTED = "Executed"


@dataclass
class AgentRequest:
    campaign_id: str
    campaign_name: str
    business_type: str
    region: str
    objective: str
    context: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.campaign_id:
            errors.append("Campaign ID is required.")
        if not self.campaign_name:
            errors.append("Campaign name is required.")
        if not self.business_type:
            errors.append("Business type is required.")
        if not self.region:
            errors.append("Region is required.")
        if not self.objective:
            errors.append("Campaign objective is required.")

        return errors


@dataclass
class AgentObservation:
    observation_id: str
    category: str
    title: str
    description: str
    severity: ObservationSeverity = ObservationSeverity.INFO
    evidence: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.observation_id:
            errors.append("Observation ID is required.")
        if not self.category:
            errors.append("Observation category is required.")
        if not self.title:
            errors.append("Observation title is required.")
        if not self.description:
            errors.append("Observation description is required.")

        return errors


@dataclass
class AgentAction:
    action_type: str
    title: str
    description: str
    priority: int = 3
    owner: str = "Marketing Operations"
    parameters: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.action_type:
            errors.append("Action type is required.")
        if not self.title:
            errors.append("Action title is required.")
        if not self.description:
            errors.append("Action description is required.")
        if self.priority < 1 or self.priority > 5:
            errors.append("Action priority must be between 1 and 5.")

        return errors


@dataclass
class AgentDecision:
    decision_id: str
    action: AgentAction
    reason: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    status: DecisionStatus = DecisionStatus.PROPOSED

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.decision_id:
            errors.append("Decision ID is required.")
        if not self.reason:
            errors.append("Decision reason is required.")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("Decision confidence must be between 0 and 1.")
        errors.extend(self.action.validate())

        return errors


@dataclass
class AgentPlan:
    plan_id: str
    campaign_id: str
    summary: str
    decisions: List[AgentDecision] = field(default_factory=list)
    generated_by: str = "CampaignOS Agent"
    requires_human_approval: bool = True

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.plan_id:
            errors.append("Plan ID is required.")
        if not self.campaign_id:
            errors.append("Campaign ID is required.")
        if not self.summary:
            errors.append("Plan summary is required.")

        for decision in self.decisions:
            errors.extend(decision.validate())

        return errors

    @property
    def action_count(self) -> int:
        return len(self.decisions)
