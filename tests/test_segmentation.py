import pandas as pd
import pytest

from src.segmentation.engine import build_segment
from src.segmentation.models import (
    SegmentDefinition,
    SegmentRule,
)


@pytest.fixture
def sample_contacts():
    return pd.DataFrame(
        [
            {
                "contact_id": "CON-001",
                "region": "APAC",
                "industry": "Technology",
                "lifecycle_stage": "MQL",
                "lead_score": 80,
                "engagement_score": 75,
                "consent_status": "Opted In",
            },
            {
                "contact_id": "CON-002",
                "region": "Europe",
                "industry": "Financial Services",
                "lifecycle_stage": "Customer",
                "lead_score": 45,
                "engagement_score": 50,
                "consent_status": "Opted In",
            },
            {
                "contact_id": "CON-003",
                "region": "APAC",
                "industry": "Technology",
                "lifecycle_stage": "Opportunity",
                "lead_score": 65,
                "engagement_score": 30,
                "consent_status": "Not Subscribed",
            },
            {
                "contact_id": "CON-004",
                "region": "AMEA",
                "industry": "Agriculture",
                "lifecycle_stage": "MQL",
                "lead_score": 72,
                "engagement_score": 68,
                "consent_status": "Opted In",
            },
        ]
    )


def test_segment_by_region(sample_contacts):

    segment = SegmentDefinition(
        segment_id="SEG-001",
        segment_name="APAC Audience",
        rules=[
            SegmentRule(
                field="region",
                operator="equals",
                value="APAC",
            )
        ],
    )

    result = build_segment(sample_contacts, segment)

    assert result.audience_count == 2
    assert result.audience_percentage == 50.0


def test_segment_with_multiple_and_rules(sample_contacts):

    segment = SegmentDefinition(
        segment_id="SEG-002",
        segment_name="APAC Technology MQLs",
        rules=[
            SegmentRule(
                field="region",
                operator="equals",
                value="APAC",
            ),
            SegmentRule(
                field="industry",
                operator="equals",
                value="Technology",
            ),
            SegmentRule(
                field="lifecycle_stage",
                operator="equals",
                value="MQL",
            ),
        ],
        logic="AND",
    )

    result = build_segment(sample_contacts, segment)

    assert result.audience_count == 1
    assert result.contacts.iloc[0]["contact_id"] == "CON-001"


def test_segment_with_score_threshold(sample_contacts):

    segment = SegmentDefinition(
        segment_id="SEG-003",
        segment_name="High Intent Audience",
        rules=[
            SegmentRule(
                field="lead_score",
                operator="greater_than_or_equal",
                value=70,
            )
        ],
    )

    result = build_segment(sample_contacts, segment)

    assert result.audience_count == 2


def test_segment_with_or_logic(sample_contacts):

    segment = SegmentDefinition(
        segment_id="SEG-004",
        segment_name="APAC or AMEA",
        rules=[
            SegmentRule(
                field="region",
                operator="equals",
                value="APAC",
            ),
            SegmentRule(
                field="region",
                operator="equals",
                value="AMEA",
            ),
        ],
        logic="OR",
    )

    result = build_segment(sample_contacts, segment)

    assert result.audience_count == 3


def test_invalid_segment():

    segment = SegmentDefinition(
        segment_id="SEG-005",
        segment_name="Invalid",
        rules=[],
    )

    with pytest.raises(ValueError):
        segment.validate()


def test_unknown_field(sample_contacts):

    segment = SegmentDefinition(
        segment_id="SEG-006",
        segment_name="Invalid Field",
        rules=[
            SegmentRule(
                field="unknown_field",
                operator="equals",
                value="APAC",
            )
        ],
    )

    with pytest.raises(ValueError):
        build_segment(sample_contacts, segment)