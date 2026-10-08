from dataclasses import replace

from .models import ApprovalRequest


class ApprovalTransitionError(ValueError):
    """Raised when an approval request attempts an invalid state transition."""


class ApprovalEngine:
    """Controls valid human approval state transitions."""

    def approve(
        self,
        request: ApprovalRequest,
        approved_by: str,
    ) -> ApprovalRequest:
        if request.status != "pending":
            raise ApprovalTransitionError(
                f"Cannot approve request in '{request.status}' state."
            )

        if not approved_by.strip():
            raise ValueError("approved_by is required.")

        return replace(
            request,
            status="approved",
            approved_by=approved_by,
            rejection_reason=None,
        )

    def reject(
        self,
        request: ApprovalRequest,
        rejection_reason: str,
    ) -> ApprovalRequest:
        if request.status != "pending":
            raise ApprovalTransitionError(
                f"Cannot reject request in '{request.status}' state."
            )

        if not rejection_reason.strip():
            raise ValueError("rejection_reason is required.")

        return replace(
            request,
            status="rejected",
            approved_by=None,
            rejection_reason=rejection_reason,
        )
