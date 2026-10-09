from pathlib import Path

import pytest

from src.identity.access import (
    IdentityAccessError,
    IdentityAccessService,
)
from src.identity.models import Identity


def make_identity(
    email="sunnyukdesign@gmail.com",
    verified=True,
):
    return Identity(
        identity_id="google:test-subject",
        email=email,
        display_name="Sunny UK",
        provider="google",
        provider_subject="test-subject",
        verified=verified,
    )


def make_config(tmp_path: Path, email="sunnyukdesign@gmail.com"):
    path = tmp_path / "memberships.yaml"

    path.write_text(
        f"""
memberships:
  - identity_email: "{email}"
    tenant_id: "reetha"
    role: "director"
    status: "active"
"""
    )

    return path


def test_google_identity_gets_reetha_director_access(tmp_path):
    service = IdentityAccessService(make_config(tmp_path))

    user_id, membership = service.resolve_campaignos_user(
        make_identity(),
        "reetha",
    )

    assert user_id == "reetha-director"
    assert membership.tenant_id == "reetha"
    assert membership.role == "director"


def test_unknown_google_identity_is_denied(tmp_path):
    service = IdentityAccessService(
        make_config(tmp_path, "someoneelse@gmail.com")
    )

    with pytest.raises(IdentityAccessError):
        service.resolve_campaignos_user(
            make_identity(),
            "reetha",
        )


def test_wrong_tenant_is_denied(tmp_path):
    service = IdentityAccessService(make_config(tmp_path))

    with pytest.raises(IdentityAccessError):
        service.resolve_campaignos_user(
            make_identity(),
            "demo",
        )


def test_unmapped_role_is_denied(tmp_path):
    path = tmp_path / "memberships.yaml"

    path.write_text(
        """
memberships:
  - identity_email: "sunnyukdesign@gmail.com"
    tenant_id: "reetha"
    role: "analyst"
    status: "active"
"""
    )

    service = IdentityAccessService(path)

    with pytest.raises(IdentityAccessError):
        service.resolve_campaignos_user(
            make_identity(),
            "reetha",
        )
