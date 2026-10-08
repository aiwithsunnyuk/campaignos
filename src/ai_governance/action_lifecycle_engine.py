from dataclasses import replace

from .action_lifecycle import GovernedAction


class ActionLifecycleError(ValueError):
    """Raised when an invalid governed-action transition is attempted."""


class ActionLifecycleEngine:
    """Controls the lifecycle of governed AI actions."""

    def submit_for_approval(
        self,
        action: GovernedAction,
    ) -> GovernedAction:
        if action.status != "recommended":
            raise ActionLifecycleError(
                f"Cannot submit action in '{action.status}' state."
            )

        return replace(
            action,
            status="pending_approval",
        )

    def approve(
        self,
        action: GovernedAction,
        approved_by: str,
    ) -> GovernedAction:
        if action.status != "pending_approval":
            raise ActionLifecycleError(
                f"Cannot approve action in '{action.status}' state."
            )

        if not approved_by.strip():
            raise ValueError("approved_by is required.")

        return replace(
            action,
            status="approved",
            approved_by=approved_by,
        )

    def reject(
        self,
        action: GovernedAction,
    ) -> GovernedAction:
        if action.status != "pending_approval":
            raise ActionLifecycleError(
                f"Cannot reject action in '{action.status}' state."
            )

        return replace(
            action,
            status="rejected",
        )

    def mark_ready_for_execution(
        self,
        action: GovernedAction,
    ) -> GovernedAction:
        if action.status != "approved":
            raise ActionLifecycleError(
                f"Cannot prepare action in '{action.status}' state."
            )

        return replace(
            action,
            status="ready_for_execution",
        )

    def mark_executed(
        self,
        action: GovernedAction,
        executed_by: str,
    ) -> GovernedAction:
        if action.status != "ready_for_execution":
            raise ActionLifecycleError(
                f"Cannot execute action in '{action.status}' state."
            )

        if not executed_by.strip():
            raise ValueError("executed_by is required.")

        return replace(
            action,
            status="executed",
            executed_by=executed_by,
        )
