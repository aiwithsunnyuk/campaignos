"""Deterministic M11 training campaign and lead-intent logic."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping

from .models import (
    LeadIntentStage,
    ProgramRecommendation,
    TrainingCampaign,
    TrainingLeadProfile,
    TrainingProgram,
)


def score_training_intent(signals: Mapping[str, bool | int | float]) -> tuple[int, LeadIntentStage]:
    """Score training intent from explicit behavioral signals only.

    This is intentionally deterministic and does not infer sensitive attributes.
    """
    weights = {
        "campaign_engaged": 5,
        "course_viewed": 10,
        "specific_course_selected": 15,
        "details_requested": 15,
        "session_registered": 20,
        "session_attended": 20,
        "course_question": 15,
        "counselling_requested": 25,
        "enquiry_submitted": 30,
    }
    score = 0
    for signal, weight in weights.items():
        value = signals.get(signal, False)
        if isinstance(value, bool):
            score += weight if value else 0
        elif isinstance(value, (int, float)):
            score += weight * max(0.0, min(1.0, float(value)))
    score = min(100, round(score))

    if score >= 85:
        stage = LeadIntentStage.ENQUIRY_READY
    elif score >= 70:
        stage = LeadIntentStage.HIGH_INTENT
    elif score >= 50:
        stage = LeadIntentStage.ENGAGED
    elif score >= 30:
        stage = LeadIntentStage.INTERESTED
    else:
        stage = LeadIntentStage.AWARENESS
    return score, stage


def recommend_programs(
    profile: TrainingLeadProfile,
    programs: Iterable[TrainingProgram],
    *,
    limit: int = 3,
) -> list[ProgramRecommendation]:
    """Recommend programs using transparent tag/goal matching."""
    profile.validate()
    scored: list[ProgramRecommendation] = []
    query = {
        profile.background.lower(),
        profile.career_goal.lower(),
        profile.interest.lower(),
        profile.experience_level.lower(),
        profile.learning_preference.lower(),
        profile.region.lower(),
    }
    for program in programs:
        program.validate()
        score = 0
        reasons: list[str] = []
        tags = {item.lower() for item in (*program.audience_tags, *program.career_paths)}
        for term in query:
            if not term:
                continue
            matches = [tag for tag in tags if term in tag or tag in term]
            if matches:
                score += 20
                reasons.append(f"Matches {term}")
        if profile.interest.lower() in program.name.lower():
            score += 25
            reasons.append("Program name matches stated interest")
        score = min(100, score)
        if score > 0:
            scored.append(
                ProgramRecommendation(
                    program_id=program.program_id,
                    program_name=program.name,
                    score=score,
                    reasons=tuple(reasons),
                )
            )
    scored.sort(key=lambda item: (-item.score, item.program_name))
    return scored[: max(1, limit)]


def build_campaign_snapshot(
    campaign: TrainingCampaign,
    program: TrainingProgram,
    *,
    audience_total: int = 0,
    marketable_total: int = 0,
    mql_total: int = 0,
    high_intent_total: int = 0,
    enquiries_total: int = 0,
) -> dict[str, object]:
    """Build a compact, UI-ready campaign snapshot."""
    campaign.validate()
    program.validate()
    if campaign.program_id != program.program_id:
        raise ValueError("campaign and program do not match")
    if any(value < 0 for value in (audience_total, marketable_total, mql_total, high_intent_total, enquiries_total)):
        raise ValueError("campaign metrics cannot be negative")
    return {
        "campaign": campaign.campaign_name,
        "program": program.name,
        "category": program.category,
        "region": campaign.region,
        "objective": campaign.objective,
        "status": campaign.status,
        "primary_channel": campaign.primary_channel,
        "audience_total": audience_total,
        "marketable_total": marketable_total,
        "mql_total": mql_total,
        "high_intent_total": high_intent_total,
        "enquiries_total": enquiries_total,
        "marketable_rate": round(marketable_total / audience_total, 4) if audience_total else 0.0,
        "enquiry_rate": round(enquiries_total / audience_total, 4) if audience_total else 0.0,
    }
