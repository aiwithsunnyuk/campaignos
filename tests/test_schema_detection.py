from src.data_ingestion import SchemaDetector


def test_detect_lead_schema():
    result = SchemaDetector().detect(
        (
            "Lead ID",
            "Email Address",
            "Full Name",
            "Mobile",
        )
    )

    assert result.dataset_type == "lead"
    assert result.confidence == 1.0
    assert result.missing_fields == ()
    assert ("lead_id", "Lead ID") in result.suggested_column_mapping
    assert ("email", "Email Address") in result.suggested_column_mapping


def test_detect_campaign_schema():
    result = SchemaDetector().detect(
        (
            "campaign_id",
            "campaign",
            "status",
        )
    )

    assert result.dataset_type == "campaign"
    assert result.confidence == 1.0
    assert result.missing_fields == ()


def test_detect_engagement_schema():
    result = SchemaDetector().detect(
        (
            "engagement_id",
            "lead id",
            "event",
            "channel",
        )
    )

    assert result.dataset_type == "engagement"
    assert result.confidence == 1.0


def test_detect_partial_registration_schema():
    result = SchemaDetector().detect(
        (
            "registration_id",
            "lead_id",
        )
    )

    assert result.dataset_type == "registration"
    assert result.confidence < 1.0
    assert result.missing_fields == ("course_id",)


def test_unknown_schema():
    result = SchemaDetector().detect(
        (
            "customer_name",
            "address",
            "city",
        )
    )

    assert result.dataset_type == "unknown"
    assert result.confidence == 0.0
    assert result.suggested_column_mapping == ()
