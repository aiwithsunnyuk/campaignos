"""M11.6 deterministic training campaign builder.

This module deliberately contains no LLM calls, external integrations, or
string-rewrite patches. It converts explicit user inputs into a validated
TrainingCampaign and deterministic operational content.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any

from .models import TrainingCampaign, TrainingProgram


CHANNELS = (
    "WhatsApp Community",
    "Email",
    "Website",
    "Social",
)

OBJECTIVES = (
    "Course Awareness",
    "Course Interest",
    "Session Registration",
    "Course Enquiry",
    "Re-engagement",
)

CAMPAIGN_TYPES = (
    "Live Session Promotion",
    "Course Awareness",
    "Course Launch",
    "Webinar / Workshop",
    "Post-Session Nurture",
    "Re-engagement",
)

FUNNEL_STEPS = (
    "Community Reach",
    "Message View / Engagement",
    "Course Interest",
    "Session Registration",
    "Session Attendance",
    "Course Enquiry",
    "High Intent",
    "Counselling",
    "Enrolment",
)

EXECUTION_AREAS = (
    "Audience",
    "Message",
    "Channel",
    "CTA",
    "Follow-up",
    "Measurement",
)


@dataclass(frozen=True)
class TrainingCampaignBrief:
    """Human-readable campaign summary derived from a validated campaign."""

    campaign_name: str
    program_name: str
    campaign_type: str
    objective: str
    audience: str
    career_persona: str
    region: str
    session: str
    primary_channel: str
    secondary_channel: str
    cta: str


def _normalise_required(value: str, field_name: str) -> str:
    value = str(value).strip()
    if not value:
        raise ValueError(f"{field_name} is required")
    return value


def _format_session(session_date: str, session_time: str) -> str:
    parsed_date = datetime.strptime(session_date, "%Y-%m-%d").date()
    parsed_time = datetime.strptime(session_time, "%H:%M").time()
    return f"{parsed_date.isoformat()} at {parsed_time.strftime('%I:%M %p')}"


def build_training_campaign(
    *,
    campaign_id: str,
    program: TrainingProgram,
    region: str,
    session_label: str,
    channel: str = "WhatsApp Community",
    objective: str = "Course Interest",
    audience: str = "Interested and opted-in prospects",
    campaign_type: str = "Live Session Promotion",
    career_persona: str = "GENERAL",
    session_date: str | date | None = None,
    session_time: str | None = None,
    delivery_mode: str = "Verify with client",
    secondary_channel: str = "Email",
    cta: str = "Request course details",
    notes: str = "",
) -> TrainingCampaign:
    """Create and validate a training campaign from explicit inputs only."""

    campaign_id = _normalise_required(campaign_id, "campaign_id")
    region = _normalise_required(region, "region")
    session_label = _normalise_required(session_label, "session_label")
    channel = _normalise_required(channel, "channel")
    objective = _normalise_required(objective, "objective")
    audience = _normalise_required(audience, "audience")
    campaign_type = _normalise_required(campaign_type, "campaign_type")
    career_persona = _normalise_required(career_persona, "career_persona")
    delivery_mode = _normalise_required(delivery_mode, "delivery_mode")
    secondary_channel = _normalise_required(secondary_channel, "secondary_channel")
    cta = _normalise_required(cta, "cta")

    if channel not in CHANNELS:
        raise ValueError(f"Unsupported primary channel: {channel}")
    if secondary_channel not in CHANNELS:
        raise ValueError(f"Unsupported secondary channel: {secondary_channel}")
    if objective not in OBJECTIVES and objective != "Training enquiry":
        raise ValueError(f"Unsupported objective: {objective}")
    if campaign_type not in CAMPAIGN_TYPES:
        raise ValueError(f"Unsupported campaign type: {campaign_type}")

    program.validate()

    if session_date is None:
        resolved_date = date.today()
    elif isinstance(session_date, date):
        resolved_date = session_date
    else:
        resolved_date = datetime.strptime(str(session_date), "%Y-%m-%d").date()

    resolved_time = session_time or "06:30"
    datetime.strptime(resolved_time, "%H:%M")

    campaign_name = f"{program.name} | {region} | {session_label}"

    campaign = TrainingCampaign(
        campaign_id=campaign_id,
        campaign_name=campaign_name,
        program_id=program.program_id,
        program_name=program.name,
        objective=objective,
        region=region,
        primary_channel=channel,
        campaign_type=campaign_type,
        audience=audience,
        session_label=session_label,
        session_date=resolved_date.isoformat(),
        session_time=resolved_time,
        delivery_mode=delivery_mode,
        secondary_channel=secondary_channel,
        status="Draft",
        cta=cta,
        notes=notes,
        metadata={
            "program_name": program.name,
            "campaign_type": campaign_type,
            "career_persona": career_persona,
            "session_date": resolved_date.isoformat(),
            "session_time": resolved_time,
            "delivery_mode": delivery_mode,
            "secondary_channel": secondary_channel,
            "notes": notes,
        },
    )

    campaign.validate()
    return campaign


def campaign_brief(campaign: TrainingCampaign) -> TrainingCampaignBrief:
    """Create a deterministic campaign brief from a validated campaign."""

    campaign.validate()
    return TrainingCampaignBrief(
        campaign_name=campaign.campaign_name,
        program_name=campaign.program_name,
        campaign_type=campaign.metadata.get('campaign_type', ''),
        objective=campaign.objective,
        audience=campaign.audience,
        career_persona=campaign.metadata.get('career_persona', ''),
        region=campaign.region,
        session=f"{campaign.metadata.get('session_date', '')} at {campaign.metadata.get('session_time', '')}",
        primary_channel=campaign.primary_channel,
        secondary_channel=campaign.metadata.get('secondary_channel', ''),
        cta=campaign.cta,
    )


def execution_plan(campaign: TrainingCampaign) -> list[dict[str, str]]:
    """Return a deterministic six-area operational execution plan."""

    campaign.validate()

    return [
        {
            "area": "Audience",
            "action": campaign.audience,
            "owner": "Marketing Operations",
        },
        {
            "area": "Message",
            "action": f"Promote {campaign.metadata.get('program_name', campaign.program_id)} for the {campaign.session_label}",
            "owner": "Marketing Operations",
        },
        {
            "area": "Channel",
            "action": f"{campaign.primary_channel} with {campaign.metadata.get('secondary_channel', '')} follow-up",
            "owner": "Marketing Operations",
        },
        {
            "area": "CTA",
            "action": campaign.cta,
            "owner": "Marketing Operations",
        },
        {
            "area": "Follow-up",
            "action": "Capture course interest and progress engaged prospects through the training funnel",
            "owner": "Marketing / Counselling",
        },
        {
            "area": "Measurement",
            "action": "Measure engagement, registration, attendance, enquiry and enrolment progression",
            "owner": "Marketing Operations",
        },
    ]


def render_training_message(
    campaign: TrainingCampaign,
    program=None,
    *,
    contact_name: str = "there",
    join_details: str = "Synthetic session details",
) -> str:
    """Render a safe synthetic promotional message for review."""

    campaign.validate()
    contact_name = _normalise_required(contact_name, "contact_name")
    join_details = _normalise_required(join_details, "join_details")

    return "\n".join(
        [
            f"Hello {contact_name},",
            "",
            f"Join our {campaign.metadata.get('program_name', campaign.program_id)} training session.",
            "",
            f"Session: {campaign.session_label}",
            f"Region: {campaign.region}",
            f"Date: {campaign.metadata.get('session_date', '')}",
            f"Time: {campaign.metadata.get('session_time', '')}",
            f"Delivery: {campaign.metadata.get('delivery_mode', 'Verify with client')}",
            "",
            "Build practical, job-relevant skills through hands-on learning.",
            "",
            join_details,
            "",
            f"CTA: {campaign.cta}",
        ]
    )


def campaign_to_dict(campaign: TrainingCampaign) -> dict[str, Any]:
    """Return a JSON-friendly campaign representation."""

    campaign.validate()
    return asdict(campaign)
