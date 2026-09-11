import streamlit as st
from datetime import date

from src.campaign.planner import create_campaign


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="CampaignOS | Campaign Planner",
    page_icon="🎯",
    layout="wide",
)


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

BUSINESS_TYPES = [
    "Professional Information Services",
    "Training & Education",
    "Farming Machinery",
    "Event Decoration",
    "Legal Services",
    "SAP Training",
]

REGIONS = [
    "WW",
    "APAC",
    "AMEA",
    "Europe",
]

OBJECTIVES = [
    "Lead Generation",
    "Brand Awareness",
    "Product Promotion",
    "Event Registration",
    "Customer Engagement",
    "Upsell / Cross-sell",
]

STATUSES = [
    "Planning",
    "Scheduled",
    "Running",
    "Paused",
    "Completed",
]

CHANNELS = [
    "Email",
    "Web",
    "LinkedIn",
    "Search",
    "Webinar",
    "Social",
]

PRODUCTS = [
    "Professional Information Subscription",
    "DevOps Leadership Program",
    "Agentic AI Practitioner",
    "Gen AI Accelerator",
    "Azure DevOps Bootcamp",
    "PMP Certification Program",
    "AI Scrum Master & Product Owner",
    "Smart Farm Equipment Demo",
    "Event Decoration Package",
    "SAP S/4HANA Training",
]


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "planned_campaigns" not in st.session_state:
    st.session_state.planned_campaigns = []


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🎯 Campaign Planner")

st.markdown(
    """
    **Design, validate and preview a marketing campaign before activation.**

    CampaignOS models the planning concepts commonly found in
    enterprise marketing-automation platforms while remaining
    vendor-neutral and using synthetic data only.
    """
)

st.divider()


# ---------------------------------------------------------
# Campaign identification
# ---------------------------------------------------------

st.subheader("1. Campaign Identification")

col1, col2 = st.columns(2)

with col1:
    campaign_id = st.text_input(
        "Campaign ID",
        value=f"CMP-{len(st.session_state.planned_campaigns) + 1:03d}",
        help="Unique identifier for the campaign.",
    )

    campaign_name = st.text_input(
        "Campaign Name",
        placeholder="e.g. APAC Agentic AI Leadership Campaign",
    )

with col2:
    business_type = st.selectbox(
        "Business Type",
        BUSINESS_TYPES,
    )

    product_name = st.selectbox(
        "Product / Offering",
        PRODUCTS,
    )


# ---------------------------------------------------------
# Strategy
# ---------------------------------------------------------

st.subheader("2. Campaign Strategy")

col1, col2, col3 = st.columns(3)

with col1:
    region = st.selectbox(
        "Target Region",
        REGIONS,
    )

with col2:
    objective = st.selectbox(
        "Campaign Objective",
        OBJECTIVES,
    )

with col3:
    status = st.selectbox(
        "Campaign Status",
        STATUSES,
    )


# ---------------------------------------------------------
# Campaign timeline
# ---------------------------------------------------------

st.subheader("3. Campaign Timeline")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=date.today(),
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
    )


# ---------------------------------------------------------
# Campaign economics
# ---------------------------------------------------------

st.subheader("4. Campaign Economics")

col1, col2 = st.columns(2)

with col1:
    target_mqls = st.number_input(
        "Target MQLs",
        min_value=0,
        value=250,
        step=10,
        help="Marketing Qualified Lead target.",
    )

with col2:
    budget = st.number_input(
        "Campaign Budget",
        min_value=0.0,
        value=125000.0,
        step=5000.0,
        format="%.2f",
        help="Planned campaign budget.",
    )


# ---------------------------------------------------------
# Channels
# ---------------------------------------------------------

st.subheader("5. Activation Channels")

selected_channels = st.multiselect(
    "Select campaign channels",
    CHANNELS,
    default=["Email", "Web"],
)

owner = st.text_input(
    "Campaign Owner",
    value="Regional Marketing",
)


# ---------------------------------------------------------
# Live campaign economics preview
# ---------------------------------------------------------

st.subheader("6. Campaign Economics Preview")

duration_days = 0
budget_per_mql = 0.0

if end_date >= start_date:
    duration_days = (end_date - start_date).days + 1

if target_mqls > 0:
    budget_per_mql = budget / target_mqls

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric(
    "Campaign Duration",
    f"{duration_days} days",
)

metric2.metric(
    "Target MQLs",
    f"{target_mqls:,}",
)

metric3.metric(
    "Budget",
    f"{budget:,.0f}",
)

metric4.metric(
    "Budget / MQL",
    f"{budget_per_mql:,.2f}",
)


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

validation_errors = []

if not campaign_id.strip():
    validation_errors.append("Campaign ID is required.")

if not campaign_name.strip():
    validation_errors.append("Campaign Name is required.")

if end_date < start_date:
    validation_errors.append("End Date cannot be before Start Date.")

if target_mqls < 0:
    validation_errors.append("Target MQLs cannot be negative.")

if budget < 0:
    validation_errors.append("Budget cannot be negative.")

if not selected_channels:
    validation_errors.append("At least one campaign channel must be selected.")


# ---------------------------------------------------------
# Campaign preview
# ---------------------------------------------------------

st.subheader("7. Campaign Preview")

preview_col1, preview_col2 = st.columns(2)

with preview_col1:
    st.markdown("### Campaign Summary")

    st.write(f"**Campaign ID:** {campaign_id}")
    st.write(f"**Campaign Name:** {campaign_name or 'Not specified'}")
    st.write(f"**Business Type:** {business_type}")
    st.write(f"**Product:** {product_name}")
    st.write(f"**Region:** {region}")
    st.write(f"**Objective:** {objective}")

with preview_col2:
    st.markdown("### Execution Summary")

    st.write(f"**Status:** {status}")
    st.write(f"**Start Date:** {start_date}")
    st.write(f"**End Date:** {end_date}")
    st.write(f"**Target MQLs:** {target_mqls:,}")
    st.write(f"**Channels:** {', '.join(selected_channels) if selected_channels else 'None'}")
    st.write(f"**Owner:** {owner or 'Not specified'}")


# ---------------------------------------------------------
# Validation messages
# ---------------------------------------------------------

if validation_errors:
    st.warning("Please resolve the following before creating the campaign:")

    for error in validation_errors:
        st.write(f"• {error}")


# ---------------------------------------------------------
# Create campaign
# ---------------------------------------------------------

st.divider()

create_col, clear_col = st.columns([1, 5])

with create_col:
    create_button = st.button(
        "🚀 Create Campaign",
        type="primary",
        use_container_width=True,
    )

with clear_col:
    if st.session_state.planned_campaigns:
        st.caption(
            f"{len(st.session_state.planned_campaigns)} campaign(s) "
            "created during this session."
        )


if create_button:

    if validation_errors:
        st.error("Campaign creation blocked. Fix the validation errors above.")

    else:
        try:
            campaign = create_campaign(
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                business_type=business_type,
                product_name=product_name,
                region=region,
                objective=objective,
                status=status,
                start_date=start_date,
                end_date=end_date,
                target_mqls=target_mqls,
                budget=budget,
                channels=selected_channels,
                owner=owner,
            )

            st.session_state.planned_campaigns.append(campaign)

            st.success(
                f"Campaign '{campaign.campaign_name}' created successfully."
            )

            st.balloons()

            st.markdown("### Created Campaign")

            result_col1, result_col2, result_col3 = st.columns(3)

            with result_col1:
                st.metric(
                    "Campaign",
                    campaign.campaign_id,
                )

            with result_col2:
                st.metric(
                    "Duration",
                    f"{campaign.duration_days} days",
                )

            with result_col3:
                st.metric(
                    "Budget / MQL",
                    f"{campaign.budget_per_target_mql:,.2f}",
                )

        except ValueError as exc:
            st.error(f"Campaign validation failed: {exc}")

        except Exception as exc:
            st.error(
                "Unexpected error while creating campaign. "
                f"Details: {exc}"
            )


# ---------------------------------------------------------
# Session campaign register
# ---------------------------------------------------------

if st.session_state.planned_campaigns:

    st.divider()

    st.subheader("8. Session Campaign Register")

    campaign_rows = []

    for campaign in st.session_state.planned_campaigns:
        campaign_rows.append(
            {
                "Campaign ID": campaign.campaign_id,
                "Campaign Name": campaign.campaign_name,
                "Business Type": campaign.business_type,
                "Product": campaign.product_name,
                "Region": campaign.region,
                "Objective": campaign.objective,
                "Status": campaign.status,
                "Start": campaign.start_date,
                "End": campaign.end_date,
                "Duration": campaign.duration_days,
                "Target MQLs": campaign.target_mqls,
                "Budget": campaign.budget,
                "Budget / MQL": campaign.budget_per_target_mql,
                "Channels": ", ".join(campaign.channels),
                "Owner": campaign.owner,
            }
        )

    st.dataframe(
        campaign_rows,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Portfolio planning note
# ---------------------------------------------------------

st.divider()

st.info(
    """
    **CampaignOS planning principle:** campaign creation is separated
    from audience selection, journey orchestration, content production,
    execution and analytics.

    This separation allows the same campaign model to support different
    business scenarios such as professional information services,
    training programs, farming machinery, event decoration, legal
    services and SAP training.
    """
)
