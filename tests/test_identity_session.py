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


def test_identity_session_can_create_authenticated_workspace():
    from src.workspace.service import workspace_from_identity_session

    identity = Identity(
        identity_id="google:789",
        email="sunnyukdesign@gmail.com",
        display_name="Sunny UK",
        provider="google",
        provider_subject="789",
        verified=True,
    )

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    session = IdentitySession(identity=identity, membership=membership)
    workspace = workspace_from_identity_session(session)

    assert workspace.tenant_id == "reetha"
    assert workspace.user_id == "google:789"
    assert workspace.display_name == "Sunny UK"
    assert workspace.role == "director"
    assert workspace.authenticated is True


def test_identity_session_can_create_streamlit_compatible_session():
    from src.session.streamlit_session import sign_in_identity
    from src.session.models import AuthenticatedSession

    identity = Identity(
        identity_id="google:streamlit-123",
        email="sunnyukdesign@gmail.com",
        display_name="Sunny UK",
        provider="google",
        provider_subject="streamlit-123",
        verified=True,
    )

    membership = TenantMembership(
        identity_id="email:sunnyukdesign@gmail.com",
        tenant_id="reetha",
        role="director",
        status="active",
    )

    identity_session = IdentitySession(
        identity=identity,
        membership=membership,
    )

    session = sign_in_identity(identity_session)

    assert isinstance(session, AuthenticatedSession)
    assert session.user_id == "google:streamlit-123"
    assert session.email == "sunnyukdesign@gmail.com"
    assert session.tenant_id == "reetha"
    assert session.role == "director"
