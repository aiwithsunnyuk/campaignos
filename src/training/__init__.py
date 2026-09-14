"""Training Growth domain for CampaignOS."""
from .campaign_builder import build_training_campaign, campaign_to_dict, render_training_message
from .engine import build_campaign_snapshot, recommend_programs, score_training_intent
from .models import (
    LeadIntentStage,
    ProgramRecommendation,
    TrainingCampaign,
    TrainingLeadProfile,
    TrainingProgram,
)
from .personas import CAREER_PERSONAS, CareerPersona, identify_persona

__all__ = [
    "LeadIntentStage",
    "ProgramRecommendation",
    "TrainingCampaign",
    "TrainingLeadProfile",
    "TrainingProgram",
    "CareerPersona",
    "CAREER_PERSONAS",
    "build_campaign_snapshot",
    "build_training_campaign",
    "campaign_to_dict",
    "identify_persona",
    "recommend_programs",
    "render_training_message",
    "score_training_intent",
]
