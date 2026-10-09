import pytest

from src.identity.oidc import (
    OIDCIdentityError,
    identity_from_streamlit_user,
)


class FakeUser:
    email = "Director@Reethaithub.com"
    name = "Reetha Director"
    sub = "google-subject-001"
    provider = "google"


def test_oidc_user_becomes_campaignos_identity():
    identity = identity_from_streamlit_user(FakeUser())

    assert identity.identity_id == "google:google-subject-001"
    assert identity.email == "director@reethaithub.com"
    assert identity.display_name == "Reetha Director"
    assert identity.provider == "google"
    assert identity.verified is True


def test_oidc_requires_email():
    class UserWithoutEmail:
        name = "Unknown"
        sub = "subject"

    with pytest.raises(OIDCIdentityError):
        identity_from_streamlit_user(UserWithoutEmail())


def test_oidc_falls_back_to_email_for_subject():
    class UserWithEmailOnly:
        email = "director@reethaithub.com"
        name = "Reetha Director"

    identity = identity_from_streamlit_user(UserWithEmailOnly())

    assert identity.provider == "oidc"
    assert identity.provider_subject == "director@reethaithub.com"
