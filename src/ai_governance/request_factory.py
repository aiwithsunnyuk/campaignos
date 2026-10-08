from src.next_best_action import NextBestAction

from .models import ApprovalRequest


class ApprovalRequestFactory:
    """Converts a Next Best Action into a governed approval request."""

    def create(
        self,
        action: NextBestAction,
        request_id: str,
    ) -> ApprovalRequest:
        return ApprovalRequest(
            request_id=request_id,
            tenant_id=action.tenant_id,
            lead_id=action.lead_id,
            action_type=action.action_type,
            recommendation=action.recommendation,
            reason=action.reason,
            evidence=action.evidence,
        )
