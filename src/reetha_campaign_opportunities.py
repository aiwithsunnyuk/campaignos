from __future__ import annotations

from pathlib import Path

import pandas as pd


def _repo_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return Path(__file__).resolve().parents[1] / "data" / "reetha"


def load_reetha_opportunity_data(data_dir: Path | None = None) -> tuple[pd.DataFrame, ...]:
    root = _repo_data_dir(data_dir)
    return (
        pd.read_csv(root / "leads.csv"),
        pd.read_csv(root / "courses.csv"),
        pd.read_csv(root / "engagements.csv"),
        pd.read_csv(root / "campaigns.csv"),
        pd.read_csv(root / "registrations.csv"),
        pd.read_csv(root / "enrollments.csv"),
    )


def build_campaign_opportunities(
    leads: pd.DataFrame,
    courses: pd.DataFrame,
    engagements: pd.DataFrame,
    campaigns: pd.DataFrame,
    registrations: pd.DataFrame,
    enrollments: pd.DataFrame,
) -> pd.DataFrame:
    """Turn existing demand into explainable campaign opportunities.

    Recommendation-only. No external campaign execution occurs.
    """
    required = {"lead_id", "interest"}
    missing = required.difference(leads.columns)
    if missing:
        raise ValueError(f"Missing lead columns: {sorted(missing)}")

    work = leads.copy()

    if "course_id" in work.columns and {"course_id", "name"}.issubset(courses.columns):
        catalogue = (
            courses[["course_id", "name"]]
            .dropna(subset=["course_id"])
            .drop_duplicates("course_id")
            .rename(columns={"name": "offering_name"})
        )
        work = work.merge(catalogue, on="course_id", how="left")
    else:
        work["offering_name"] = pd.NA

    interest = work["interest"].fillna("").astype(str).str.strip()
    offering = work["offering_name"].fillna("").astype(str).str.strip()
    opaque = interest.str.fullmatch(r"CRS-\d+", case=False, na=False)

    work["demand_signal"] = (
        interest.where(~opaque, offering)
        .replace("", pd.NA)
        .fillna(offering)
        .replace("", pd.NA)
        .fillna("Unspecified")
    )

    def ids(frame: pd.DataFrame) -> set[str]:
        if "lead_id" not in frame.columns:
            return set()
        return set(frame["lead_id"].dropna().astype(str).unique())

    engaged, registered, enrolled = ids(engagements), ids(registrations), ids(enrollments)

    rows = []
    for signal, group in work.groupby("demand_signal", dropna=False):
        lead_ids = set(group["lead_id"].dropna().astype(str))
        interested = len(lead_ids)
        if not interested:
            continue

        engaged_count = len(lead_ids & engaged)
        registered_count = len(lead_ids & registered)
        enrolled_count = len(lead_ids & enrolled)
        registration_gap = max(interested - registered_count, 0)

        engagement_rate = engaged_count / interested
        gap_rate = registration_gap / interested
        opportunity_score = round((0.55 * engagement_rate + 0.45 * gap_rate) * 100, 1)

        if registered_count == 0:
            action = "Launch targeted campaign"
        elif registered_count < interested:
            action = "Prioritize registration conversion"
        else:
            action = "Nurture and expand"

        rows.append({
            "demand_signal": signal,
            "interested_leads": interested,
            "engaged_leads": engaged_count,
            "registered_leads": registered_count,
            "enrolled_leads": enrolled_count,
            "registration_gap": registration_gap,
            "opportunity_score": opportunity_score,
            "recommended_action": action,
        })

    columns = [
        "demand_signal", "interested_leads", "engaged_leads",
        "registered_leads", "enrolled_leads", "registration_gap",
        "opportunity_score", "recommended_action",
    ]
    if not rows:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(rows).sort_values(
        ["opportunity_score", "interested_leads"],
        ascending=[False, False],
    ).reset_index(drop=True)


def render_campaign_opportunity_engine() -> None:
    import streamlit as st

    data = load_reetha_opportunity_data()
    opportunities = build_campaign_opportunities(*data)

    st.markdown("## AI Campaign Opportunity Engine")
    st.caption(
        "M13.3 · Recommendation layer connecting existing demand signals "
        "to Reetha campaign opportunities. No external execution occurs."
    )
    st.info(
        "DEMO / SYNTHETIC DATA: CampaignOS identifies opportunities from the "
        "controlled Reetha dataset. Personal lead records are not displayed."
    )

    if opportunities.empty:
        st.warning("No campaign opportunities can be derived from the current dataset.")
        return

    top = opportunities.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Opportunities", len(opportunities))
    c2.metric("Top Demand", str(top["demand_signal"]))
    c3.metric("Interested Leads", int(top["interested_leads"]))
    c4.metric("Registration Gap", int(top["registration_gap"]))

    st.markdown("### AI-Recommended Campaign Opportunities")
    display = opportunities.rename(columns={
        "demand_signal": "Demand / Offering",
        "interested_leads": "Interested",
        "engaged_leads": "Engaged",
        "registered_leads": "Registered",
        "enrolled_leads": "Enrolled",
        "registration_gap": "Registration Gap",
        "opportunity_score": "Opportunity Score",
        "recommended_action": "Recommended Action",
    })
    st.dataframe(display.head(12), use_container_width=True, hide_index=True)

    st.markdown("### Recommended Next Campaign")
    st.success(
        f"**{top['recommended_action']}** for **{top['demand_signal']}**. "
        f"{int(top['interested_leads'])} interested leads, "
        f"{int(top['engaged_leads'])} engaged, "
        f"{int(top['registered_leads'])} registered, "
        f"{int(top['registration_gap'])} registration gap."
    )
    st.caption(
        "Next stage: turn an approved opportunity into an audience, campaign "
        "brief, content package and governed execution plan."
    )
