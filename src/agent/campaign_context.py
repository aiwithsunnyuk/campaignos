from __future__ import annotations

from typing import Any

import pandas as pd


def build_campaign_context(
    campaign: pd.Series,
    contacts: pd.DataFrame,
    activities: pd.DataFrame,
) -> dict[str, Any]:
    """Build deterministic agent context from CampaignOS synthetic data."""

    campaign_id = str(campaign["campaign_id"])
    campaign_activities = activities[
        activities["campaign_id"].astype(str) == campaign_id
    ].copy()

    def count_activity(name: str) -> int:
        return int(
            (campaign_activities["activity_type"].astype(str).str.lower() == name.lower()).sum()
        )

    sent = count_activity("Sent")
    opened = count_activity("Opened")
    clicked = count_activity("Clicked")
    converted = count_activity("Submitted")

    if sent:
        open_rate = opened / sent
        click_rate = clicked / sent
        conversion_rate = converted / sent
    else:
        open_rate = click_rate = conversion_rate = 0.0

    region = str(campaign["region"])
    regional_contacts = contacts[
        contacts["region"].astype(str) == region
    ].copy()

    marketable = int(
        (regional_contacts["consent_status"].astype(str).str.lower() == "opted in").sum()
    )
    mql_count = int(
        (regional_contacts["lifecycle_stage"].astype(str).str.upper() == "MQL").sum()
    )
    average_lead_score = (
        float(regional_contacts["lead_score"].mean())
        if not regional_contacts.empty
        else 0.0
    )

    return {
        "sent": sent,
        "opened": opened,
        "clicked": clicked,
        "converted": converted,
        "open_rate": open_rate,
        "click_rate": click_rate,
        "conversion_rate": conversion_rate,
        "conversion_benchmark": 0.04,
        "marketable_contacts": marketable,
        "mql_count": mql_count,
        "average_lead_score": average_lead_score,
    }
