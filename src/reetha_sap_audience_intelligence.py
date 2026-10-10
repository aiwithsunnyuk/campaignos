from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

DOMAIN_TO_SERVER = {
    "SAP Finance / FICO": ("SAP S/4HANA", "SAP SAC", "SAP Datasphere"),
    "SAP ABAP / Development": ("SAP S/4HANA", "SAP BTP", "SAP S/4HANA Public Cloud"),
    "SAP Sales / SD": ("SAP S/4HANA", "SAP BRIM", "SAP S/4HANA Public Cloud"),
    "SAP Procurement / MM": ("SAP S/4HANA", "SAP Ariba", "SAP IBP"),
    "SAP Warehouse / EWM": ("SAP S/4HANA", "SAP IBP"),
    "SAP Manufacturing / PP": ("SAP S/4HANA", "SAP IBP"),
    "SAP HCM / SuccessFactors": ("SAP SuccessFactors", "SAP S/4HANA"),
    "SAP Integration / CPI": ("SAP BTP", "SAP S/4HANA"),
    "SAP Basis / Administration": ("SAP S/4HANA", "SAP BTP", "SAP S/4HANA Public Cloud"),
    "SAP UX / UI5 / Fiori": ("SAP BTP", "SAP S/4HANA"),
    "SAP HANA / Data": ("SAP BTP", "SAP Datasphere", "SAP SAC"),
    "SAP BTP / Cloud": ("SAP BTP", "SAP S/4HANA Public Cloud"),
    "SAP Analytics / BW": ("SAP Datasphere", "SAP SAC", "SAP S/4HANA"),
    "SAP Transportation / TM": ("SAP S/4HANA", "SAP IBP"),
    "SAP Plant Maintenance / PM": ("SAP S/4HANA", "SAP ECC"),
    "SAP Project Systems / PS": ("SAP S/4HANA", "SAP ECC"),
    "SAP Security / GRC": ("SAP S/4HANA", "SAP BTP"),
    "SAP Supply Chain / APO": ("SAP IBP", "SAP S/4HANA"),
    "SAP General / Consulting": ("SAP S/4HANA", "SAP Joule / Business AI"),
    "Non-SAP / Ambiguous": ("SAP S/4HANA",),
}

DOMAIN_TO_CAMPAIGN = {
    "SAP Finance / FICO": "S/4HANA Finance + Analytics Transformation",
    "SAP ABAP / Development": "ABAP → HANA / BTP Modernization",
    "SAP Sales / SD": "S/4HANA Sales Transformation",
    "SAP Procurement / MM": "S/4HANA Procurement + Ariba",
    "SAP Warehouse / EWM": "EWM + Supply Chain Practice",
    "SAP Manufacturing / PP": "S/4HANA Manufacturing + IBP",
    "SAP HCM / SuccessFactors": "SuccessFactors Transformation",
    "SAP Integration / CPI": "BTP Integration / CPI Modernization",
    "SAP Basis / Administration": "S/4HANA Administration + Cloud Transition",
    "SAP UX / UI5 / Fiori": "BTP + Fiori Modernization",
    "SAP HANA / Data": "HANA → Datasphere / Analytics",
    "SAP BTP / Cloud": "BTP Application + Integration",
    "SAP Analytics / BW": "Datasphere + SAC Analytics",
    "SAP Transportation / TM": "S/4HANA Transportation + IBP",
    "SAP Plant Maintenance / PM": "S/4HANA Asset / Plant Maintenance",
    "SAP Project Systems / PS": "S/4HANA Project Transformation",
    "SAP Security / GRC": "SAP Security + BTP Governance",
    "SAP Supply Chain / APO": "IBP / Supply Chain Modernization",
    "SAP General / Consulting": "SAP Transformation Orientation + Joule",
    "Non-SAP / Ambiguous": "SAP Career Transformation / Foundation",
}

DOMAIN_EXPANSION = {
    "SAP Finance / FICO": ["SAP Analytics / BW", "SAP HANA / Data", "SAP General / Consulting"],
    "SAP ABAP / Development": ["SAP HANA / Data", "SAP BTP / Cloud", "SAP UX / UI5 / Fiori", "SAP Integration / CPI"],
    "SAP Sales / SD": ["SAP Procurement / MM", "SAP Finance / FICO", "SAP General / Consulting"],
    "SAP Procurement / MM": ["SAP Warehouse / EWM", "SAP Manufacturing / PP", "SAP Supply Chain / APO"],
    "SAP Warehouse / EWM": ["SAP Procurement / MM", "SAP Supply Chain / APO", "SAP Manufacturing / PP"],
    "SAP Manufacturing / PP": ["SAP Supply Chain / APO", "SAP Warehouse / EWM", "SAP Plant Maintenance / PM"],
    "SAP HCM / SuccessFactors": ["SAP General / Consulting", "SAP Analytics / BW"],
    "SAP Integration / CPI": ["SAP BTP / Cloud", "SAP ABAP / Development", "SAP HANA / Data"],
    "SAP Basis / Administration": ["SAP BTP / Cloud", "SAP Security / GRC", "SAP HANA / Data"],
    "SAP UX / UI5 / Fiori": ["SAP BTP / Cloud", "SAP ABAP / Development"],
    "SAP HANA / Data": ["SAP BTP / Cloud", "SAP Analytics / BW", "SAP ABAP / Development"],
    "SAP BTP / Cloud": ["SAP Integration / CPI", "SAP ABAP / Development", "SAP HANA / Data"],
    "SAP Analytics / BW": ["SAP HANA / Data", "SAP Finance / FICO"],
    "SAP Transportation / TM": ["SAP Supply Chain / APO", "SAP Warehouse / EWM"],
    "SAP Plant Maintenance / PM": ["SAP Manufacturing / PP", "SAP Project Systems / PS"],
    "SAP Project Systems / PS": ["SAP Finance / FICO", "SAP Plant Maintenance / PM"],
    "SAP Security / GRC": ["SAP Basis / Administration", "SAP BTP / Cloud"],
    "SAP Supply Chain / APO": ["SAP Procurement / MM", "SAP Warehouse / EWM", "SAP Manufacturing / PP"],
    "SAP General / Consulting": ["SAP BTP / Cloud", "SAP Finance / FICO"],
    "Non-SAP / Ambiguous": ["SAP General / Consulting", "SAP BTP / Cloud", "SAP Finance / FICO"],
}

def _repo_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return Path(__file__).resolve().parents[1] / "data" / "reetha"

def normalize_domain(value: object) -> str:
    x = str(value).replace("\xa0", " ").strip().upper()
    if not x or x == "NAN":
        return "Unknown"
    rules = [
        (r"\bABAP\b", "SAP ABAP / Development"),
        (r"\bFICO\b|\bFI\b|\bCO\b|ACCOUNT|TREASURY|FSCM|GROUP REPORTING", "SAP Finance / FICO"),
        (r"\bSD\b|SALES", "SAP Sales / SD"),
        (r"\bMM\b|PROCURE|PURCHAS|SOURC", "SAP Procurement / MM"),
        (r"\bEWM\b|\bWM\b|WAREHOUSE", "SAP Warehouse / EWM"),
        (r"\bPP\b|PRODUCTION|MANUFACTUR", "SAP Manufacturing / PP"),
        (r"\bHCM\b|SUCCESSFACTORS", "SAP HCM / SuccessFactors"),
        (r"\bCPI\b|INTEGRATION|PI\b|PO\b", "SAP Integration / CPI"),
        (r"\bBASIS\b|ADMIN", "SAP Basis / Administration"),
        (r"\bUI5\b|FIORI", "SAP UX / UI5 / Fiori"),
        (r"\bHANA\b|DATABASE", "SAP HANA / Data"),
        (r"\bBTP\b|CAP\b|CLOUD", "SAP BTP / Cloud"),
        (r"\bBW\b|ANALYTICS|BI", "SAP Analytics / BW"),
        (r"\bTM\b|TRANSPORT", "SAP Transportation / TM"),
        (r"\bPM\b|PLANT MAINT", "SAP Plant Maintenance / PM"),
        (r"\bPS\b|PROJECT", "SAP Project Systems / PS"),
        (r"\bGRC\b|SECURITY", "SAP Security / GRC"),
        (r"\bAPO\b|SUPPLY", "SAP Supply Chain / APO"),
    ]
    for pattern, label in rules:
        if re.search(pattern, x):
            return label
    if "SAP" in x:
        return "SAP General / Consulting"
    return "Non-SAP / Ambiguous"

def load_sap_profile_seed(data_dir: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(_repo_data_dir(data_dir) / "sap_audience_profiles.csv")

def load_server_catalog(data_dir: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(_repo_data_dir(data_dir) / "sap_server_catalog.csv")

def load_existing_channel_signals(data_dir: Path | None = None) -> pd.DataFrame:
    path = _repo_data_dir(data_dir) / "engagements.csv"
    if not path.exists():
        return pd.DataFrame(columns=["channel", "event_count"])
    events = pd.read_csv(path)
    if "channel" not in events.columns:
        return pd.DataFrame(columns=["channel", "event_count"])
    return events.groupby("channel").size().reset_index(name="event_count").sort_values(
        "event_count", ascending=False
    ).reset_index(drop=True)

def build_sap_profile_intelligence(profiles: pd.DataFrame) -> pd.DataFrame:
    required = {"profile_key", "sap_domain", "experience_band", "work_location"}
    missing = required.difference(profiles.columns)
    if missing:
        raise ValueError(f"Missing profile columns: {sorted(missing)}")
    work = profiles.copy()
    work["campaign_recommendation"] = work["sap_domain"].map(DOMAIN_TO_CAMPAIGN).fillna(
        "SAP Career Transformation / Foundation"
    )
    work["recommended_server_access"] = work["sap_domain"].map(
        lambda d: " + ".join(DOMAIN_TO_SERVER.get(d, ("SAP S/4HANA",)))
    )
    work["audience_pathway"] = work.apply(_audience_pathway, axis=1)
    return work

def _audience_pathway(row: pd.Series) -> str:
    band = str(row.get("experience_band", ""))
    if band == "0–2 years":
        return "Fresher / Early Career"
    if band in {"3–4 years", "5–7 years"}:
        return "Practitioner Upskill"
    if band in {"8–11 years", "12+ years"}:
        return "Experienced Transformation"
    if str(row.get("sap_domain", "")) == "Non-SAP / Ambiguous":
        return "Career Transformation / Enrichment"
    return "Enrichment Required"

def build_domain_priority(profiles: pd.DataFrame) -> pd.DataFrame:
    counts = profiles.groupby("sap_domain").agg(
        audience_size=("profile_key", "nunique"),
        locations=("work_location", "nunique"),
        experienced=("experience_band", lambda s: int(s.isin(["8–11 years", "12+ years"]).sum())),
        early_career=("experience_band", lambda s: int(s.eq("0–2 years").sum())),
    ).reset_index()
    counts["campaign"] = counts["sap_domain"].map(DOMAIN_TO_CAMPAIGN)
    counts["server_access"] = counts["sap_domain"].map(
        lambda d: " + ".join(DOMAIN_TO_SERVER.get(d, ("SAP S/4HANA",)))
    )
    max_size = max(float(counts["audience_size"].max()), 1.0)
    max_locations = max(float(counts["locations"].max()), 1.0)
    counts["priority_score"] = (
        60 * counts["audience_size"] / max_size
        + 25 * counts["locations"] / max_locations
        + 15 * (counts["experienced"] / counts["audience_size"].clip(lower=1))
    ).round(1)
    return counts.sort_values(["priority_score", "audience_size"], ascending=[False, False]).reset_index(drop=True)

def build_expansion_opportunities(domain_priority: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in domain_priority.iterrows():
        for adjacent in DOMAIN_EXPANSION.get(row["sap_domain"], []):
            rows.append({
                "source_domain": row["sap_domain"],
                "adjacent_domain": adjacent,
                "source_audience": int(row["audience_size"]),
                "expansion_campaign": DOMAIN_TO_CAMPAIGN.get(adjacent, "SAP Transformation"),
                "recommended_server_access": " + ".join(DOMAIN_TO_SERVER.get(adjacent, ("SAP S/4HANA",))),
            })
    return pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)

def build_channel_reach_signals(engagements: pd.DataFrame) -> pd.DataFrame:
    if engagements.empty or "channel" not in engagements.columns:
        return pd.DataFrame(columns=["channel", "event_count", "reach_signal", "role"])
    result = engagements.groupby("channel").size().reset_index(name="event_count").sort_values(
        "event_count", ascending=False
    ).reset_index(drop=True)
    result["reach_signal"] = (result["event_count"] / max(float(result["event_count"].max()), 1.0) * 100).round(1)
    roles = {
        "LinkedIn": "Professional acquisition / domain targeting",
        "Google Ads": "Intent capture",
        "Organic Search": "Intent capture / discovery",
        "Meta": "Broad awareness / retargeting",
        "Instagram": "Awareness / education",
        "WhatsApp": "Nurture / follow-up",
        "Email": "Nurture / reactivation",
    }
    result["role"] = result["channel"].map(roles).fillna("Channel role requires validation")
    return result

def data_quality_summary(profiles: pd.DataFrame) -> dict[str, int]:
    exp = pd.to_numeric(profiles.get("experience_years"), errors="coerce")
    return {
        "profiles": int(len(profiles)),
        "domains": int(profiles["sap_domain"].nunique()),
        "locations": int(profiles["work_location"].nunique()),
        "experience_known": int(exp.notna().sum()),
        "experience_unknown": int(exp.isna().sum()),
    }

def render_sap_audience_intelligence() -> None:
    import streamlit as st
    profiles = build_sap_profile_intelligence(load_sap_profile_seed())
    server_catalog = load_server_catalog()
    priority = build_domain_priority(profiles)
    expansion = build_expansion_opportunities(priority)
    channel_signals = build_channel_reach_signals(load_existing_channel_signals())
    quality = data_quality_summary(profiles)

    st.markdown("## SAP Audience Intelligence & Expansion")
    st.caption("M13.4.1 · Normalize SAP demand, prioritize campaigns, match training/server access, and identify adjacent audience expansion paths.")
    st.info("SOURCE-SAFE DATA: The supplied SAP profile seed is used for audience intelligence. Candidate, mobile and email fields are not displayed. Live external channel expansion requires authorized connectors.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SAP Seed Profiles", quality["profiles"])
    c2.metric("Canonical Domains", quality["domains"])
    c3.metric("Locations", quality["locations"])
    c4.metric("Experience Known", quality["experience_known"])

    st.markdown("### Campaign Priority")
    display = priority.rename(columns={
        "sap_domain": "SAP Domain", "audience_size": "Audience", "locations": "Locations",
        "campaign": "Priority Campaign", "server_access": "Recommended Server Access",
        "priority_score": "Priority Score",
    })
    st.dataframe(display[["SAP Domain","Audience","Locations","Priority Campaign","Recommended Server Access","Priority Score"]].head(15), use_container_width=True, hide_index=True)

    top = priority.iloc[0]
    st.success(f"**Priority campaign:** {top['campaign']} · {int(top['audience_size'])} seed profiles · recommended environment: **{top['server_access']}**.")

    st.markdown("### Audience Pathways")
    pathways = profiles.groupby("audience_pathway").size().reset_index(name="audience_size").sort_values("audience_size", ascending=False)
    st.dataframe(pathways.rename(columns={"audience_pathway":"Audience Pathway","audience_size":"Audience"}), use_container_width=True, hide_index=True)

    st.markdown("### Adjacent Audience Expansion")
    st.dataframe(
        expansion.head(20).rename(columns={
            "source_domain":"Seed Domain","adjacent_domain":"Adjacent Audience",
            "source_audience":"Seed Audience","expansion_campaign":"Expansion Campaign",
            "recommended_server_access":"Server Access",
        }),
        use_container_width=True, hide_index=True,
    )

    st.markdown("### Channel Reach Signals")
    if channel_signals.empty:
        st.caption("No existing engagement channel data is available. Authorized connectors can add channel-level audience signals later.")
    else:
        st.dataframe(channel_signals.rename(columns={
            "channel":"Channel","event_count":"Existing Signal Events",
            "reach_signal":"Reach Signal","role":"Recommended Role",
        }), use_container_width=True, hide_index=True)

    st.markdown("### Data Quality & Enrichment")
    st.caption(f"{quality['experience_unknown']} profiles need experience enrichment. Experience values outside a 0–40 year range are treated as unknown. The source contains duplicate location columns; CampaignOS uses the first populated value.")
    st.caption(f"Server catalogue loaded: {len(server_catalog)} Reetha SAP service/server options. External audience expansion remains recommendation-only until connectors are authorized.")
