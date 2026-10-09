from src.identity.models import Identity, TenantMembership
from src.session.identity_session import (
    IdentitySession,
    identity_session_from_context,
)


def test_identity_session_exposes_identity_and_membership_context():
    identity = Identity(
        identity_id="google:123",
        email="sunnyukdesign@gmail.com",
        display_name="Sunny UK",
        provider="google",
        provider_subject="123",
        verified=True,
    )

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    session = IdentitySession(
        identity=identity,
        membership=membership,
    )

    assert session.user_id == "google:123"
    assert session.email == "sunnyukdesign@gmail.com"
    assert session.display_name == "Sunny UK"
    assert session.tenant_id == "reetha"
    assert session.role == "director"


def test_identity_session_factory_preserves_tenant_and_role():
    identity = Identity(
        identity_id="google:456",
        email="sunnyukdesign@gmail.com",
        display_name="Sunny UK",
        provider="google",
        provider_subject="456",
        verified=True,
    )

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    session = identity_session_from_context(identity, membership)

    assert session.user_id == "google:456"
    assert session.tenant_id == "reetha"
    assert session.role == "director"


def test_identity_session_factory_preserves_tenant_and_role():
    identity = Identity(
        identity_id="google:456",
        email="sunnyukdesign@gmail.com",
        display_name="Sunny UK",
        provider="google",
        provider_subject="456",
        verified=True,
    )

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    session = identity_session_from_context(identity, membership)

    assert session.user_id == "google:456"
    assert session.tenant_id == "reetha"
    assert session.role == "director"
