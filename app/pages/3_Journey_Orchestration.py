import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.loader import load_contacts
from src.scoring.engine import score_contacts
from src.segmentation.engine import build_segment
from src.segmentation.models import SegmentDefinition, SegmentRule
from src.journey.engine import (
    JourneyEngine,
    summarize_journey_states,
)
from src.journey.models import (
    Journey,
    JourneyStep,
    JourneyStatus,
    StepType,
)


st.set_page_config(
    page_title="CampaignOS | Journey Orchestration",
    page_icon="🧭",
    layout="wide",
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def build_segment_definition(
    segment_id: str,
    segment_name: str,
    field: str,
    operator: str,
    value,
) -> SegmentDefinition:
    return SegmentDefinition(
        segment_id=segment_id,
        segment_name=segment_name,
        description="CampaignOS synthetic journey audience.",
        rules=[
            SegmentRule(
                field=field,
                operator=operator,
                value=value,
            )
        ],
        logic="AND",
    )


def build_demo_journey(
    segment_name: str,
    score_threshold: int,
) -> Journey:

    journey = Journey(
        journey_id="JRN-M5-001",
        journey_name="MQL Conversion Journey",
        description=(
            "Synthetic MQL nurture and sales conversion journey."
        ),
        status=JourneyStatus.ACTIVE,
        entry_segment=segment_name,
    )

    journey.add_step(
        JourneyStep(
            step_id="entry",
            name="Audience Entry",
            step_type=StepType.ENTRY,
            next_step_id="welcome",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="welcome",
            name="Welcome Email",
            step_type=StepType.EMAIL,
            config={
                "template": "mql_welcome",
                "channel": "Email",
            },
            next_step_id="lifecycle_check",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="lifecycle_check",
            name="Lifecycle Check",
            step_type=StepType.CONDITION,
            config={
                "field": "lifecycle_stage",
                "operator": "equals",
                "value": "MQL",
            },
            true_step_id="score_check",
            false_step_id="nurture",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="score_check",
            name=f"Lead Score ≥ {score_threshold}",
            step_type=StepType.SCORE_CHECK,
            config={
                "field": "calculated_lead_score",
                "threshold": score_threshold,
            },
            true_step_id="sales",
            false_step_id="nurture",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="nurture",
            name="Nurture Email",
            step_type=StepType.EMAIL,
            config={
                "template": "targeted_nurture",
                "channel": "Email",
            },
            next_step_id="exit",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="sales",
            name="Sales Handoff",
            step_type=StepType.SALES_HANDOFF,
            config={
                "priority": "High",
            },
            next_step_id="exit",
        )
    )

    journey.add_step(
        JourneyStep(
            step_id="exit",
            name="Journey Exit",
            step_type=StepType.EXIT,
        )
    )

    return journey


def format_step(step: JourneyStep) -> str:
    icons = {
        StepType.ENTRY: "🟢",
        StepType.EMAIL: "✉️",
        StepType.WAIT: "⏳",
        StepType.CONDITION: "🔀",
        StepType.SCORE_CHECK: "🎯",
        StepType.SALES_HANDOFF: "🤝",
        StepType.EXIT: "🏁",
    }

    return f"{icons.get(step.step_type, '▪️')} {step.name}"


# ---------------------------------------------------------
# Page Header
# ---------------------------------------------------------

st.title("🧭 Journey Orchestration")

st.caption(
    "Design and simulate rule-based marketing journeys using "
    "CampaignOS segmentation, lead scoring and synthetic contacts."
)


# ---------------------------------------------------------
# Load contacts
# ---------------------------------------------------------

contacts = load_contacts()

if contacts.empty:
    st.error(
        "No synthetic contact data was found. "
        "Run the CampaignOS data generator first."
    )
    st.stop()


# ---------------------------------------------------------
# Sidebar configuration
# ---------------------------------------------------------

st.sidebar.header("Journey Configuration")

segment_field = st.sidebar.selectbox(
    "Entry Audience Field",
    options=[
        "lifecycle_stage",
        "region",
        "industry",
        "country",
        "job_title",
        "consent_status",
    ],
    index=0,
)

field_values = (
    contacts[segment_field]
    .dropna()
    .astype(str)
    .sort_values()
    .unique()
    .tolist()
)

if not field_values:
    st.error("No values available for the selected audience field.")
    st.stop()

segment_value = st.sidebar.selectbox(
    "Entry Audience Value",
    options=field_values,
)

score_threshold = st.sidebar.slider(
    "Sales Handoff Score",
    min_value=0,
    max_value=100,
    value=70,
    step=5,
)

simulate_limit = st.sidebar.slider(
    "Maximum Contacts to Simulate",
    min_value=100,
    max_value=min(2000, len(contacts)),
    value=min(500, len(contacts)),
    step=100,
)


# ---------------------------------------------------------
# Build M3 audience
# ---------------------------------------------------------

segment_definition = build_segment_definition(
    segment_id="SEG-M5-001",
    segment_name=(
        f"{segment_field} = {segment_value}"
    ),
    field=segment_field,
    operator="equals",
    value=segment_value,
)

try:
    segment_result = build_segment(
        contacts,
        segment_definition,
    )
except Exception as exc:
    st.error(f"Unable to build audience segment: {exc}")
    st.stop()


audience = segment_result.contacts.copy()


# ---------------------------------------------------------
# Apply M4 lead scoring
# ---------------------------------------------------------

if audience.empty:
    st.warning(
        "The selected audience contains no contacts."
    )
    st.stop()

scored_audience = score_contacts(audience)


# ---------------------------------------------------------
# Build M5 journey
# ---------------------------------------------------------

journey = build_demo_journey(
    segment_name=segment_definition.segment_name,
    score_threshold=score_threshold,
)

validation_errors = journey.validate()

if validation_errors:
    st.error("Journey validation failed.")

    for error in validation_errors:
        st.write(f"• {error}")

    st.stop()


engine = JourneyEngine(journey)


# ---------------------------------------------------------
# KPI summary
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Entry Audience",
    f"{len(scored_audience):,}",
)

col2.metric(
    "Average Lead Score",
    round(
        scored_audience["calculated_lead_score"].mean(),
        1,
    ),
)

col3.metric(
    "Hot Leads",
    int(
        (
            scored_audience["score_band"] == "Hot"
        ).sum()
    ),
)

col4.metric(
    "Marketable",
    int(
        (
            scored_audience["qualification"]
            != "Not Marketable"
        ).sum()
    ),
)


# ---------------------------------------------------------
# Journey flow
# ---------------------------------------------------------

st.subheader("Journey Flow")

flow_columns = st.columns(len(journey.steps))

for column, step in zip(
    flow_columns,
    journey.steps,
):
    with column:
        st.markdown(
            f"**{format_step(step)}**"
        )

        st.caption(
            step.step_type.value.replace(
                "_",
                " ",
            ).title()
        )


# ---------------------------------------------------------
# Journey logic
# ---------------------------------------------------------

st.subheader("Orchestration Logic")

logic_col1, logic_col2 = st.columns(2)

with logic_col1:
    st.markdown(
        """
### Audience Entry

The selected M3 segment becomes the journey entry audience.

```text
Segment
   ↓
Audience Entry
   ↓
Welcome Email
"""
)
with logic_col2:
    st.markdown(
    f"""
    ## Decisioning
    Contacts are evaluated using the M4 calculated lead score.
    Lifecycle = MQL
          ↓
    Score ≥ {score_threshold}
       ↙       ↘
     Sales    Nurture
    
     """
    )
# ---------------------------------------------------------
# Audience preview
# ---------------------------------------------------------
st.subheader("Entry Audience Preview")
preview_columns = [
"contact_id",
"first_name",
"last_name",
"region",
"country",
"industry",
"lifecycle_stage",
"engagement_score",
"calculated_lead_score",
"score_band",
"qualification",
]
available_preview_columns = [
column
for column in preview_columns
if column in scored_audience.columns
]
st.dataframe(
scored_audience[
available_preview_columns
].sort_values(
"calculated_lead_score",
ascending=False,
).head(25),
width="stretch",
hide_index=True,
)
# ---------------------------------------------------------
# 
# st.subheader("Journey Simulation")

st.write(
    f"Simulate up to {simulate_limit:,} contacts "
    "from the selected entry audience."
)

if st.button(
    "▶ Run Journey Simulation",
    type="primary",
):
    simulation_contacts = scored_audience.head(
        simulate_limit
    )

    states = []

    progress = st.progress(0)
    total = len(simulation_contacts)

    for index, (_, contact) in enumerate(
        simulation_contacts.iterrows(),
        start=1,
    ):
        state = engine.execute_contact(
            contact.to_dict()
        )
        states.append(state)

        progress.progress(index / total)

    progress.empty()

    summary = summarize_journey_states(states)

    st.success(
        f"Journey simulation completed for "
        f"{len(states):,} contacts."
    )

    sim_col1, sim_col2, sim_col3, sim_col4 = st.columns(4)

    sim_col1.metric(
        "Simulated",
        f"{len(states):,}",
    )

    sim_col2.metric(
        "Completed",
        f"{summary.get('Completed', 0):,}",
    )

    sales_count = sum(
        1
        for state in states
        if state.metadata.get(
            "sales_handoff",
            False,
        )
    )

    sim_col3.metric(
        "Sales Handoffs",
        f"{sales_count:,}",
    )

    sim_col4.metric(
        "Errors",
        f"{summary.get('Error', 0):,}",
    )

    st.subheader("Journey Outcomes")

    outcome_rows = []

    for state in states:
        if state.metadata.get(
            "sales_handoff",
            False,
        ):
            outcome = "Sales Handoff"
        elif "nurture" in state.history:
            outcome = "Nurture"
        else:
            outcome = "Other"

        outcome_rows.append(
            {
                "contact_id": state.contact_id,
                "outcome": outcome,
                "status": state.status,
                "steps_completed": len(state.history),
                "journey_path": " → ".join(
                    state.history
                ),
            }
        )

    outcome_df = pd.DataFrame(outcome_rows)

    if not outcome_df.empty:
        outcome_distribution = (
            outcome_df["outcome"]
            .value_counts()
            .rename_axis("Outcome")
            .reset_index(name="Contacts")
        )

        chart_col, table_col = st.columns([2, 1])

        with chart_col:
            st.bar_chart(
                outcome_distribution.set_index(
                    "Outcome"
                )
            )

        with table_col:
            st.dataframe(
                outcome_distribution,
                width="stretch",
                hide_index=True,
            )

        st.subheader("Contact Journey Paths")

        st.dataframe(
            outcome_df,
            width="stretch",
            hide_index=True,
        )

        csv_data = outcome_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Export Journey Results",
            data=csv_data,
            file_name="campaignos_journey_results.csv",
            mime="text/csv",
        )

st.subheader("Marketing Automation Design Notes")

st.markdown(
    """
**Entry Audience**

The journey begins with a dynamically evaluated
segmentation rule rather than a hard-coded contact list.

**Lifecycle Decision**

MQL contacts continue into lead-score qualification.
Other lifecycle stages are routed toward nurture.

**Lead Score Decision**

Contacts meeting the configured score threshold
receive a synthetic sales handoff.

**Nurture Path**

Lower-intent contacts remain in marketing nurture
rather than being immediately handed to sales.

**Sales Handoff**

The journey records a sales-handoff event in the
contact's journey state.

**Synthetic Execution**

No email is actually sent, no CRM record is changed,
and no external system is contacted. The engine
simulates the orchestration locally using synthetic data.
"""
)
