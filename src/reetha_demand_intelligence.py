from __future__ import annotations

from pathlib import Path

import pandas as pd


def _repo_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return Path(__file__).resolve().parents[1] / "data" / "reetha"


def load_reetha_demand_data(
    data_dir: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    root = _repo_data_dir(data_dir)
    leads = pd.read_csv(root / "leads.csv")
    engagements = pd.read_csv(root / "engagements.csv")
    courses = pd.read_csv(root / "courses.csv")
    return leads, engagements, courses


def build_demand_summary(
    leads: pd.DataFrame,
    courses: pd.DataFrame | None = None,
) -> pd.DataFrame:
    required = {"lead_id", "interest"}
    missing = required.difference(leads.columns)
    if missing:
        raise ValueError(f"Missing lead columns: {sorted(missing)}")

    work = leads.copy()

    if (
        courses is not None
        and "course_id" in work.columns
        and {"course_id", "name"}.issubset(courses.columns)
    ):
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

    # Replace opaque synthetic CRS-* labels with catalogue names.
    opaque = interest.str.fullmatch(r"CRS-\d+", case=False, na=False)

    work["demand_signal"] = interest.where(~opaque, offering)
    work["demand_signal"] = (
        work["demand_signal"]
        .replace("", pd.NA)
        .fillna(offering)
        .replace("", pd.NA)
        .fillna("Unspecified")
    )

    return (
        work.groupby("demand_signal", as_index=False)
        .agg(interested_leads=("lead_id", "nunique"))
        .sort_values(
            ["interested_leads", "demand_signal"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )


def build_location_and_experience_note(
    leads: pd.DataFrame,
) -> tuple[str, str]:
    normalized = {c.lower().replace(" ", "_") for c in leads.columns}

    experience = (
        "Synthetic dataset contains an experience field."
        if "total_exp" in normalized
        else "Available when real Total Exp data is connected."
    )

    location = (
        "Synthetic dataset contains a work-location field."
        if "work_location" in normalized
        else "Available when real Work Location data is connected."
    )

    return experience, location


def render_reetha_demand_intelligence() -> None:
    import streamlit as st

    leads, engagements, courses = load_reetha_demand_data()
    demand = build_demand_summary(leads, courses)

    st.markdown("## SAP Demand Intelligence")
    st.caption(
        "M13.2 · Controlled demand view using the existing Reetha synthetic "
        "lead dataset. Real personal lead records are not loaded."
    )

    st.info(
        "DEMO / SYNTHETIC DATA: opaque course IDs are resolved through the "
        "existing Reetha course catalogue. Real SAP Domain, Total Exp and "
        "Work Location values can be connected later."
    )

    total_leads = int(leads["lead_id"].nunique())
    demand_categories = int(demand["demand_signal"].nunique())
    engaged_leads = (
        int(engagements["lead_id"].nunique())
        if "lead_id" in engagements.columns
        else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Leads", total_leads)
    c2.metric("Demand Signals", demand_categories)
    c3.metric("Engaged Leads", engaged_leads)

    st.markdown("### Demand by Offering / Interest")

    display = demand.rename(
        columns={
            "demand_signal": "Demand / Offering",
            "interested_leads": "Interested Leads",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Reetha Data Readiness")

    r1, r2, r3 = st.columns(3)
    r1.metric("SAP Domain", "Awaiting authorized source")
    r2.metric("Total Exp", "Awaiting authorized source")
    r3.metric("Work Location", "Awaiting authorized source")

    st.caption(
        "Future segmentation: SAP Domain → Total Exp → Work Location → "
        "Offering match."
    )

    experience_note, location_note = build_location_and_experience_note(leads)
    st.caption(experience_note)
    st.caption(location_note)

    st.markdown("### Demand → Offering Opportunity")
    st.markdown(
        "**Demand signal → Reetha offering catalogue → Target audience → "
        "Campaign opportunity → Next Best Action**"
    )
