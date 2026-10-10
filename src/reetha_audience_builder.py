from __future__ import annotations

from pathlib import Path

import pandas as pd


AUDIENCE_SEGMENTS = (
    "Direct Fit",
    "Adjacent Fit",
    "Career Transformation",
    "Fresher / Career Entry",
    "Experienced Upskiller",
    "Referral Opportunity",
)


def _repo_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return Path(__file__).resolve().parents[1] / "data" / "reetha"


def load_reetha_audience_data(data_dir: Path | None = None) -> tuple[pd.DataFrame, ...]:
    root = _repo_data_dir(data_dir)
    return (
        pd.read_csv(root / "leads.csv"),
        pd.read_csv(root / "courses.csv"),
        pd.read_csv(root / "engagements.csv"),
        pd.read_csv(root / "registrations.csv"),
        pd.read_csv(root / "enrollments.csv"),
    )


def _ids(frame: pd.DataFrame) -> set[str]:
    if "lead_id" not in frame.columns:
        return set()
    return set(frame["lead_id"].dropna().astype(str).unique())


def _normalise(value: object) -> str:
    return str(value).strip().lower() if pd.notna(value) else ""


def _classify_segment(row: pd.Series, direct_signal: bool) -> str:
    lifecycle = _normalise(row.get("lifecycle_stage", ""))
    source = _normalise(row.get("source", ""))
    interest = _normalise(row.get("interest", ""))
    total_exp = _normalise(row.get("total_experience", row.get("total_exp", "")))
    domain = _normalise(row.get("domain_experience", row.get("domain", "")))

    if "refer" in source or "referr" in lifecycle:
        return "Referral Opportunity"

    fresher_terms = {"fresher", "student", "graduate", "entry level", "entry-level"}
    if lifecycle in fresher_terms or total_exp in {"0", "0 years", "fresher"}:
        return "Fresher / Career Entry"

    transformation_terms = {
        "career transformation", "career switch", "reskill",
        "career change", "career transition"
    }
    if any(term in lifecycle or term in interest for term in transformation_terms):
        return "Career Transformation"

    if direct_signal:
        return "Direct Fit"

    experienced_terms = {
        "experienced", "professional", "senior", "mid", "manager",
        "3+", "5+", "6+", "10+"
    }
    if any(term in total_exp for term in experienced_terms) or domain:
        return "Experienced Upskiller"

    return "Adjacent Fit"


def build_audience_segments(
    leads: pd.DataFrame,
    courses: pd.DataFrame,
    engagements: pd.DataFrame,
    registrations: pd.DataFrame,
    enrollments: pd.DataFrame,
    opportunity_signal: str | None = None,
) -> pd.DataFrame:
    """Build privacy-safe, explainable audience segments.

    No personal fields are returned. No audience-size ceiling is applied.
    """
    required = {"lead_id", "interest"}
    missing = required.difference(leads.columns)
    if missing:
        raise ValueError(f"Missing lead columns: {sorted(missing)}")

    work = leads.copy()
    opportunity = _normalise(opportunity_signal)

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
    work["demand_signal"] = interest.where(~opaque, offering).replace("", pd.NA).fillna(offering).replace("", pd.NA).fillna("Unspecified")

    engaged = _ids(engagements)
    registered = _ids(registrations)
    enrolled = _ids(enrollments)

    rows: list[dict[str, object]] = []
    for _, row in work.iterrows():
        lead_id = str(row["lead_id"])
        signal = _normalise(row["demand_signal"])
        direct = bool(opportunity and signal == opportunity)

        segment = _classify_segment(row, direct)

        if direct:
            rationale = "Direct demand signal matches the selected campaign opportunity."
        elif segment == "Career Transformation":
            rationale = "Career-change or reskilling intent indicates a plausible transformation pathway."
        elif segment == "Fresher / Career Entry":
            rationale = "Early-career profile indicates potential entry into the programme."
        elif segment == "Experienced Upskiller":
            rationale = "Existing experience or domain context creates an upskilling pathway."
        elif segment == "Referral Opportunity":
            rationale = "Referral-related source or lifecycle signal creates a referral pathway."
        else:
            rationale = "Related demand or engagement indicates an adjacent campaign opportunity."

        rows.append(
            {
                "lead_key": lead_id,
                "audience_segment": segment,
                "demand_signal": row["demand_signal"],
                "engaged": lead_id in engaged,
                "registered": lead_id in registered,
                "enrolled": lead_id in enrolled,
                "audience_rationale": rationale,
            }
        )

    columns = [
        "lead_key",
        "audience_segment",
        "demand_signal",
        "engaged",
        "registered",
        "enrolled",
        "audience_rationale",
    ]
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows, columns=columns)


def summarize_audience_segments(audience: pd.DataFrame) -> pd.DataFrame:
    if audience.empty:
        return pd.DataFrame(columns=["audience_segment", "audience_size", "engaged", "registered", "enrolled"])

    summary = (
        audience.groupby("audience_segment", dropna=False)
        .agg(
            audience_size=("lead_key", "nunique"),
            engaged=("engaged", "sum"),
            registered=("registered", "sum"),
            enrolled=("enrolled", "sum"),
        )
        .reset_index()
        .sort_values(["audience_size", "engaged"], ascending=[False, False])
        .reset_index(drop=True)
    )
    return summary


def render_ai_audience_builder() -> None:
    import streamlit as st

    leads, courses, engagements, registrations, enrollments = load_reetha_audience_data()

    st.markdown("## AI Audience Builder")
    st.caption(
        "M13.4 · Build explainable campaign audiences across direct demand, "
        "adjacent domains, experience, career stage and transformation intent."
    )
    st.info(
        "DEMO / SYNTHETIC DATA: CampaignOS uses controlled Reetha data. "
        "Personal lead records are not displayed. Audience size is not capped."
    )

    opportunity_signal = st.text_input(
        "Campaign opportunity / demand signal",
        value="",
        placeholder="Example: SAP BTP, Python Programming, Generative AI",
    )

    audience = build_audience_segments(
        leads,
        courses,
        engagements,
        registrations,
        enrollments,
        opportunity_signal=opportunity_signal or None,
    )
    summary = summarize_audience_segments(audience)

    if summary.empty:
        st.warning("No audience segments can be derived from the current dataset.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Eligible Audience", int(summary["audience_size"].sum()))
    c2.metric("Audience Segments", len(summary))
    c3.metric("Engaged Audience", int(summary["engaged"].sum()))

    st.markdown("### Audience Segments")
    st.dataframe(
        summary.rename(
            columns={
                "audience_segment": "Audience Segment",
                "audience_size": "Audience Size",
                "engaged": "Engaged",
                "registered": "Registered",
                "enrolled": "Enrolled",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    top = summary.iloc[0]
    st.markdown("### AI Audience Rationale")
    st.success(
        f"**{top['audience_segment']}** is the largest eligible segment with "
        f"**{int(top['audience_size'])}** leads. CampaignOS does not impose a "
        "fixed audience limit; campaign constraints can be applied later by the planner."
    )

    sample = audience[audience["audience_segment"] == top["audience_segment"]].head(8)
    st.markdown("### Explainable Audience Signals")
    st.dataframe(
        sample[
            ["audience_segment", "demand_signal", "engaged", "registered", "enrolled", "audience_rationale"]
        ].rename(
            columns={
                "audience_segment": "Segment",
                "demand_signal": "Demand Signal",
                "engaged": "Engaged",
                "registered": "Registered",
                "enrolled": "Enrolled",
                "audience_rationale": "Why selected",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Next stage: turn an audience definition into a governed campaign brief, "
        "content package and execution plan."
    )
