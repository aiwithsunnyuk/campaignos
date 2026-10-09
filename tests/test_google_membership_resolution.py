import pytest

from src.identity.models import Identity, TenantMembership
from src.identity.membership import TenantMembershipService


def google_identity(
    email="sunnyukdesign@gmail.com",
    verified=True,
):
    return Identity(
        identity_id="google:123456789",
        email=email,
        display_name="Sunny UK",
        provider="google",
        provider_subject="123456789",
        verified=verified,
    )


def test_google_identity_resolves_reetha_membership():
    identity = google_identity()

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    service = TenantMembershipService([membership])

    result = service.resolve(identity, "reetha")

    assert result.tenant_id == "reetha"
    assert result.role == "director"


def test_google_identity_without_membership_is_denied():
    identity = google_identity()

    service = TenantMembershipService([])

    with pytest.raises(PermissionError):
        service.resolve(identity, "reetha")


def test_google_identity_for_wrong_email_is_denied():
    identity = google_identity(
        email="another.user@gmail.com",
    )

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    service = TenantMembershipService([membership])

    with pytest.raises(PermissionError):
        service.resolve(identity, "reetha")


def test_unverified_google_identity_is_denied():
    identity = google_identity(verified=False)

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    service = TenantMembershipService([membership])

    with pytest.raises(PermissionError):
        service.resolve(identity, "reetha")
