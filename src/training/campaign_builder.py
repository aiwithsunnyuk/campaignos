"""M11.2 deterministic training campaign builder and content templates."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date

from .models import TrainingCampaign, TrainingProgram


def build_training_campaign(
    *,
    campaign_id: str,
    program: TrainingProgram,
    region: str,
    session_label: str,
    channel: str = "WhatsApp",
    objective: str = "Training enquiry",
    audience: str = "Interested and opted-in prospects",
    cta: str = "Request course details",
) -> TrainingCampaign:
    """Create a validated training campaign from explicit inputs only."""
    if not session_label.strip():
        raise ValueError("session_label is required")
    campaign = TrainingCampaign(
        campaign_id=campaign_id,
        campaign_name=f"{program.name} | {region} | {session_label}",
        program_id=program.program_id,
        objective=objective,
        region=region,
        primary_channel=channel,
        status="Draft",
        audience=audience,
        session_label=session_label,
        cta=cta,
        metadata={"created_on": date.today().isoformat()},
    )
    campaign.validate()
    return campaign


def render_training_message(
    campaign: TrainingCampaign,
    program: TrainingProgram,
    *,
    contact_name: str = "there",
    join_details: str = "Synthetic session details",
) -> str:
    """Render a safe synthetic promotional message."""
    campaign.validate()
    program.validate()
    return (
        f"Hello {contact_name},\n\n"
        f"Join our {program.name} training session.\n"
        f"Session: {campaign.session_label}\n"
        f"Region: {campaign.region}\n\n"
        f"Build practical, job-relevant skills through hands-on learning.\n\n"
        f"{join_details}\n\n"
        f"CTA: {campaign.cta}"
    )


def campaign_to_dict(campaign: TrainingCampaign) -> dict[str, object]:
    """Return a serializable campaign representation."""
    campaign.validate()
    return asdict(campaign)
