from src.auth.authorization import authorize
from src.auth.models import Permission, User
from src.next_best_action.models import NextBestAction

from .action_factory import GovernedActionFactory
from .action_lifecycle import GovernedAction
from .action_lifecycle_engine import ActionLifecycleEngine
from .models import ApprovalRequest
from .request_factory import ApprovalRequestFactory
from .tenant_approval import TenantApprovalService


class LeadActionGovernanceService:
    """Tenant-safe bridge from lead NBA to governed approval."""

    def __init__(self) -> None:
        self._lifecycle = ActionLifecycleEngine()
        self._approval = TenantApprovalService()

    def create_governed_action(
        self,
        user: User,
        action: NextBestAction,
    ) -> GovernedAction:
        authorize(
            user=user,
            permission=Permission.GENERATE_AI_RECOMMENDATION,
            resource_tenant_id=action.tenant_id,
        )

        governed_action = GovernedActionFactory().create(
            action=action,
            action_id=f"ACT-{action.tenant_id.upper()}-{action.lead_id}",
        )

        return self._lifecycle.submit_for_approval(governed_action)

    def create_approval_request(
        self,
        user: User,
        action: NextBestAction,
    ) -> ApprovalRequest:
        authorize(
            user=user,
            permission=Permission.GENERATE_AI_RECOMMENDATION,
            resource_tenant_id=action.tenant_id,
        )

        return ApprovalRequestFactory().create(
            action=action,
            request_id=f"APR-{action.tenant_id.upper()}-{action.lead_id}",
        )

    def approve_action(
        self,
        user: User,
        action: GovernedAction,
    ) -> GovernedAction:
        authorize(
            user=user,
            permission=Permission.APPROVE_AI_ACTION,
            resource_tenant_id=action.tenant_id,
        )

        return self._lifecycle.approve(
            action=action,
            approved_by=user.user_id,
        )

    def reject_action(
        self,
        user: User,
        action: GovernedAction,
    ) -> GovernedAction:
        authorize(
            user=user,
            permission=Permission.APPROVE_AI_ACTION,
            resource_tenant_id=action.tenant_id,
        )

        return self._lifecycle.reject(action=action)

    def prepare_for_execution(
        self,
        user: User,
        action: GovernedAction,
    ) -> GovernedAction:
        authorize(
            user=user,
            permission=Permission.APPROVE_AI_ACTION,
            resource_tenant_id=action.tenant_id,
        )

        return self._lifecycle.mark_ready_for_execution(action)

    def dry_run_ready_action(
        self,
        user: User,
        action: GovernedAction,
    ) -> GovernedAction:
        authorize(
            user=user,
            permission=Permission.EXECUTE_CAMPAIGN,
            resource_tenant_id=action.tenant_id,
        )

        return action
