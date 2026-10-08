from src.next_best_action import NextBestAction

from .action_lifecycle import GovernedAction


class GovernedActionFactory:
    """Converts an explainable NBA into a governed action."""

    def create(
        self,
        action: NextBestAction,
        action_id: str,
    ) -> GovernedAction:
        return GovernedAction(
            action_id=action_id,
            tenant_id=action.tenant_id,
            lead_id=action.lead_id,
            action_type=action.action_type,
            recommendation=action.recommendation,
        )
