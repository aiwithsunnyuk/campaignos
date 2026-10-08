from pathlib import Path

from src.data_adapters import SyntheticContactLeadAdapter


CONTACTS_FILE = Path("data/synthetic/contacts.csv")


def test_synthetic_contacts_map_to_canonical_leads():
    adapter = SyntheticContactLeadAdapter(
        tenant_id="demo",
        path=CONTACTS_FILE,
    )

    leads = adapter.load()

    assert len(leads) > 0

    first = leads[0]

    assert first.lead_id
    assert first.tenant_id == "demo"
    assert first.first_name
    assert first.lifecycle_stage
    assert first.source == "synthetic_contacts"


def test_synthetic_contact_lead_score_is_numeric():
    adapter = SyntheticContactLeadAdapter(
        tenant_id="demo",
        path=CONTACTS_FILE,
    )

    leads = adapter.load()

    scored_leads = [
        lead for lead in leads
        if lead.lead_score is not None
    ]

    assert scored_leads
    assert all(
        isinstance(lead.lead_score, float)
        for lead in scored_leads
    )
