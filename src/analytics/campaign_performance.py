from typing import Dict, List

import pandas as pd


FUNNEL_EVENTS = {
    "sent": "Email Sent",
    "opened": "Email Opened",
    "clicked": "Email Clicked",
    "converted": "Form Submitted",
}


def _unique_contacts(
    activities: pd.DataFrame,
    activity_type: str,
) -> int:
    """Return unique contacts for a specific activity type."""
    if activities.empty:
        return 0

    filtered = activities[
        activities["activity_type"] == activity_type
    ]

    if filtered.empty:
        return 0

    return int(filtered["contact_id"].nunique())


def _rate(
    numerator: int,
    denominator: int,
) -> float:
    """Return a safe percentage rate."""
    if denominator <= 0:
        return 0.0

    return round((numerator / denominator) * 100, 2)


def calculate_funnel_metrics(
    activities: pd.DataFrame,
) -> Dict[str, float]:
    """
    Calculate the overall campaign engagement funnel.

    Funnel:
        Sent → Opened → Clicked → Converted
    """
    sent = _unique_contacts(
        activities,
        FUNNEL_EVENTS["sent"],
    )

    opened = _unique_contacts(
        activities,
        FUNNEL_EVENTS["opened"],
    )

    clicked = _unique_contacts(
        activities,
        FUNNEL_EVENTS["clicked"],
    )

    converted = _unique_contacts(
        activities,
        FUNNEL_EVENTS["converted"],
    )

    return {
        "sent": sent,
        "opened": opened,
        "clicked": clicked,
        "converted": converted,
        "open_rate": _rate(opened, sent),
        "click_rate": _rate(clicked, sent),
        "click_to_open_rate": _rate(clicked, opened),
        "conversion_rate": _rate(converted, sent),
        "conversion_from_click_rate": _rate(
            converted,
            clicked,
        ),
    }


def campaign_performance(
    campaigns: pd.DataFrame,
    activities: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate campaign-level performance metrics.

    Metrics are based on unique contacts performing
    each activity for each campaign.
    """
    if campaigns.empty:
        return pd.DataFrame()

    rows: List[Dict] = []

    for _, campaign in campaigns.iterrows():
        campaign_id = campaign["campaign_id"]

        campaign_activities = activities[
            activities["campaign_id"] == campaign_id
        ]

        sent = _unique_contacts(
            campaign_activities,
            FUNNEL_EVENTS["sent"],
        )

        opened = _unique_contacts(
            campaign_activities,
            FUNNEL_EVENTS["opened"],
        )

        clicked = _unique_contacts(
            campaign_activities,
            FUNNEL_EVENTS["clicked"],
        )

        converted = _unique_contacts(
            campaign_activities,
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
                "sent": sent,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
                "open_rate": _rate(opened, sent),
                "click_rate": _rate(clicked, sent),
                "click_to_open_rate": _rate(
                    clicked,
                    opened,
                ),
                "conversion_rate": _rate(
                    converted,
                    sent,
                ),
                "conversion_from_click_rate": _rate(
                    converted,
                    clicked,
                ),
            }
        )

    return pd.DataFrame(rows)


def regional_performance(
    contacts: pd.DataFrame,
    activities: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate engagement and conversion performance
    by global marketing region.
    """
    if contacts.empty or activities.empty:
        return pd.DataFrame()

    required_contact_columns = {
        "contact_id",
        "region",
    }

    required_activity_columns = {
        "contact_id",
        "activity_type",
    }

    if not required_contact_columns.issubset(
        contacts.columns
    ):
        return pd.DataFrame()

    if not required_activity_columns.issubset(
        activities.columns
    ):
        return pd.DataFrame()

    activity_data = activities.merge(
        contacts[
            [
                "contact_id",
                "region",
            ]
        ],
        on="contact_id",
        how="left",
    )

    rows: List[Dict] = []

    for region, region_data in activity_data.groupby(
        "region",
        dropna=False,
    ):
        sent = _unique_contacts(
            region_data,
            FUNNEL_EVENTS["sent"],
        )

        opened = _unique_contacts(
            region_data,
            FUNNEL_EVENTS["opened"],
        )

        clicked = _unique_contacts(
            region_data,
            FUNNEL_EVENTS["clicked"],
        )

        converted = _unique_contacts(
            region_data,
            FUNNEL_EVENTS["converted"],
        )

        rows.append(
            {
                "region": (
                    str(region)
                    if pd.notna(region)
                    else "Unknown"
                ),
                "sent": sent,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
                "open_rate": _rate(
                    opened,
                    sent,
                ),
                "click_rate": _rate(
                    clicked,
                    sent,
                ),
                "conversion_rate": _rate(
                    converted,
                    sent,
                ),
            }
        )

    result = pd.DataFrame(rows)

    if not result.empty:
        result = result.sort_values(
            "conversion_rate",
            ascending=False,
        ).reset_index(drop=True)

    return result


def channel_performance(
    activities: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate activity volume by marketing channel.
    """
    if activities.empty:
        return pd.DataFrame()

    if not {
        "channel",
        "activity_type",
        "contact_id",
    }.issubset(activities.columns):
        return pd.DataFrame()

    rows: List[Dict] = []

    for channel, channel_data in activities.groupby(
        "channel",
        dropna=False,
    ):
        sent = _unique_contacts(
            channel_data,
            FUNNEL_EVENTS["sent"],
        )

        opened = _unique_contacts(
            channel_data,
            FUNNEL_EVENTS["opened"],
        )

        clicked = _unique_contacts(
            channel_data,
            FUNNEL_EVENTS["clicked"],
        )

        converted = _unique_contacts(
            channel_data,
            FUNNEL_EVENTS["converted"],
        )

        rows.append(
            {
                "channel": (
                    str(channel)
                    if pd.notna(channel)
                    else "Unknown"
                ),
                "sent": sent,
                "opened": opened,
                "clicked": clicked,
                "converted": converted,
                "open_rate": _rate(
                    opened,
                    sent,
                ),
                "click_rate": _rate(
                    clicked,
                    sent,
                ),
                "conversion_rate": _rate(
                    converted,
                    sent,
                ),
            }
        )

    result = pd.DataFrame(rows)

    if not result.empty:
        result = result.sort_values(
            "converted",
            ascending=False,
        ).reset_index(drop=True)

    return result


def top_campaigns(
    performance: pd.DataFrame,
    metric: str = "conversion_rate",
    limit: int = 10,
) -> pd.DataFrame:
    """Return the top campaigns for a selected metric."""
    if performance.empty:
        return pd.DataFrame()

    if metric not in performance.columns:
        raise ValueError(
            f"Unknown performance metric: {metric}"
        )

    return (
        performance.sort_values(
            metric,
            ascending=False,
        )
        .head(limit)
        .reset_index(drop=True)
    )


def executive_insights(
    performance: pd.DataFrame,
    regional: pd.DataFrame,
) -> List[str]:
    """
    Generate concise management-level insights
    from campaign and regional performance.
    """
    insights: List[str] = []

    if performance.empty:
        insights.append(
            "No campaign performance data is available."
        )
        return insights

    best_campaign = performance.loc[
        performance["conversion_rate"].idxmax()
    ]

    insights.append(
        f"Top conversion campaign: "
        f"{best_campaign['campaign_name']} "
        f"({best_campaign['conversion_rate']:.2f}% "
        f"conversion rate)."
    )

    best_open_campaign = performance.loc[
        performance["open_rate"].idxmax()
    ]

    insights.append(
        f"Strongest engagement campaign: "
        f"{best_open_campaign['campaign_name']} "
        f"({best_open_campaign['open_rate']:.2f}% "
        f"open rate)."
    )

    if not regional.empty:
        best_region = regional.iloc[0]

        insights.append(
            f"Leading region by conversion rate: "
            f"{best_region['region']} "
            f"({best_region['conversion_rate']:.2f}%)."
        )

        lowest_region = regional.loc[
            regional["conversion_rate"].idxmin()
        ]

        insights.append(
            f"Lowest regional conversion rate: "
            f"{lowest_region['region']} "
            f"({lowest_region['conversion_rate']:.2f}%)."
        )

    total_budget = performance["budget"].sum()

    insights.append(
        f"Portfolio campaign budget represented: "
        f"{total_budget:,.0f}."
    )

    return insights


def campaign_summary(
    performance: pd.DataFrame,
) -> Dict[str, float]:
    """Return executive KPI totals for the campaign portfolio."""
    if performance.empty:
        return {
            "campaigns": 0,
            "budget": 0.0,
            "sent": 0,
            "opened": 0,
            "clicked": 0,
            "converted": 0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "conversion_rate": 0.0,
        }

    sent = int(performance["sent"].sum())
    opened = int(performance["opened"].sum())
    clicked = int(performance["clicked"].sum())
    converted = int(performance["converted"].sum())

    return {
        "campaigns": int(len(performance)),
        "budget": float(performance["budget"].sum()),
        "sent": sent,
        "opened": opened,
        "clicked": clicked,
        "converted": converted,
        "open_rate": _rate(opened, sent),
        "click_rate": _rate(clicked, sent),
        "conversion_rate": _rate(
            converted,
            sent,
        ),
    }
