from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, List, Optional

from .models import AgentDecision, AgentPlan, DecisionStatus


class ApprovalStatus(str, Enum):
    """Human review state for an agent decision."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


@dataclass(frozen=True)
class ApprovalRecord:
    """Audit-friendly record of a human review action."""

    decision_id: str
    status: ApprovalStatus
    reviewer: str
    comment: str = ""
    reviewed_at: str = ""

    def validate(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id is required")
        if not self.reviewer.strip():
            raise ValueError("reviewer is required")
        if not isinstance(self.status, ApprovalStatus):
            raise ValueError("status must be an ApprovalStatus")

    @classmethod
    def create(
        cls,
        decision_id: str,
        status: ApprovalStatus,
        reviewer: str,
        comment: str = "",
    ) -> "ApprovalRecord":
        record = cls(
            decision_id=decision_id,
            status=status,
            reviewer=reviewer,
            comment=comment,
            reviewed_at=datetime.now(timezone.utc).isoformat(),
        )
        record.validate()
        return record


@dataclass(frozen=True)
class ExecutionAction:
    """Execution-ready representation of an approved agent action."""

    decision_id: str
    action_type: str
    title: str
    description: str
    priority: int
    owner: str
    parameters: dict

    def validate(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id is required")
        if not self.action_type:
            raise ValueError("action_type is required")
        if not self.title:
            raise ValueError("title is required")
        if not 1 <= self.priority <= 5:
            raise ValueError("priority must be between 1 and 5")


@dataclass(frozen=True)
class HumanApprovedActionPlan:
    """Controlled action plan produced after human review."""

    plan_id: str
    campaign_id: str
    status: ApprovalStatus
    actions: List[ExecutionAction]
    rejected_decision_ids: List[str]
    reviewer: str
    summary: str
    source_plan_id: str

    @property
    def action_count(self) -> int:
        return len(self.actions)

    @property
    def ready_for_execution(self) -> bool:
        return self.status == ApprovalStatus.APPROVED and bool(self.actions)

    def validate(self) -> None:
        if not self.plan_id:
            raise ValueError("plan_id is required")
        if not self.campaign_id:
            raise ValueError("campaign_id is required")
        if not self.source_plan_id:
            raise ValueError("source_plan_id is required")
        if not self.reviewer.strip():
            raise ValueError("reviewer is required")
        for action in self.actions:
            action.validate()


class HumanApprovalService:
    """Human-in-the-loop review and execution-plan builder.

    This service never sends emails, updates CRM records, or calls external
    systems. It only changes the in-memory decision state and creates an
    execution-ready plan for a later controlled integration.
    """

    def review(
        self,
        decision: AgentDecision,
        approve: bool,
        reviewer: str,
        comment: str = "",
    ) -> tuple[AgentDecision, ApprovalRecord]:
        if not reviewer.strip():
            raise ValueError("reviewer is required")

        status = (
            DecisionStatus.APPROVED
            if approve
            else DecisionStatus.REJECTED
        )
        approval_status = (
            ApprovalStatus.APPROVED
            if approve
            else ApprovalStatus.REJECTED
        )

        updated = replace(decision, status=status)
        record = ApprovalRecord.create(
            decision_id=decision.decision_id,
            status=approval_status,
            reviewer=reviewer,
            comment=comment,
        )
        return updated, record

    def build_action_plan(
        self,
        plan: AgentPlan,
        reviewed_decisions: Iterable[AgentDecision],
        reviewer: str,
        summary: Optional[str] = None,
    ) -> HumanApprovedActionPlan:
        if not reviewer.strip():
            raise ValueError("reviewer is required")

        reviewed = list(reviewed_decisions)
        expected_ids = {decision.decision_id for decision in plan.decisions}
        actual_ids = {decision.decision_id for decision in reviewed}

        if actual_ids != expected_ids:
            missing = sorted(expected_ids - actual_ids)
            unexpected = sorted(actual_ids - expected_ids)
            details = []
            if missing:
                details.append(f"missing={missing}")
            if unexpected:
                details.append(f"unexpected={unexpected}")
            raise ValueError(
                "reviewed decisions must exactly match the source plan: "
                + ", ".join(details)
            )

        approved = [
            decision
            for decision in reviewed
            if decision.status == DecisionStatus.APPROVED
        ]
        rejected = [
            decision.decision_id
            for decision in reviewed
            if decision.status == DecisionStatus.REJECTED
        ]

        actions = [
            ExecutionAction(
                decision_id=decision.decision_id,
                action_type=decision.action.action_type,
                title=decision.action.title,
                description=decision.action.description,
                priority=decision.action.priority,
                owner=decision.action.owner,
                parameters=dict(decision.action.parameters),
            )
            for decision in approved
        ]

        if approved and not rejected:
            status = ApprovalStatus.APPROVED
        elif approved and rejected:
            status = ApprovalStatus.PENDING
        else:
            status = ApprovalStatus.REJECTED

        action_plan = HumanApprovedActionPlan(
            plan_id=f"{plan.plan_id}-EXEC",
            campaign_id=plan.campaign_id,
            status=status,
            actions=actions,
            rejected_decision_ids=rejected,
            reviewer=reviewer,
            summary=summary or plan.summary,
            source_plan_id=plan.plan_id,
        )
        action_plan.validate()
        return action_plan
