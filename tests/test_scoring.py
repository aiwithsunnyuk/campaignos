import pandas as pd

from src.scoring.engine import (
    score_contact,
    score_contacts,
    score_distribution,
)


def make_contact(
    contact_id="CON-000001",
    engagement_score=80,
    lifecycle_stage="MQL",
    consent_status="Opted In",
    job_title="Director",
    industry="Technology",
    region="APAC",
    country="India",
    account_id="ACC-000001",
):
    return pd.Series(
        {
            "contact_id": contact_id,
            "engagement_score": engagement_score,
            "lifecycle_stage": lifecycle_stage,
            "consent_status": consent_status,
            "job_title": job_title,
            "industry": industry,
            "region": region,
            "country": country,
            "account_id": account_id,
        }
    )


def test_score_contact_returns_valid_result():
    result = score_contact(make_contact())

    assert result.contact_id == "CON-000001"
    assert 0 <= result.lead_score <= 100
    assert result.score_band in {"Hot", "Warm", "Nurture", "Cold"}
    assert result.qualification
    assert result.recommended_action


def test_high_engagement_contact_scores_well():
    result = score_contact(
        make_contact(
            engagement_score=100,
            lifecycle_stage="Customer",
        )
    )

    assert result.lead_score >= 80
    assert result.score_band == "Hot"


def test_low_engagement_contact_scores_lower():
    result = score_contact(
        make_contact(
            engagement_score=10,
            lifecycle_stage="Lead",
        )
    )

    assert result.lead_score < 60
    assert result.score_band in {"Cold", "Nurture"}


def test_non_opted_in_contact_is_not_marketable():
    result = score_contact(
        make_contact(
            engagement_score=100,
            lifecycle_stage="Customer",
            consent_status="Not Subscribed",
        )
    )

    assert result.qualification == "Not Marketable"
    assert result.recommended_action == "Suppress from outbound campaigns"


def test_score_contacts_preserves_original_data():
    contacts = pd.DataFrame(
        [
            make_contact("CON-000001"),
            make_contact(
                contact_id="CON-000002",
                engagement_score=30,
                lifecycle_stage="Lead",
            ),
        ]
    )

    scored = score_contacts(contacts)

    assert len(scored) == 2
    assert "first_name" not in scored.columns
    assert "contact_id" in scored.columns
    assert "calculated_lead_score" in scored.columns
    assert "score_band" in scored.columns
    assert "qualification" in scored.columns
    assert "recommended_action" in scored.columns


def test_score_distribution():
    contacts = pd.DataFrame(
        [
            make_contact("CON-000001", engagement_score=100),
            make_contact("CON-000002", engagement_score=90),
            make_contact(
                "CON-000003",
                engagement_score=20,
                lifecycle_stage="Lead",
            ),
        ]
    )

    scored = score_contacts(contacts)
    distribution = score_distribution(scored)

    assert "score_band" in distribution.columns
    assert "contacts" in distribution.columns
    assert "percentage" in distribution.columns
    assert distribution["contacts"].sum() == 3