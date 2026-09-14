"""Domain models for M11 Training Growth & Campaign 360."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LeadIntentStage(str, Enum):
    AWARENESS = "Awareness"
    INTERESTED = "Interested"
    ENGAGED = "Engaged"
    HIGH_INTENT = "High Intent"
    ENQUIRY_READY = "Enquiry Ready"


@dataclass(frozen=True)
class TrainingProgram:
    program_id: str
    name: str
    category: str
    audience_tags: tuple[str, ...] = ()
    career_paths: tuple[str, ...] = ()
    delivery_mode: str = "Verify with client"
    source_url: str = "https://handsonagilecoaching.com/"
    active: bool = True

    def validate(self) -> None:
        if not self.program_id.strip():
            raise ValueError("program_id is required")
        if not self.name.strip():
            raise ValueError("name is required")
        if not self.category.strip():
            raise ValueError("category is required")


@dataclass(frozen=True)
class TrainingLeadProfile:
    background: str
    career_goal: str
    interest: str
    experience_level: str
    learning_preference: str = ""
    region: str = "Global"

    def validate(self) -> None:
        required = {
            "background": self.background,
            "career_goal": self.career_goal,
            "interest": self.interest,
            "experience_level": self.experience_level,
        }
        missing = [key for key, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"Missing lead profile fields: {', '.join(missing)}")


@dataclass(frozen=True)
class TrainingCampaign:
    campaign_id: str
    campaign_name: str
    program_id: str
    objective: str = "Training enquiry"
    region: str = "Global"
    primary_channel: str = "WhatsApp"
    status: str = "Draft"
    audience: str = ""
    session_label: str = ""
    cta: str = "Course enquiry"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.campaign_id.strip():
            raise ValueError("campaign_id is required")
        if not self.campaign_name.strip():
            raise ValueError("campaign_name is required")
        if not self.program_id.strip():
            raise ValueError("program_id is required")


@dataclass(frozen=True)
class ProgramRecommendation:
    program_id: str
    program_name: str
    score: int
    reasons: tuple[str, ...]

    def validate(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError("recommendation score must be between 0 and 100")
