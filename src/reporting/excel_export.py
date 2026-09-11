from pathlib import Path
from typing import Dict

import pandas as pd


FUNNEL_EVENTS = {
    "sent": "Email Sent",
    "opened": "Email Opened",
    "clicked": "Email Clicked",
    "converted": "Form Submitted",
}


def _unique_contacts(
    activity_data: pd.DataFrame,
    activity_type: str,
) -> int:
    if activity_data.empty:
        return 0

    filtered = activity_data[
        activity_data["activity_type"] == activity_type
    ]

    if "contact_id" not in filtered.columns:
        return 0

    return int(filtered["contact_id"].nunique())


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return round((numerator / denominator) * 100, 2)


def build_campaign_performance(
    campaigns: pd.DataFrame,
    activities: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build campaign-level performance metrics for Excel reporting.
    """

    if campaigns.empty:
        return pd.DataFrame()

    rows = []

    for _, campaign in campaigns.iterrows():
        campaign_id = campaign["campaign_id"]

        activity_data = activities[
            activities["campaign_id"] == campaign_id
        ]

        sent = _unique_contacts(
            activity_data,
            FUNNEL_EVENTS["sent"],
        )

        opened = _unique_contacts(
            activity_data,
            FUNNEL_EVENTS["opened"],
        )

        clicked = _unique_contacts(
            activity_data,
            FUNNEL_EVENTS["clicked"],
        )

        converted = _unique_contacts(
            activity_data,
            FUNNEL_EVENTS["converted"],
        )

        rows.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign["campaign_name"],
                "business_type": campaign["business_type"],
                "region": campaign["region"],
                "objective": campaign["objective"],
                "status": campaign["status"],
                "budget": float(campaign["budget"]),
                "start_date": campaign["start_date"],
                "sent": sent,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
                "open_rate": _rate(opened, sent),
                "click_rate": _rate(clicked, sent),
                "conversion_rate": _rate(converted, sent),
            }
        )

    return pd.DataFrame(rows)


def build_regional_performance(
    performance: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate campaign performance by region.
    """

    if performance.empty:
        return pd.DataFrame()

    grouped = (
        performance.groupby("region", dropna=False)
        .agg(
            campaigns=("campaign_id", "count"),
            budget=("budget", "sum"),
            sent=("sent", "sum"),
            opened=("opened", "sum"),
            clicked=("clicked", "sum"),
            converted=("converted", "sum"),
        )
        .reset_index()
    )

    grouped["open_rate"] = grouped.apply(
        lambda row: _rate(
            int(row["opened"]),
            int(row["sent"]),
        ),
        axis=1,
    )

    grouped["click_rate"] = grouped.apply(
        lambda row: _rate(
            int(row["clicked"]),
            int(row["sent"]),
        ),
        axis=1,
    )

    grouped["conversion_rate"] = grouped.apply(
        lambda row: _rate(
            int(row["converted"]),
            int(row["sent"]),
        ),
        axis=1,
    )

    return grouped


def build_executive_summary(
    performance: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build executive-level KPI summary.
    """

    if performance.empty:
        return pd.DataFrame(
            [
                {
                    "metric": "Campaigns",
                    "value": 0,
                }
            ]
        )

    sent = int(performance["sent"].sum())
    opened = int(performance["opened"].sum())
    clicked = int(performance["clicked"].sum())
    converted = int(performance["converted"].sum())

    rows = [
        {
            "metric": "Campaigns",
            "value": int(len(performance)),
        },
        {
            "metric": "Total Budget",
            "value": float(performance["budget"].sum()),
        },
        {
            "metric": "Contacts Sent",
            "value": sent,
        },
        {
            "metric": "Engaged Opens",
            "value": opened,
        },
        {
            "metric": "Clicks",
            "value": clicked,
        },
        {
            "metric": "Conversions",
            "value": converted,
        },
        {
            "metric": "Open Rate %",
            "value": _rate(opened, sent),
        },
        {
            "metric": "Click Rate %",
            "value": _rate(clicked, sent),
        },
        {
            "metric": "Conversion Rate %",
            "value": _rate(converted, sent),
        },
    ]

    return pd.DataFrame(rows)


def build_lead_export(
    contacts: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare a clean lead-scoring export.
    """

    if contacts.empty:
        return pd.DataFrame()

    columns = [
        "contact_id",
        "first_name",
        "last_name",
        "email",
        "account_id",
        "job_title",
        "country",
        "region",
        "industry",
        "lifecycle_stage",
        "lead_score",
        "engagement_score",
        "consent_status",
    ]

    available = [
        column
        for column in columns
        if column in contacts.columns
    ]

    result = contacts[available].copy()

    if "lead_score" in result.columns:
        result = result.sort_values(
            "lead_score",
            ascending=False,
        )

    return result


def export_campaignos_workbook(
    output_path: str | Path,
    campaigns: pd.DataFrame,
    activities: pd.DataFrame,
    contacts: pd.DataFrame,
) -> Path:
    """
    Create a multi-sheet CampaignOS Excel workbook.
    """

    output = Path(output_path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    performance = build_campaign_performance(
        campaigns,
        activities,
    )

    regional = build_regional_performance(
        performance,
    )

    executive = build_executive_summary(
        performance,
    )

    leads = build_lead_export(
        contacts,
    )

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        executive.to_excel(
            writer,
            sheet_name="Executive Summary",
            index=False,
        )

        performance.to_excel(
            writer,
            sheet_name="Campaign Performance",
            index=False,
        )

        regional.to_excel(
            writer,
            sheet_name="Regional Performance",
            index=False,
        )

        leads.to_excel(
            writer,
            sheet_name="Lead Export",
            index=False,
        )

    return output
