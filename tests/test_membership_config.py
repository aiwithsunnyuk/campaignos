from pathlib import Path

import pytest

from src.identity.membership_config import (
    MembershipConfigError,
    MembershipConfigService,
)


def test_load_reetha_membership(tmp_path: Path):
    config = tmp_path / "memberships.yaml"

    config.write_text(
        """
memberships:
  - identity_email: "Director@Reethaithub.com"
    tenant_id: "reetha"
    role: "director"
    status: "active"
"""
    )

    memberships = MembershipConfigService(config).load()

    assert len(memberships) == 1
    assert memberships[0].identity_id == "email:director@reethaithub.com"
    assert memberships[0].tenant_id == "reetha"
    assert memberships[0].role == "director"
    assert memberships[0].status == "active"


def test_missing_configuration_fails(tmp_path: Path):
    config = tmp_path / "missing.yaml"

    with pytest.raises(MembershipConfigError):
        MembershipConfigService(config).load()


def test_invalid_membership_fails(tmp_path: Path):
    config = tmp_path / "invalid.yaml"

    config.write_text(
        """
memberships:
  - identity_email: "director@reethaithub.com"
    tenant_id: "reetha"
"""
    )

    with pytest.raises(MembershipConfigError):
        MembershipConfigService(config).load()
