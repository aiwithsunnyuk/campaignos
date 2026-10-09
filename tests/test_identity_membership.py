import pytest

from src.identity.models import Identity, TenantMembership
from src.identity.membership import TenantMembershipService
from src.identity.providers import (
    IdentityProviderError,
    build_identity,
)


def make_identity(
    *,
    identity_id="identity-001",
    verified=True,
):
    return Identity(
        identity_id=identity_id,
        email="director@reethaithub.com",
        display_name="Reetha Director",
        provider="work_email",
        provider_subject="subject-001",
        verified=verified,
    )


def test_verified_identity_can_resolve_tenant_membership():
    identity = make_identity()

    membership = TenantMembership(
        identity_id="identity-001",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    service = TenantMembershipService([membership])

    result = service.resolve(identity, "reetha")

    assert result.tenant_id == "reetha"
    assert result.role == "director"


def test_unverified_identity_is_rejected():
    identity = make_identity(verified=False)

    membership = TenantMembership(
        identity_id="identity-001",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    service = TenantMembershipService([membership])

    with pytest.raises(PermissionError):
        service.resolve(identity, "reetha")


def test_identity_without_membership_is_rejected():
    identity = make_identity()

    service = TenantMembershipService([])

    with pytest.raises(PermissionError):
        service.resolve(identity, "reetha")


def test_suspended_membership_is_rejected():
    identity = make_identity()

    membership = TenantMembership(
        identity_id="identity-001",
        tenant_id="reetha",
        role="director",
        status="suspended",
    )

    service = TenantMembershipService([membership])

    with pytest.raises(PermissionError):
        service.resolve(identity, "reetha")


def test_provider_identity_is_normalized():
    identity = build_identity(
        identity_id="google-001",
        email="  Director@Reethaithub.com ",
        display_name=" Reetha Director ",
        provider="google",
        provider_subject="google-subject",
        verified=True,
    )

    assert identity.email == "director@reethaithub.com"
    assert identity.display_name == "Reetha Director"
    assert identity.provider == "google"


def test_unknown_provider_is_rejected():
    with pytest.raises(IdentityProviderError):
        build_identity(
            identity_id="x",
            email="director@example.com",
            display_name="Director",
            provider="unknown",
            provider_subject="subject",
            verified=True,
        )
