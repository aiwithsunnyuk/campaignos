from src.ai_governance import ApprovalRequest


def test_approval_request_defaults_to_pending():
    request = ApprovalRequest(
        request_id="APR-0001",
        tenant_id="reetha",
        lead_id="LEAD-0001",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=(
            "high engagement coverage",
            "registration is the current funnel bottleneck",
        ),
    )

    assert request.status == "pending"
    assert request.approved_by is None
    assert request.rejection_reason is None


def test_pending_request_can_be_approved():
    from src.ai_governance import ApprovalEngine

    request = ApprovalRequest(
        request_id="APR-0002",
        tenant_id="reetha",
        lead_id="LEAD-0002",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the funnel bottleneck.",
        evidence=("registration bottleneck",),
    )

    approved = ApprovalEngine().approve(
        request,
        approved_by="reetha-director",
    )

    assert request.status == "pending"
    assert approved.status == "approved"
    assert approved.approved_by == "reetha-director"
    assert approved.rejection_reason is None


def test_pending_request_can_be_rejected():
    from src.ai_governance import ApprovalEngine

    request = ApprovalRequest(
        request_id="APR-0003",
        tenant_id="reetha",
        lead_id="LEAD-0003",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the funnel bottleneck.",
        evidence=("registration bottleneck",),
    )

    rejected = ApprovalEngine().reject(
        request,
        rejection_reason="Campaign requires additional review.",
    )

    assert request.status == "pending"
    assert rejected.status == "rejected"
    assert rejected.rejection_reason == "Campaign requires additional review."
    assert rejected.approved_by is None


def test_rejected_request_cannot_be_approved():
    import pytest
    from src.ai_governance import ApprovalEngine, ApprovalTransitionError

    request = ApprovalRequest(
        request_id="APR-0004",
        tenant_id="reetha",
        lead_id="LEAD-0004",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the funnel bottleneck.",
        evidence=("registration bottleneck",),
        status="rejected",
        rejection_reason="Not approved.",
    )

    with pytest.raises(ApprovalTransitionError):
        ApprovalEngine().approve(
            request,
            approved_by="reetha-director",
        )


def test_approved_request_cannot_be_rejected():
    import pytest
    from src.ai_governance import ApprovalEngine, ApprovalTransitionError

    request = ApprovalRequest(
        request_id="APR-0005",
        tenant_id="reetha",
        lead_id="LEAD-0005",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the funnel bottleneck.",
        evidence=("registration bottleneck",),
        status="approved",
        approved_by="reetha-director",
    )

    with pytest.raises(ApprovalTransitionError):
        ApprovalEngine().reject(
            request,
            rejection_reason="Changed my mind.",
        )


def test_nba_can_be_converted_to_pending_approval_request():
    from src.ai_governance import ApprovalRequestFactory
    from src.next_best_action import NextBestAction

    action = NextBestAction(
        lead_id="LEAD-0010",
        tenant_id="reetha",
        action_type="registration_follow_up",
        priority="high",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=(
            "high engagement coverage",
            "registration is the current funnel bottleneck",
        ),
    )

    request = ApprovalRequestFactory().create(
        action=action,
        request_id="APR-0010",
    )

    assert request.request_id == "APR-0010"
    assert request.tenant_id == "reetha"
    assert request.lead_id == "LEAD-0010"
    assert request.action_type == "registration_follow_up"
    assert request.status == "pending"
    assert request.approved_by is None
    assert request.rejection_reason is None
    assert request.evidence == action.evidence
