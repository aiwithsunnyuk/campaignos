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


def test_approved_request_creates_audit_event():
    from src.ai_governance import ApprovalEngine, AuditRecorder

    request = ApprovalRequest(
        request_id="APR-0020",
        tenant_id="reetha",
        lead_id="LEAD-0020",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=(
            "high engagement coverage",
            "registration is the current funnel bottleneck",
        ),
    )

    approved = ApprovalEngine().approve(
        request,
        approved_by="reetha-director",
    )

    event = AuditRecorder().record(
        request=approved,
        event_id="AUD-0020",
        actor_id="reetha-director",
        timestamp="2026-10-08T22:00:00+05:30",
    )

    assert event.event_id == "AUD-0020"
    assert event.request_id == "APR-0020"
    assert event.tenant_id == "reetha"
    assert event.lead_id == "LEAD-0020"
    assert event.event_type == "approval_approved"
    assert event.actor_id == "reetha-director"
    assert event.decision == "approved"
    assert event.recommendation == approved.recommendation
    assert event.reason == approved.reason
    assert event.evidence == approved.evidence


def test_pending_request_cannot_create_audit_event():
    import pytest
    from src.ai_governance import AuditRecorder

    request = ApprovalRequest(
        request_id="APR-0021",
        tenant_id="reetha",
        lead_id="LEAD-0021",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=("registration bottleneck",),
    )

    with pytest.raises(ValueError):
        AuditRecorder().record(
            request=request,
            event_id="AUD-0021",
            actor_id="system",
            timestamp="2026-10-08T22:00:00+05:30",
        )


def test_reetha_director_can_approve_reetha_request():
    from src.ai_governance import TenantApprovalService
    from src.auth.models import Permission, Role, User

    user = User(
        user_id="reetha-director",
        email="director@reetha.example",
        display_name="Reetha Director",
        tenant_id="reetha",
        role=Role.DIRECTOR,
    )

    request = ApprovalRequest(
        request_id="APR-0030",
        tenant_id="reetha",
        lead_id="LEAD-0030",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=("registration bottleneck",),
    )

    approved = TenantApprovalService().approve(
        user=user,
        request=request,
    )

    assert approved.status == "approved"
    assert approved.approved_by == "reetha-director"


def test_demo_user_cannot_approve_reetha_request():
    import pytest
    from src.ai_governance import TenantApprovalService
    from src.auth.authorization import AuthorizationError
    from src.auth.models import Role, User

    user = User(
        user_id="demo-admin",
        email="admin@demo.example",
        display_name="Demo Admin",
        tenant_id="demo",
        role=Role.ADMIN,
    )

    request = ApprovalRequest(
        request_id="APR-0031",
        tenant_id="reetha",
        lead_id="LEAD-0031",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=("registration bottleneck",),
    )

    with pytest.raises(AuthorizationError, match="Tenant access denied"):
        TenantApprovalService().approve(
            user=user,
            request=request,
        )


def test_reetha_director_can_record_reetha_audit():
    from src.ai_governance import ApprovalEngine, TenantAuditService
    from src.auth.models import Role, User

    user = User(
        user_id="reetha-director",
        email="director@reetha.example",
        display_name="Reetha Director",
        tenant_id="reetha",
        role=Role.DIRECTOR,
    )

    request = ApprovalRequest(
        request_id="APR-0040",
        tenant_id="reetha",
        lead_id="LEAD-0040",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=("registration bottleneck",),
    )

    approved = ApprovalEngine().approve(
        request=request,
        approved_by=user.user_id,
    )

    event = TenantAuditService().record(
        user=user,
        request=approved,
        event_id="AUD-0040",
        timestamp="2026-10-08T23:00:00+05:30",
    )

    assert event.tenant_id == "reetha"
    assert event.request_id == "APR-0040"
    assert event.actor_id == "reetha-director"
    assert event.decision == "approved"


def test_demo_admin_cannot_record_reetha_audit():
    import pytest
    from src.ai_governance import ApprovalEngine, TenantAuditService
    from src.auth.authorization import AuthorizationError
    from src.auth.models import Role, User

    user = User(
        user_id="demo-admin",
        email="admin@demo.example",
        display_name="Demo Admin",
        tenant_id="demo",
        role=Role.ADMIN,
    )

    request = ApprovalRequest(
        request_id="APR-0041",
        tenant_id="reetha",
        lead_id="LEAD-0041",
        action_type="registration_follow_up",
        recommendation="Prioritize registration conversion",
        reason="Registration is the current funnel bottleneck.",
        evidence=("registration bottleneck",),
    )

    approved = ApprovalEngine().approve(
        request=request,
        approved_by="reetha-director",
    )

    with pytest.raises(AuthorizationError, match="Tenant access denied"):
        TenantAuditService().record(
            user=user,
            request=approved,
            event_id="AUD-0041",
            timestamp="2026-10-08T23:00:00+05:30",
        )
