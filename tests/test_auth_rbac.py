from src.auth import Permission, Role, User, has_permission


def test_reetha_marketing_manager_can_manage_campaigns():
    assert has_permission(
        Role.MARKETING_MANAGER,
        Permission.MANAGE_CAMPAIGNS,
    )


def test_reetha_marketing_manager_can_generate_ai_recommendations():
    assert has_permission(
        Role.MARKETING_MANAGER,
        Permission.GENERATE_AI_RECOMMENDATION,
    )


def test_marketing_manager_cannot_execute_campaign():
    assert not has_permission(
        Role.MARKETING_MANAGER,
        Permission.EXECUTE_CAMPAIGN,
    )


def test_director_can_approve_ai_action():
    assert has_permission(
        Role.DIRECTOR,
        Permission.APPROVE_AI_ACTION,
    )


def test_viewer_is_read_only():
    assert has_permission(
        Role.VIEWER,
        Permission.VIEW_DASHBOARD,
    )

    assert not has_permission(
        Role.VIEWER,
        Permission.MANAGE_CAMPAIGNS,
    )


def test_user_contains_tenant_context():
    user = User(
        user_id="reetha-user-001",
        email="marketing@example.com",
        display_name="Reetha Marketing Manager",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    assert user.tenant_id == "reetha"
    assert user.role == Role.MARKETING_MANAGER
    assert user.active


def test_user_can_access_own_tenant():
    from src.auth import authorize

    user = User(
        user_id="reetha-user-001",
        email="marketing@example.com",
        display_name="Reetha Marketing Manager",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    authorize(
        user,
        Permission.VIEW_LEADS,
        "reetha",
    )


def test_user_cannot_access_another_tenant():
    import pytest
    from src.auth import AuthorizationError, authorize

    user = User(
        user_id="reetha-user-001",
        email="marketing@example.com",
        display_name="Reetha Marketing Manager",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
    )

    with pytest.raises(
        AuthorizationError,
        match="Tenant access denied",
    ):
        authorize(
            user,
            Permission.VIEW_LEADS,
            "demo",
        )


def test_inactive_user_is_rejected():
    import pytest
    from src.auth import AuthorizationError, authorize

    user = User(
        user_id="reetha-user-002",
        email="inactive@example.com",
        display_name="Inactive User",
        tenant_id="reetha",
        role=Role.MARKETING_MANAGER,
        active=False,
    )

    with pytest.raises(
        AuthorizationError,
        match="User is inactive",
    ):
        authorize(
            user,
            Permission.VIEW_LEADS,
            "reetha",
        )


def test_user_without_permission_is_rejected():
    import pytest
    from src.auth import AuthorizationError, authorize

    user = User(
        user_id="reetha-user-003",
        email="viewer@example.com",
        display_name="Reetha Viewer",
        tenant_id="reetha",
        role=Role.VIEWER,
    )

    with pytest.raises(
        AuthorizationError,
        match="Permission denied",
    ):
        authorize(
            user,
            Permission.MANAGE_CAMPAIGNS,
            "reetha",
        )


def test_reetha_director_resolves_to_reetha_tenant():
    from src.auth import get_user

    user = get_user("reetha-director")

    assert user.tenant_id == "reetha"
    assert user.role == Role.DIRECTOR


def test_reetha_marketing_user_resolves_correctly():
    from src.auth import get_user

    user = get_user("reetha-marketing")

    assert user.tenant_id == "reetha"
    assert user.role == Role.MARKETING_MANAGER


def test_reetha_sales_user_resolves_correctly():
    from src.auth import get_user

    user = get_user("reetha-sales")

    assert user.tenant_id == "reetha"
    assert user.role == Role.SALES_USER


def test_unknown_user_is_rejected():
    import pytest
    from src.auth import get_user

    with pytest.raises(ValueError, match="Unknown CampaignOS user"):
        get_user("does-not-exist")


def test_user_registry_contains_multiple_tenants():
    from src.auth import list_users

    users = list_users()
    tenant_ids = {user.tenant_id for user in users}

    assert "demo" in tenant_ids
    assert "reetha" in tenant_ids
