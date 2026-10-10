import pandas as pd

from src.reetha_sap_audience_intelligence import (
    build_domain_priority,
    build_expansion_opportunities,
    build_sap_profile_intelligence,
    normalize_domain,
)

def test_domain_normalization_groups_realistic_variants():
    assert normalize_domain("Sap Fico Consultant") == "SAP Finance / FICO"
    assert normalize_domain("SAP ABAP+HANA") == "SAP ABAP / Development"
    assert normalize_domain("SAP MM Consultant") == "SAP Procurement / MM"
    assert normalize_domain("SAP CPI") == "SAP Integration / CPI"

def test_profile_intelligence_maps_campaign_and_server_access():
    profiles = pd.DataFrame([
        {"profile_key":"P1","sap_domain":"SAP Finance / FICO","experience_band":"8–11 years","work_location":"Hyderabad"},
        {"profile_key":"P2","sap_domain":"SAP ABAP / Development","experience_band":"5–7 years","work_location":"Bengaluru"},
        {"profile_key":"P3","sap_domain":"SAP HCM / SuccessFactors","experience_band":"3–4 years","work_location":"Pune"},
    ])
    result = build_sap_profile_intelligence(profiles)
    assert "S/4HANA Finance" in result.iloc[0]["campaign_recommendation"]
    assert "SAP S/4HANA" in result.iloc[0]["recommended_server_access"]
    assert result.iloc[1]["audience_pathway"] == "Practitioner Upskill"

def test_domain_priority_and_expansion_are_not_capped():
    profiles = pd.DataFrame([
        *[{"profile_key":f"F{i}","sap_domain":"SAP Finance / FICO","experience_band":"8–11 years","work_location":"Hyderabad"} for i in range(1,101)],
        *[{"profile_key":f"A{i}","sap_domain":"SAP ABAP / Development","experience_band":"5–7 years","work_location":"Bengaluru"} for i in range(1,51)],
    ])
    priority = build_domain_priority(profiles)
    expansion = build_expansion_opportunities(priority)
    assert int(priority.loc[priority["sap_domain"]=="SAP Finance / FICO","audience_size"].iloc[0]) == 100
    assert not expansion.empty
    assert expansion["source_audience"].max() == 100

def test_channel_signals_are_separate_from_external_execution():
    from src.reetha_sap_audience_intelligence import build_channel_reach_signals
    engagements = pd.DataFrame([{"channel":"LinkedIn"},{"channel":"LinkedIn"},{"channel":"WhatsApp"}])
    result = build_channel_reach_signals(engagements)
    assert result.iloc[0]["channel"] == "LinkedIn"
    assert result.iloc[0]["event_count"] == 2
    assert result.iloc[0]["role"] == "Professional acquisition / domain targeting"
