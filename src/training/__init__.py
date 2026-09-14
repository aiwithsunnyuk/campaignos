"""M11 training growth domain primitives for CampaignOS."""

from .models import (
    LeadIntentStage,
    TrainingCampaign,
    TrainingLeadProfile,
    TrainingProgram,
)
from .engine import (
    build_campaign_snapshot,
    recommend_programs,
    score_training_intent,
)

__all__ = [
    "LeadIntentStage",
    "TrainingCampaign",
    "TrainingLeadProfile",
    "TrainingProgram",
    "build_campaign_snapshot",
    "recommend_programs",
    "score_training_intent",
]
