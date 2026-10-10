from __future__ import annotations

from pathlib import Path

import pandas as pd


LEAD_FIELD_CONTRACT = [
    "SAP Domain",
    "Candidate",
    "Mobile",
    "Email ID",
    "Total Exp",
    "Work Location",
]


def load_offering_catalog(data_dir: Path | None = None) -> pd.DataFrame:
    root = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data" / "reetha"
    path = root / "offering_catalog.csv"
    return pd.read_csv(path)


def offering_summary(df: pd.DataFrame) -> dict[str, int]:
    return {
        "total": int(len(df)),
        "standalone": int((df["offering_type"] == "Standalone").sum()),
        "integrated": int((df["offering_type"] == "Integrated").sum()),
        "contact_us": int(df["pricing"].astype(str).str.strip().eq("Contact Us").sum()),
    }


def render_reetha_business_surface() -> None:
    import streamlit as st

    df = load_offering_catalog()
    summary = offering_summary(df)

    st.markdown("## Reetha IT Hub · GTM Command Center")
    st.caption(
        "M13.1 · Reetha commercial surface | Catalogue loaded from the approved "
        "SAP Server & Integration Services pricing sheet"
    )

    st.info(
        "DEMO / SYNTHETIC DATA: Lead records are not loaded here. "
        "Only the Reetha offering catalogue and the agreed lead-field contract "
        "are being established."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SAP Offerings", summary["total"])
    c2.metric("Standalone", summary["standalone"])
    c3.metric("Integrated", summary["integrated"])
    c4.metric("Contact Us", summary["contact_us"])

    st.markdown("### SAP Offering Catalogue")
    display = df.rename(
        columns={
            "offering_name": "Offering",
            "offering_type": "Type",
            "integration_backend": "Integration / Backend",
            "pricing": "Pricing",
            "purpose": "Purpose",
        }
    )[["Offering", "Type", "Integration / Backend", "Pricing", "Purpose"]]
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.markdown("### Lead Intelligence Contract")
    st.caption(
        "The following fields define the future Reetha lead view. "
        "No personal lead records are required for M13.1."
    )
    st.code(" | ".join(LEAD_FIELD_CONTRACT), language="text")

    l1, l2, l3 = st.columns(3)
    l1.metric("Lead identity", "Candidate + Email ID")
    l2.metric("Demand signal", "SAP Domain")
    l3.metric("Segmentation", "Total Exp + Work Location")

    st.markdown("### M13 Business Loop")
    st.markdown(
        "**SAP Offering → SAP Domain → Interested Lead → Campaign → "
        "Engagement → Registration → Enrollment → Business Outcome**"
    )
