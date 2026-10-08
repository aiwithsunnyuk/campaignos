from src.ai_governance.action_lifecycle import GovernedAction

from .models import ExecutionResult


class ExecutionBoundaryError(ValueError):
    """Raised when an action is not eligible for execution."""


class DryRunExecutionAdapter:
    """Simulates execution without contacting an external system."""

    def execute(
        self,
        action: GovernedAction,
        execution_id: str,
    ) -> ExecutionResult:
        if action.status != "ready_for_execution":
            raise ExecutionBoundaryError(
                f"Action must be 'ready_for_execution', "
                f"got '{action.status}'."
            )

        return ExecutionResult(
            execution_id=execution_id,
            action_id=action.action_id,
            tenant_id=action.tenant_id,
            status="dry_run",
            action_type=action.action_type,
            message="Dry-run only. No external system was contacted.",
        )
