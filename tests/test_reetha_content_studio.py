from src.reetha_content_studio import generate_content_package, normalize_brief


def _default_package():
    return generate_content_package({
        "campaign_name": "SAP Finance / FICO Growth Campaign",
        "objective": "Nurture demand and generate qualified enquiries",
        "audience": "sap finance / fico professionals",
        "demand_signal": "SAP Finance / FICO",
        "primary_offering": "SAP Finance / FICO training",
        "channels": ["Email", "WhatsApp", "LinkedIn"],
        "cta": "Book a consultation",
    })


def test_generates_expected_channel_assets_and_keeps_governance():
    package = _default_package()
    assert {draft.channel for draft in package.drafts} == {"Email", "WhatsApp", "LinkedIn"}
    assert len(package.drafts) == 4
    assert package.approval_required is True
    assert package.external_execution_enabled is False


def test_email_body_avoids_internal_objective_as_awkward_audience_claim():
    package = _default_package()
    email = next(d.body for d in package.drafts if d.channel == "Email" and d.asset_type == "Email body")
    assert "generate qualified enquiries for sap finance / fico professionals" not in email.lower()
    assert "help interested professionals explore the right next step" in email
    assert "SAP Finance / FICO professionals" in email


def test_linkedin_copy_does_not_repeat_internal_objective_verbatim():
    package = _default_package()
    post = next(d.body for d in package.drafts if d.channel == "LinkedIn")
    assert "who want to nurture demand" not in post.lower()
    assert "The goal is to help interested professionals explore the right next step." in post


def test_whatsapp_copy_has_clean_punctuation():
    package = _default_package()
    message = next(d.body for d in package.drafts if d.channel == "WhatsApp")
    assert " . " not in message
    assert "Book a consultation." in message


def test_normalization_preserves_supported_domain_names():
    brief = normalize_brief({"audience": "sap finance / fico professionals"})
    assert brief.audience == "SAP Finance / FICO professionals"


def test_export_contract_preserves_approval_safety():
    data = _default_package().to_dict()
    assert data["approval_required"] is True
    assert data["external_execution_enabled"] is False
    assert len(data["drafts"]) == 4
