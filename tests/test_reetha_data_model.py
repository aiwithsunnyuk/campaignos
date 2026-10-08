from pathlib import Path


def test_reetha_data_model_documentation_exists():
    path = Path("docs/M12_REETHA_DATA_MODEL.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "Courses" in content
    assert "Campaigns" in content
    assert "Leads" in content
    assert "Engagements" in content
    assert "Registrations" in content
    assert "Enrollments" in content


def test_reetha_data_model_is_tenant_scoped():
    content = Path(
        "docs/M12_REETHA_DATA_MODEL.md"
    ).read_text(encoding="utf-8")

    assert "tenant_id = reetha" in content
    assert "No Reetha dataset may contain records belonging to another tenant." in content


def test_reetha_funnel_relationship_is_defined():
    content = Path(
        "docs/M12_REETHA_DATA_MODEL.md"
    ).read_text(encoding="utf-8")

    assert "Campaign" in content
    assert "Lead" in content
    assert "Engagement" in content
    assert "Registration" in content
    assert "Enrollment" in content
