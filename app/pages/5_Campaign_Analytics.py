import sys
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from src.analytics.campaign_performance import (
    campaign_performance,
    campaign_summary,
    channel_performance,
    executive_insights,
    regional_performance,
    top_campaigns,
)
from src.data.loader import (
    load_activities,
    load_campaigns,
    load_contacts,
)


st.set_page_config(
    page_title="CampaignOS | Campaign Analytics",
    page_icon="📊",
    layout="wide",
)


st.title("📊 Campaign Analytics & Regional Reporting")

st.caption(
    "Measure campaign performance, engagement funnels, "
    "regional outcomes and executive-level marketing insights "
    "using CampaignOS synthetic data."
)


campaigns = load_campaigns()
activities = load_activities()
contacts = load_contacts()


if (
    campaigns.empty
    or activities.empty
    or contacts.empty
):
    st.error(
        "Required synthetic campaign, activity or contact data "
        "is unavailable."
    )
    st.stop()


st.sidebar.header("Analytics Filters")


regions = sorted(
    campaigns["region"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

region_options = ["All Regions"] + regions

selected_region = st.sidebar.selectbox(
    "Region",
    region_options,
)


statuses = sorted(
    campaigns["status"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

status_options = ["All Statuses"] + statuses

selected_status = st.sidebar.selectbox(
    "Campaign Status",
    status_options,
)


business_types = sorted(
    campaigns["business_type"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

business_options = [
    "All Business Types"
] + business_types

selected_business = st.sidebar.selectbox(
    "Business Type",
    business_options,
)


filtered_campaigns = campaigns.copy()


if selected_region != "All Regions":
    filtered_campaigns = filtered_campaigns[
        filtered_campaigns["region"]
        == selected_region
    ]


if selected_status != "All Statuses":
    filtered_campaigns = filtered_campaigns[
        filtered_campaigns["status"]
        == selected_status
    ]


if selected_business != "All Business Types":
    filtered_campaigns = filtered_campaigns[
        filtered_campaigns["business_type"]
        == selected_business
    ]


campaign_ids = set(
    filtered_campaigns["campaign_id"]
)


filtered_activities = activities[
    activities["campaign_id"].isin(
        campaign_ids
    )
].copy()


performance = campaign_performance(
    filtered_campaigns,
    filtered_activities,
)


regional = regional_performance(
    contacts,
    filtered_activities,
)


channels = channel_performance(
    filtered_activities,
)


summary = campaign_summary(
    performance
)


st.subheader("Executive KPI Summary")


kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


kpi1.metric(
    "Campaigns",
    f"{summary['campaigns']:,}",
)


kpi2.metric(
    "Budget",
    f"{summary['budget']:,.0f}",
)


kpi3.metric(
    "Engaged Opens",
    f"{summary['opened']:,}",
)


kpi4.metric(
    "Clicks",
    f"{summary['clicked']:,}",
)


kpi5.metric(
    "Conversions",
    f"{summary['converted']:,}",
)


st.subheader("Portfolio Funnel")


funnel_col1, funnel_col2, funnel_col3, funnel_col4 = (
    st.columns(4)
)


funnel_col1.metric(
    "Sent",
    f"{summary['sent']:,}",
)


funnel_col2.metric(
    "Open Rate",
    f"{summary['open_rate']:.2f}%",
)


funnel_col3.metric(
    "Click Rate",
    f"{summary['click_rate']:.2f}%",
)


funnel_col4.metric(
    "Conversion Rate",
    f"{summary['conversion_rate']:.2f}%",
)


if not performance.empty:

    st.subheader("Campaign Performance")


    display_columns = [
        "campaign_name",
        "business_type",
        "region",
        "objective",
        "status",
        "budget",
        "sent",
        "opened",
        "clicked",
        "converted",
        "open_rate",
        "click_rate",
        "conversion_rate",
    ]


    available_columns = [
        column
        for column in display_columns
        if column in performance.columns
    ]


    performance_display = performance[
        available_columns
    ].copy()


    st.dataframe(
        performance_display,
        width="stretch",
        hide_index=True,
    )


    st.subheader("Top Campaigns")


    top_metric = st.selectbox(
        "Rank campaigns by",
        [
            "conversion_rate",
            "open_rate",
            "click_rate",
            "converted",
        ],
    )


    top_n = st.slider(
        "Number of campaigns",
        min_value=3,
        max_value=min(
            10,
            len(performance),
        ),
        value=min(
            5,
            len(performance),
        ),
    )


    top_df = top_campaigns(
        performance,
        metric=top_metric,
        limit=top_n,
    )


    if not top_df.empty:

        chart_data = top_df[
            [
                "campaign_name",
                top_metric,
            ]
        ].set_index(
            "campaign_name"
        )


        st.bar_chart(
            chart_data
        )


st.subheader("Regional Performance")


if not regional.empty:

    regional_col1, regional_col2 = st.columns(
        [2, 1]
    )


    with regional_col1:

        regional_chart = regional[
            [
                "region",
                "conversion_rate",
            ]
        ].set_index(
            "region"
        )


        st.bar_chart(
            regional_chart
        )


    with regional_col2:

        st.dataframe(
            regional,
            width="stretch",
            hide_index=True,
        )

else:

    st.info(
        "No regional performance data is available "
        "for the selected filters."
    )


st.subheader("Channel Performance")


if not channels.empty:

    channel_col1, channel_col2 = st.columns(
        [2, 1]
    )


    with channel_col1:

        channel_chart = channels[
            [
                "channel",
                "converted",
            ]
        ].set_index(
            "channel"
        )


        st.bar_chart(
            channel_chart
        )


    with channel_col2:

        st.dataframe(
            channels,
            width="stretch",
            hide_index=True,
        )

else:

    st.info(
        "No channel performance data is available."
    )


st.subheader("Executive Insights")


insights = executive_insights(
    performance,
    regional,
)


for insight in insights:

    st.info(
        f"💡 {insight}"
    )


st.subheader("Campaign Management View")


management_col1, management_col2 = st.columns(2)


with management_col1:

    if not performance.empty:

        status_summary = (
            performance["status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(
                name="Campaigns"
            )
        )


        st.markdown(
            "### Campaign Status"
        )


        st.dataframe(
            status_summary,
            width="stretch",
            hide_index=True,
        )


with management_col2:

    if not performance.empty:

        objective_summary = (
            performance.groupby(
                "objective",
                as_index=False,
            )[
                "converted"
            ]
            .sum()
            .sort_values(
                "converted",
                ascending=False,
            )
        )


        st.markdown(
            "### Conversions by Objective"
        )


        st.dataframe(
            objective_summary,
            width="stretch",
            hide_index=True,
        )


st.subheader("Export Analytics")


export_df = performance.copy()


if not regional.empty:

    regional_export = regional.copy()

else:

    regional_export = pd.DataFrame()


campaign_csv = export_df.to_csv(
    index=False
).encode(
    "utf-8"
)


st.download_button(
    label="⬇️ Export Campaign Performance CSV",
    data=campaign_csv,
    file_name="campaignos_campaign_performance.csv",
    mime="text/csv",
    width="stretch",
)


if not regional_export.empty:

    regional_csv = regional_export.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    st.download_button(
        label="⬇️ Export Regional Performance CSV",
        data=regional_csv,
        file_name="campaignos_regional_performance.csv",
        mime="text/csv",
        width="stretch",
    )


st.divider()


st.subheader(
    "Marketing Operations Design Notes"
)


st.markdown(
    """
### Campaign Performance

CampaignOS measures the campaign funnel from:

**Email Sent → Email Opened → Email Clicked → Form Submitted**

The metrics are calculated from synthetic activity records
and unique contacts rather than raw event-row counts.

### Regional Reporting

Performance can be reviewed across global marketing regions
such as WW, AMEA, APAC and Europe.

This supports regional campaign operations and management
reporting without connecting to a proprietary marketing
automation platform.

### Channel Analysis

Marketing activity is grouped by channel so campaign teams
can understand where engagement and conversion activity is
being generated.

### Executive Reporting

CampaignOS converts operational activity into management
signals including:

- strongest campaign
- strongest engagement
- leading region
- lowest regional conversion
- portfolio budget representation

### Synthetic-Only Architecture

No real emails are sent.

No CRM records are updated.

No Oracle Eloqua, Salesforce, Outlook or other external
business system is contacted.

All reporting is generated locally from CampaignOS synthetic
data.
"""
)
