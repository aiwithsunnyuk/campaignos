"""M13.6.1: copy-quality refinement for CampaignOS Content Studio."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping


@dataclass(frozen=True)
class CampaignBrief:
    campaign_name: str
    objective: str
    audience: str
    demand_signal: str
    primary_offering: str
    channels: tuple[str, ...]
    call_to_action: str
    tone: str = "Professional and helpful"


@dataclass(frozen=True)
class ContentDraft:
    channel: str
    asset_type: str
    title: str
    body: str
    call_to_action: str
    rationale: str
    status: str = "Draft · awaiting human review"


@dataclass(frozen=True)
class ContentPackage:
    campaign_name: str
    objective: str
    audience: str
    offering: str
    drafts: tuple[ContentDraft, ...]
    approval_required: bool = True
    external_execution_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["drafts"] = [asdict(draft) for draft in self.drafts]
        return result


SUPPORTED_CHANNELS = ("Email", "WhatsApp", "LinkedIn")


def _clean(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _sentence_case(value: str) -> str:
    """Light normalization for display copy without rewriting domain names."""
    value = " ".join(value.strip().split())
    if not value:
        return value
    return value[0].upper() + value[1:]


def _audience_phrase(value: str) -> str:
    """Normalize generic audience labels while preserving known SAP abbreviations."""
    value = " ".join(value.strip().split())
    replacements = {
        "sap finance / fico professionals": "SAP Finance / FICO professionals",
        "sap professionals": "SAP professionals",
        "sap consultants": "SAP consultants",
    }
    return replacements.get(value.casefold(), _sentence_case(value))


def _objective_phrase(value: str) -> str:
    """Return a customer-facing objective phrase, not an internal planning verbatim."""
    objective = " ".join(value.strip().split()).rstrip(".")
    normalized = objective.casefold()
    if not objective:
        return "help you explore practical next steps"
    # Common internal marketing objectives are translated to natural reader-facing copy.
    if "nurture demand" in normalized and ("qualified enquir" in normalized or "lead" in normalized):
        return "help interested professionals explore the right next step"
    if "generate qualified enquir" in normalized:
        return "help interested professionals find the right next step"
    if "nurture demand" in normalized:
        return "help interested professionals explore relevant options"
    if normalized.startswith("increase awareness"):
        return "help more professionals understand the available options"
    return _sentence_case(objective)


def normalize_brief(value: CampaignBrief | Mapping[str, Any]) -> CampaignBrief:
    """Accept a typed brief or mapping with common campaign-plan field names."""
    if isinstance(value, CampaignBrief):
        return CampaignBrief(
            campaign_name=_clean(value.campaign_name, "Reetha Growth Campaign"),
            objective=_clean(value.objective, "Explore relevant options"),
            audience=_audience_phrase(_clean(value.audience, "relevant professionals")),
            demand_signal=_clean(value.demand_signal, "relevant business interest"),
            primary_offering=_clean(value.primary_offering, "relevant training or consulting offering"),
            channels=value.channels,
            call_to_action=_clean(value.call_to_action, "Book a consultation"),
            tone=_clean(value.tone, "Professional and helpful"),
        )
    if not isinstance(value, Mapping):
        raise TypeError("brief must be a CampaignBrief or mapping")

    def pick(*keys: str, default: str = "") -> str:
        for key in keys:
            if key in value and value[key] not in (None, ""):
                return str(value[key]).strip()
        return default

    raw_channels = value.get("channels", value.get("recommended_channels", ("Email", "WhatsApp", "LinkedIn")))
    if isinstance(raw_channels, str):
        channels = tuple(part.strip() for part in raw_channels.replace(";", ",").split(",") if part.strip())
    else:
        channels = tuple(str(part).strip() for part in (raw_channels or ()) if str(part).strip())

    return CampaignBrief(
        campaign_name=pick("campaign_name", "name", "campaign", default="Reetha Growth Campaign"),
        objective=pick("objective", "goal", default="Nurture relevant demand and generate qualified enquiries"),
        audience=_audience_phrase(pick("audience", "target_audience", default="Relevant professionals and prospective learners")),
        demand_signal=pick("demand_signal", "demand", "sap_domain", default="Relevant business interest"),
        primary_offering=pick("primary_offering", "offering", "course", default="Relevant training or consulting offering"),
        channels=channels,
        call_to_action=pick("call_to_action", "cta", "CTA", default="Book a consultation"),
        tone=pick("tone", default="Professional and helpful"),
    )


def generate_content_package(brief: CampaignBrief | Mapping[str, Any]) -> ContentPackage:
    """Build deterministic first drafts. No external model, network or publishing."""
    b = normalize_brief(brief)
    objective_phrase = _objective_phrase(b.objective)
    audience_phrase = _audience_phrase(b.audience)
    allowed = {channel.lower(): channel for channel in SUPPORTED_CHANNELS}
    channels: list[str] = []
    for channel in b.channels:
        canonical = allowed.get(channel.lower())
        if canonical and canonical not in channels:
            channels.append(canonical)
    if not channels:
        channels = ["Email", "WhatsApp", "LinkedIn"]

    offering = _sentence_case(b.primary_offering)
    demand = b.demand_signal.strip()
    drafts: list[ContentDraft] = []
    if "Email" in channels:
        drafts.extend([
            ContentDraft(
                channel="Email",
                asset_type="Subject line",
                title=f"Explore {demand} with Reetha IT Hub",
                body=f"Explore {demand} with Reetha IT Hub",
                call_to_action=b.call_to_action,
                rationale="Connects the audience's stated demand signal to the relevant offering.",
            ),
            ContentDraft(
                channel="Email",
                asset_type="Email body",
                title=f"{offering}: a practical next step",
                body=(
                    f"Hello,\n\n"
                    f"If {demand} is relevant to your goals, Reetha IT Hub can help you explore {offering}. "
                    f"We aim to {objective_phrase} for {audience_phrase}.\n\n"
                    f"Reply to discuss your needs or use the next step below.\n\n"
                    f"{b.call_to_action}\n\n"
                    "Reetha IT Hub"
                ),
                call_to_action=b.call_to_action,
                rationale="States the relevance, offering and next step without unsupported performance claims.",
            ),
        ])
    if "WhatsApp" in channels:
        drafts.append(ContentDraft(
            channel="WhatsApp",
            asset_type="Message",
            title=f"{demand} | Reetha IT Hub",
            body=(
                f"Hello! Are you exploring {demand}? Reetha IT Hub can help you learn more about {offering}. "
                f"If this is relevant to you, {b.call_to_action.rstrip('.')} . "
                "Reply here if you would like more details."
            ).replace(" . ", ". "),
            call_to_action=b.call_to_action,
            rationale="Short, conversational copy suitable for a permission-based follow-up.",
        ))
    if "LinkedIn" in channels:
        drafts.append(ContentDraft(
            channel="LinkedIn",
            asset_type="Post",
            title=f"Turning {demand} into a practical next step",
            body=(
                f"Considering your next step in {demand}?\n\n"
                f"Reetha IT Hub is highlighting {offering} for {audience_phrase}.\n\n"
                f"The goal is to {objective_phrase}. Start with your priorities, explore the options, "
                "and choose a next step that fits your context.\n\n"
                f"{b.call_to_action.rstrip('.')}."
            ),
            call_to_action=b.call_to_action,
            rationale="Educational framing aligned to the campaign brief; avoids unsupported performance claims.",
        ))

    return ContentPackage(
        campaign_name=b.campaign_name,
        objective=b.objective,
        audience=audience_phrase,
        offering=offering,
        drafts=tuple(drafts),
    )


def render_content_studio() -> None:
    """Streamlit UI for building and reviewing a campaign content package."""
    import json
    import streamlit as st

    st.divider()
    st.header("AI Content Studio")
    st.caption(
        "M13.6 · Convert a campaign brief into editable multi-channel drafts. "
        "Draft generation is deterministic in this milestone; external publishing is disabled."
    )
    st.info(
        "DEMO / GOVERNED MODE: review and edit all copy before approval. "
        "No external AI provider, contact list, or publishing channel is called."
    )

    with st.container(border=True):
        st.subheader("Campaign brief")
        campaign_name = st.text_input("Campaign name", value="SAP Finance / FICO Growth Campaign")
        objective = st.text_input(
            "Objective", value="Nurture demand and generate qualified enquiries"
        )
        audience = st.text_input("Target audience", value="SAP Finance / FICO professionals")
        demand = st.text_input("Demand signal", value="SAP Finance / FICO")
        offering = st.text_input("Primary offering", value="SAP Finance / FICO training")
        channels = st.multiselect(
            "Channels", options=list(SUPPORTED_CHANNELS),
            default=["Email", "WhatsApp", "LinkedIn"],
        )
        cta = st.text_input("Call to action", value="Book a consultation")
        tone = st.selectbox("Tone", ["Professional and helpful", "Educational", "Concise", "Consultative"])

    package = generate_content_package(CampaignBrief(
        campaign_name=campaign_name, objective=objective, audience=audience,
        demand_signal=demand, primary_offering=offering, channels=tuple(channels),
        call_to_action=cta, tone=tone,
    ))

    col1, col2 = st.columns(2)
    col1.metric("Content assets", len(package.drafts))
    col2.metric("Channels", len({draft.channel for draft in package.drafts}))
    if not package.drafts:
        st.warning("Select at least one channel to generate drafts.")
        return

    st.subheader("Editable content drafts")
    edited: list[ContentDraft] = []
    for index, draft in enumerate(package.drafts):
        with st.expander(f"{draft.channel} · {draft.asset_type}", expanded=(index == 0)):
            title = st.text_input("Asset title", value=draft.title, key=f"m136_title_{index}")
            body = st.text_area("Draft copy", value=draft.body, height=180, key=f"m136_body_{index}")
            edited.append(ContentDraft(
                channel=draft.channel, asset_type=draft.asset_type, title=title, body=body,
                call_to_action=draft.call_to_action, rationale=draft.rationale,
            ))
            st.caption(f"Rationale: {draft.rationale}")

    st.subheader("Approval gate")
    st.warning("Approval is a review-state only in M13.6. It does not send, schedule, or publish content.")
    approved = st.checkbox(
        "I have reviewed these drafts and mark this content package approved for the next governed workflow.",
        key="m136_content_approval",
    )
    package_out = ContentPackage(
        campaign_name=package.campaign_name, objective=package.objective,
        audience=package.audience, offering=package.offering, drafts=tuple(edited),
        approval_required=not approved, external_execution_enabled=False,
    )
    st.download_button(
        "Export content package (JSON)",
        data=json.dumps(package_out.to_dict(), indent=2, ensure_ascii=False),
        file_name="campaignos_content_package.json", mime="application/json",
    )
    if approved:
        st.success("Marked reviewed in this session. No external action was performed.")
    else:
        st.caption("Status: awaiting human review.")
