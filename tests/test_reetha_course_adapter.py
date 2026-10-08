from pathlib import Path

import pytest

from src.data_adapters import CSVCourseAdapter


COURSES_PATH = "data/reetha/courses.csv"


def test_reetha_courses_load_into_canonical_contract():
    adapter = CSVCourseAdapter(
        tenant_id="reetha",
        path=COURSES_PATH,
    )

    courses = adapter.load()

    assert len(courses) == 12
    assert all(course.tenant_id == "reetha" for course in courses)

    first = courses[0]

    assert first.course_id == "CRS-001"
    assert first.tenant_id == "reetha"
    assert first.name == "Generative AI"
    assert first.category == "AI"
    assert first.delivery_mode == "hybrid"
    assert first.duration == "4 weeks"
    assert first.price == 12000.0
    assert first.status == "active"


def test_course_adapter_rejects_wrong_tenant(tmp_path: Path):
    csv_file = tmp_path / "wrong_tenant_courses.csv"

    csv_file.write_text(
        "course_id,tenant_id,name,category,delivery_mode,"
        "duration,price,status,created_at,updated_at\n"
        "CRS-001,demo,Generative AI,AI,hybrid,4 weeks,12000,"
        "active,2026-01-01T00:00:00,2026-01-01T00:00:00\n",
        encoding="utf-8",
    )

    adapter = CSVCourseAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    with pytest.raises(ValueError, match="Tenant mismatch"):
        adapter.load()


def test_course_adapter_rejects_missing_required_columns(tmp_path: Path):
    csv_file = tmp_path / "invalid_courses.csv"

    csv_file.write_text(
        "course_id,tenant_id,name,status\n"
        "CRS-001,reetha,Generative AI,active\n",
        encoding="utf-8",
    )

    adapter = CSVCourseAdapter(
        tenant_id="reetha",
        path=csv_file,
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        adapter.load()
