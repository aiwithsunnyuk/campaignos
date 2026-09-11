from __future__ import annotations

from typing import Any

import pandas as pd

from src.scoring.models import (
    DEFAULT_LIFECYCLE_RULES,
    LeadScoreResult,
    ScoringWeights,
)


def _score_engagement(engagement_score: float) -> int:
    """Convert engagement score to a 0-40 contribution."""
    return round(max(0, min(float(engagement_score), 100)) * 0.40)


def _score_profile(row: pd.Series) -> int:
    """Score contact profile quality from available contact attributes."""
    score = 0

    if str(row.get("job_title", "")).strip():
        score += 10

    if str(row.get("industry", "")).strip():
        score += 5

    if str(row.get("region", "")).strip():
        score += 5

    if str(row.get("country", "")).strip():
        score += 5

    if str(row.get("account_id", "")).strip():
        score += 5

    return min(score, 30)


def _score_lifecycle(lifecycle_stage: str) -> int:
    """Convert lifecycle stage into a 0-20 contribution."""
    stage_scores = {
        "Customer": 20,
        "MQL": 18,
        "SQL": 18,
        "Engaged": 14,
        "Marketing Qualified Prospect": 10,
        "Opportunity": 16,
        "Lead": 5,
        "Unknown": 0,
    }

    return stage_scores.get(str(lifecycle_stage), 5)


def _score_consent(consent_status: str) -> int:
    """Give full consent points only to marketable contacts."""
    return 10 if str(consent_status).strip().lower() == "opted in" else 0


def _score_band(score: int) -> str:
    if score >= 80:
        return "Hot"
    if score >= 60:
        return "Warm"
    if score >= 40:
        return "Nurture"
    return "Cold"


def _lifecycle_from_score(score: int) -> str:
    for rule in DEFAULT_LIFECYCLE_RULES:
        if score >= rule.minimum_score:
            return rule.lifecycle_stage

    return "Lead"


def _qualification(score: int, consent_status: str) -> str:
    if str(consent_status).strip().lower() != "opted in":
        return "Not Marketable"

    if score >= 80:
        return "MQL Candidate"

    if score >= 60:
        return "Sales Review"

    if score >= 40:
        return "Nurture"

    return "Early Stage"


def _recommended_action(score: int, consent_status: str) -> str:
    if str(consent_status).strip().lower() != "opted in":
        return "Suppress from outbound campaigns"

    if score >= 80:
        return "Prioritize for sales follow-up"

    if score >= 60:
        return "Add to high-intent nurture"

    if score >= 40:
        return "Continue engagement nurture"

    return "Build awareness"


def score_contact(
    row: pd.Series,
    weights: ScoringWeights | None = None,
) -> LeadScoreResult:
    """
    Calculate a normalized lead score for one contact.

    The scoring model combines:
    - engagement
    - profile completeness
    - lifecycle stage
    - consent
    """

    weights = weights or ScoringWeights()

    engagement = _score_engagement(row.get("engagement_score", 0))
    profile = _score_profile(row)
    lifecycle = _score_lifecycle(row.get("lifecycle_stage", "Unknown"))
    consent = _score_consent(row.get("consent_status", ""))

    raw_score = (
        engagement
        + profile
        + lifecycle
        + consent
    )

    # Keep the score within the standard 0-100 range.
    lead_score = max(0, min(int(raw_score), 100))

    return LeadScoreResult(
        contact_id=str(row.get("contact_id", "")),
        lead_score=lead_score,
        score_band=_score_band(lead_score),
        lifecycle_stage=_lifecycle_from_score(lead_score),
        qualification=_qualification(
            lead_score,
            row.get("consent_status", ""),
        ),
        recommended_action=_recommended_action(
            lead_score,
            row.get("consent_status", ""),
        ),
        score_breakdown={
            "engagement": engagement,
            "profile": profile,
            "lifecycle": lifecycle,
            "consent": consent,
        },
    )


def score_contacts(
    contacts: pd.DataFrame,
    weights: ScoringWeights | None = None,
) -> pd.DataFrame:
    """
    Score an entire contact dataframe.

    Returns the original contact attributes plus:
    - calculated lead score
    - score band
    - qualification
    - recommended action
    """

    if contacts.empty:
        return contacts.copy()

    results = [
        score_contact(row, weights)
        for _, row in contacts.iterrows()
    ]

    scoring_df = pd.DataFrame(
        [
            {
                "contact_id": result.contact_id,
                "calculated_lead_score": result.lead_score,
                "score_band": result.score_band,
                "calculated_lifecycle_stage": result.lifecycle_stage,
                "qualification": result.qualification,
                "recommended_action": result.recommended_action,
            }
            for result in results
        ]
    )

    return contacts.merge(
        scoring_df,
        on="contact_id",
        how="left",
    )


def score_distribution(scored_contacts: pd.DataFrame) -> pd.DataFrame:
    """Return lead-score band distribution."""

    if scored_contacts.empty:
        return pd.DataFrame(
            columns=["score_band", "contacts", "percentage"]
        )

    distribution = (
        scored_contacts
        .groupby("score_band")
        .size()
        .reset_index(name="contacts")
    )

    total = distribution["contacts"].sum()

    if total:
        distribution["percentage"] = (
            distribution["contacts"] / total * 100
        ).round(2)
    else:
        distribution["percentage"] = 0.0

    band_order = ["Hot", "Warm", "Nurture", "Cold"]

    distribution["score_band"] = pd.Categorical(
        distribution["score_band"],
        categories=band_order,
        ordered=True,
    )

    return distribution.sort_values("score_band").reset_index(drop=True)