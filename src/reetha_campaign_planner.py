from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "reetha"


@dataclass(frozen=True)
class CampaignPlan:
    campaign_name: str
    objective: str
    audience: str
    demand_signal: str
    primary_offering: str
    secondary_offering: str
    channels: tuple[str, ...]
    cta: str
    reason: str
    priority: str
    audience_size: int
    engagement_rate: float
    registration_gap_rate: float


def _load_csv(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _clean(value: object) -> str:
    return "" if pd.isna(value) else str(value).strip()


def _normalise_domain(value: object) -> str:
    text = _clean(value)
    low = text.lower()
    mapping = [
        (("finance", "fico"), "SAP Finance / FICO"),
        (("procurement", "material management"), "SAP Procurement / MM"),
        (("mm",), "SAP Procurement / MM"),
        (("sales", "sd"), "SAP Sales / SD"),
        (("abap", "development"), "SAP ABAP / Development"),
        (("basis", "administration"), "SAP Basis / Administration"),
        (("hana",), "SAP HANA / Data"),
        (("btp", "cloud"), "SAP BTP / Cloud"),
        (("integration", "cpi"), "SAP Integration / CPI"),
        (("analytics", "bw"), "SAP Analytics / BW"),
        (("fiori", "ui5"), "SAP UX / UI5 / Fiori"),
        (("successfactors", "hcm"), "SAP HCM / SuccessFactors"),
        (("ewm", "warehouse"), "SAP Warehouse / EWM"),
        (("manufacturing", "pp"), "SAP Manufacturing / PP"),
        (("supply chain", "apo"), "SAP Supply Chain / APO"),
        (("security", "grc"), "SAP Security / GRC"),
    ]
    for tokens, label in mapping:
        if any(token in low for token in tokens):
            return label
    return text or "SAP General / Consulting"


def _experience_value(value: object) -> float:
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", _clean(value))]
    return sum(nums[:2]) / min(len(nums), 2) if nums else 0.0


def _column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    return next((c for c in candidates if c in df.columns), None)


def _audience_by_domain() -> pd.DataFrame:
    audience = _load_csv("sap_audience_profiles.csv")
    # M13.4.1 publishes a normalized contract:
    # sap_domain is already canonical and experience_years is numeric.
    # Prefer those fields, while retaining compatibility with older/raw shapes.
    dcol = _column(audience, ("sap_domain", "SAP Domain", "SAP_Domain", "Domain", "interest"))
    ecol = _column(audience, ("experience_years", "Total Exp", "Total Exp ", "Experience", "experience"))
    if audience.empty or not dcol:
        return pd.DataFrame(columns=["domain", "audience_size", "avg_experience"])

    work = audience.copy()
    if dcol == "sap_domain":
        work["domain"] = work[dcol].map(lambda x: _clean(x) or "SAP General / Consulting")
    else:
        work["domain"] = work[dcol].map(_normalise_domain)

    if ecol:
        work["experience"] = pd.to_numeric(work[ecol], errors="coerce").fillna(
            work[ecol].map(_experience_value)
        )
    else:
        work["experience"] = 0.0
    return (
        work.groupby("domain")
        .agg(audience_size=("domain", "size"), avg_experience=("experience", "mean"))
        .reset_index()
    )


def _course_name(course_id: object, courses: pd.DataFrame) -> str:
    cid = _clean(course_id)
    if not cid or courses.empty or not {"course_id", "name"}.issubset(courses.columns):
        return cid
    hit = courses.loc[courses["course_id"].astype(str) == cid, "name"]
    return _clean(hit.iloc[0]) if not hit.empty else cid


def _training_for_domain(domain: str, courses: pd.DataFrame) -> str:
    fallback = {
        "SAP Finance / FICO": "SAP Finance / FICO training",
        "SAP Procurement / MM": "SAP MM / Procurement training",
        "SAP Sales / SD": "SAP SD / Sales training",
        "SAP ABAP / Development": "SAP ABAP / Development training",
        "SAP HANA / Data": "SAP HANA / Data training",
        "SAP BTP / Cloud": "SAP BTP / Cloud training",
        "SAP Integration / CPI": "SAP BTP Integration / CPI training",
        "SAP Analytics / BW": "SAP Analytics / BW training",
    }.get(domain, "Relevant SAP training programme")
    if courses.empty or "name" not in courses.columns:
        return fallback

    tokens = {
        "SAP Finance / FICO": ("finance", "fico"),
        "SAP Procurement / MM": ("procurement", "mm"),
        "SAP Sales / SD": ("sales", "sd"),
        "SAP ABAP / Development": ("abap",),
        "SAP HANA / Data": ("hana", "data"),
        "SAP BTP / Cloud": ("btp", "cloud"),
        "SAP Integration / CPI": ("integration", "cpi"),
        "SAP Analytics / BW": ("analytics", "bw"),
        "SAP UX / UI5 / Fiori": ("fiori", "ui5"),
        "SAP HCM / SuccessFactors": ("hcm", "success"),
    }.get(domain, ())
    for name in courses["name"].dropna().astype(str):
        if any(token in name.lower() for token in tokens):
            return name
    return fallback


def _server_for_domain(domain: str) -> str:
    catalog = _load_csv("sap_server_catalog.csv")
    if catalog.empty:
        return "SAP practice/server access"
    dcol = _column(catalog, ("sap_domain", "SAP Domain", "domain", "Domain"))
    ocol = _column(catalog, ("server_access", "server_name", "name", "offering"))
    if not dcol or not ocol:
        return "SAP practice/server access"
    normalized_target = _normalise_domain(domain).lower()

    # The supplied M13.4.1 server catalogue is a service catalogue rather
    # than a domain-to-service mapping. Use deterministic domain mappings
    # and resolve them against the catalogue's service column.
    domain_service = {
        "sap finance / fico": "SAP SAC",
        "sap procurement / mm": "SAP Ariba",
        "sap sales / sd": "SAP S/4HANA",
        "sap abap / development": "SAP BTP",
        "sap hana / data": "SAP Datasphere",
        "sap btp / cloud": "SAP BTP",
        "sap integration / cpi": "SAP BTP",
        "sap analytics / bw": "SAP SAC",
        "sap ux / ui5 / fiori": "SAP BTP",
        "sap hcm / successfactors": "SAP SuccessFactors",
        "sap warehouse / ewm": "SAP S/4HANA",
        "sap manufacturing / pp": "SAP S/4HANA",
        "sap supply chain / apo": "SAP IBP",
        "sap security / grc": "SAP S/4HANA",
        "sap basis / administration": "SAP S/4HANA",
        "sap transportation / tm": "SAP S/4HANA",
        "sap plant maintenance / pm": "SAP S/4HANA",
        "sap project systems / ps": "SAP S/4HANA",
    }
    desired = domain_service.get(normalized_target, "SAP S/4HANA")
    service_col = _column(catalog, ("service", "server_access", "server_name", "name", "offering"))
    if service_col:
        hit = catalog.loc[
            catalog[service_col].astype(str).str.strip().str.lower() == desired.lower(),
            service_col,
        ]
        if not hit.empty:
            return _clean(hit.iloc[0])
    return desired


def _engagement_signals() -> pd.DataFrame:
    engagements = _load_csv("engagements.csv")
    leads = _load_csv("leads.csv")
    registrations = _load_csv("registrations.csv")
    courses = _load_csv("courses.csv")
    if engagements.empty or leads.empty or "lead_id" not in leads.columns:
        return pd.DataFrame(columns=["domain", "engaged", "registered", "engagement_rate", "registration_gap_rate"])

    leads = leads.copy()
    if "interest" in leads.columns:
        leads["domain"] = leads["interest"].map(_normalise_domain)
    elif "course_id" in leads.columns:
        leads["domain"] = leads["course_id"].map(lambda x: _normalise_domain(_course_name(x, courses)))
    else:
        leads["domain"] = "SAP General / Consulting"

    lead_ids = leads["lead_id"].astype(str)
    engaged_ids = set(engagements["lead_id"].astype(str)) if "lead_id" in engagements.columns else set()
    registered_ids = set(registrations["lead_id"].astype(str)) if "lead_id" in registrations.columns else set()
    leads["engaged"] = lead_ids.isin(engaged_ids)
    leads["registered"] = lead_ids.isin(registered_ids)

    grouped = leads.groupby("domain").agg(
        engaged=("engaged", "sum"),
        registered=("registered", "sum"),
        total=("lead_id", "size"),
    ).reset_index()
    grouped["engagement_rate"] = grouped["engaged"] / grouped["total"].replace(0, 1)
    grouped["registration_gap_rate"] = (
        (grouped["engaged"] - grouped["registered"]).clip(lower=0)
        / grouped["engaged"].replace(0, 1)
    )
    return grouped


def build_campaign_plans(min_audience_size: int = 1, max_plans: int = 10) -> list[CampaignPlan]:
    audience = _audience_by_domain()
    if audience.empty:
        return []

    signals = _engagement_signals()
    merged = audience.merge(signals, on="domain", how="left").fillna(0)
    merged["score"] = (
        merged["engagement_rate"] * 0.55
        + merged["registration_gap_rate"] * 0.45
    ) * 100
    merged = merged[merged["audience_size"] >= min_audience_size].sort_values(
        ["score", "audience_size"], ascending=False
    )

    courses = _load_csv("courses.csv")
    plans = []
    for _, row in merged.head(max_plans).iterrows():
        domain = _clean(row["domain"])
        gap = float(row["registration_gap_rate"])
        engagement = float(row["engagement_rate"])
        score = float(row["score"])
        if gap >= 0.70:
            objective, cta = "Generate qualified registrations from high-intent SAP audience", "Register now"
        elif gap >= 0.35:
            objective, cta = "Improve registration conversion from engaged SAP audience", "Explore programme"
        else:
            objective, cta = "Nurture and expand demand for the relevant SAP practice", "Book a consultation"
        priority = "High" if score >= 65 else "Medium" if score >= 40 else "Build"
        plans.append(CampaignPlan(
            campaign_name=f"{domain} Growth Campaign",
            objective=objective,
            audience=f"{domain} professionals",
            demand_signal=domain,
            primary_offering=_training_for_domain(domain, courses),
            secondary_offering=_server_for_domain(domain),
            channels=("Email", "WhatsApp", "LinkedIn"),
            cta=cta,
            reason=f"{int(row['audience_size'])} audience profiles mapped to {domain}; {engagement:.0%} engagement signal and {gap:.0%} registration gap.",
            priority=priority,
            audience_size=int(row["audience_size"]),
            engagement_rate=engagement,
            registration_gap_rate=gap,
        ))
    return plans


def render_campaign_planner() -> None:
    import streamlit as st
    st.subheader("AI Campaign Planner")
    st.caption("Turns audience intelligence and demand signals into approval-ready campaign briefs. Planning only: no external campaign is executed by this milestone.")
    plans = build_campaign_plans()
    if not plans:
        st.info("No campaign-ready audience signals are available yet.")
        return
    top = plans[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Campaign plans", len(plans))
    c2.metric("Top audience", f"{top.audience_size:,}")
    c3.metric("Engagement", f"{top.engagement_rate:.0%}")
    c4.metric("Priority", top.priority)
    st.markdown("### Recommended campaign")
    st.write(f"**{top.campaign_name}**")
    st.write(f"**Objective:** {top.objective}")
    st.write(f"**Audience:** {top.audience}")
    st.write(f"**Primary offering:** {top.primary_offering}")
    st.write(f"**Secondary offering:** {top.secondary_offering}")
    st.write(f"**Channels:** {', '.join(top.channels)}")
    st.write(f"**CTA:** {top.cta}")
    st.info(top.reason)
    st.markdown("### Campaign plan portfolio")
    st.dataframe(pd.DataFrame([{
        "Campaign": p.campaign_name,
        "Priority": p.priority,
        "Audience": p.audience_size,
        "Engagement": f"{p.engagement_rate:.0%}",
        "Registration Gap": f"{p.registration_gap_rate:.0%}",
        "Primary Offering": p.primary_offering,
        "Server Access": p.secondary_offering,
    } for p in plans]), use_container_width=True, hide_index=True)
    with st.expander("Campaign brief"):
        st.markdown(f"**Campaign:** {top.campaign_name}")
        st.markdown(f"**Objective:** {top.objective}")
        st.markdown(f"**Target audience:** {top.audience}")
        st.markdown(f"**Demand signal:** {top.demand_signal}")
        st.markdown(f"**Primary offering:** {top.primary_offering}")
        st.markdown(f"**Secondary offering:** {top.secondary_offering}")
        st.markdown(f"**Recommended channels:** {', '.join(top.channels)}")
        st.markdown(f"**CTA:** {top.cta}")
        st.markdown(f"**Priority:** {top.priority}")
        st.markdown(f"**Why now:** {top.reason}")
        st.warning("Human approval is required before execution. M13.5 creates the plan; execution connectors belong to later milestones.")
