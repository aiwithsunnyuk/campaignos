from src.reetha_content_studio import (
    CampaignBrief, content_brief_signature, generate_content_package,
    matching_saved_drafts, normalize_brief,
)


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


def test_brief_signature_changes_when_campaign_inputs_change():
    original = CampaignBrief(
        campaign_name="Campaign A", objective="Educate", audience="SAP professionals",
        demand_signal="SAP FICO", primary_offering="Training",
        channels=("Email", "LinkedIn"), call_to_action="Learn more",
    )
    changed = CampaignBrief(
        campaign_name="Campaign A", objective="Educate", audience="SAP professionals",
        demand_signal="SAP FICO", primary_offering="Training",
        channels=("Email",), call_to_action="Learn more",
    )
    assert content_brief_signature(original) != content_brief_signature(changed)


def test_matching_saved_drafts_are_reused_for_same_brief():
    signature = ("Campaign A", "SAP professionals", ("Email",))
    saved = [{"channel": "Email", "body": "Reviewed draft"}]
    assert matching_saved_drafts(signature, signature, saved) == saved


def test_stale_saved_drafts_are_rejected_for_changed_brief():
    current = ("Campaign B", "SAP professionals", ("Email",))
    previous = ("Campaign A", "SAP professionals", ("Email",))
    saved = [{"channel": "Email", "body": "Old draft"}]
    assert matching_saved_drafts(current, previous, saved) is None


def test_deterministic_drafts_remain_available_without_provider():
    from src.reetha_ai_provider import load_provider_config

    config = load_provider_config(environ={}, secrets_reader=lambda _name: "")
    package = _default_package()

    assert config is None
    assert len(package.drafts) == 4
    assert package.approval_required is True
    assert package.external_execution_enabled is False



def test_provider_failure_returns_no_partial_refinement():
    from src.reetha_ai_provider import ProviderRequestError
    from src.reetha_content_studio import refine_content_drafts

    package = _default_package()

    class FailingProvider:
        def __init__(self):
            self.calls = 0

        def generate_text(self, prompt):
            self.calls += 1
            if self.calls == 2:
                raise ProviderRequestError(
                    "AI provider could not be reached or timed out."
                )
            return "Partially refined copy"

    provider = FailingProvider()
    revised, error = refine_content_drafts(
        package,
        normalize_brief({
            "campaign_name": "SAP Finance / FICO Growth Campaign",
            "objective": "Nurture demand and generate qualified enquiries",
            "audience": "sap finance / fico professionals",
            "demand_signal": "SAP Finance / FICO",
            "primary_offering": "SAP Finance / FICO training",
            "channels": ["Email", "WhatsApp", "LinkedIn"],
            "cta": "Book a consultation",
        }),
        provider,
    )

    assert provider.calls == 2
    assert revised is None
    assert "could not be reached" in error
    assert len(package.drafts) == 4
    assert package.approval_required is True
    assert package.external_execution_enabled is False


def test_unexpected_provider_error_discards_partial_refinement():
    from src.reetha_content_studio import refine_content_drafts

    package = _default_package()
    brief = normalize_brief({
        "campaign_name": "SAP Finance / FICO Growth Campaign",
        "objective": "Nurture demand and generate qualified enquiries",
        "audience": "sap finance / fico professionals",
        "demand_signal": "SAP Finance / FICO",
        "primary_offering": "SAP Finance / FICO training",
        "channels": ["Email", "WhatsApp", "LinkedIn"],
        "cta": "Book a consultation",
    })

    class UnexpectedFailureProvider:
        def __init__(self):
            self.calls = 0

        def generate_text(self, prompt):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError(
                    "sensitive internal endpoint and credentials detail"
                )
            return "Partially refined copy"

    provider = UnexpectedFailureProvider()
    revised, error = refine_content_drafts(package, brief, provider)

    assert provider.calls == 2
    assert revised is None
    assert error == (
        "An unexpected error occurred during AI refinement. "
        "Deterministic drafts remain available."
    )
    assert "credentials" not in error
    assert len(package.drafts) == 4
    assert package.approval_required is True
    assert package.external_execution_enabled is False


def test_streamlit_content_studio_handles_provider_failure(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import src.reetha_ai_provider as ai_provider
    from src.reetha_ai_provider import ProviderRequestError

    class FailingProvider:
        def __init__(self):
            self.calls = 0

        def generate_text(self, prompt):
            self.calls += 1
            if self.calls == 2:
                raise ProviderRequestError(
                    "AI provider could not be reached or timed out."
                )
            return "Partial AI result"

    provider = FailingProvider()
    monkeypatch.setattr(
        ai_provider, "configured_provider", lambda: provider
    )

    app = AppTest.from_string(
        "from src.reetha_content_studio import render_content_studio\n"
        "render_content_studio()\n"
    ).run()

    app.checkbox(key="m137_use_ai").set_value(True).run()
    app.button(key="m137_generate_ai").click().run()

    assert not app.exception
    assert provider.calls == 2
    assert any(
        "AI refinement failed" in item.value
        for item in app.error
    )
    assert "m137_ai_drafts" not in app.session_state
    assert "m137_brief_signature" not in app.session_state
    assert len(app.text_area) == 4
    assert app.session_state["m136_content_approval"] is False


def test_streamlit_content_studio_saves_successful_refinement(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import src.reetha_ai_provider as ai_provider

    class SuccessfulProvider:
        def __init__(self):
            self.calls = 0

        def generate_text(self, prompt):
            self.calls += 1
            return f"Refined campaign copy {self.calls}"

    provider = SuccessfulProvider()
    monkeypatch.setattr(
        ai_provider, "configured_provider", lambda: provider
    )

    app = AppTest.from_string(
        "from src.reetha_content_studio import render_content_studio\n"
        "render_content_studio()\n"
    ).run()

    app.checkbox(key="m137_use_ai").set_value(True).run()
    app.button(key="m137_generate_ai").click().run()

    assert not app.exception
    assert provider.calls == 4
    saved = app.session_state["m137_ai_drafts"]
    assert len(saved) == 4
    assert all(item["body"].startswith("Refined campaign copy ") for item in saved)
    assert app.session_state["m137_brief_signature"]
    assert any(
        "AI drafts generated" in item.value
        for item in app.success
    )


def test_streamlit_content_studio_preserves_refinements_on_unchanged_brief(
    monkeypatch,
):
    from streamlit.testing.v1 import AppTest
    import src.reetha_ai_provider as ai_provider

    class SuccessfulProvider:
        def __init__(self):
            self.calls = 0

        def generate_text(self, prompt):
            self.calls += 1
            return f"Saved refinement {self.calls}"

    provider = SuccessfulProvider()
    monkeypatch.setattr(
        ai_provider, "configured_provider", lambda: provider
    )

    app = AppTest.from_string(
        "from src.reetha_content_studio import render_content_studio\n"
        "render_content_studio()\n"
    ).run()

    app.checkbox(key="m137_use_ai").set_value(True).run()
    app.button(key="m137_generate_ai").click().run()

    before = list(app.session_state["m137_ai_drafts"])
    signature_before = app.session_state["m137_brief_signature"]

    # A plain rerun with the same brief must preserve saved refinements.
    app.run()

    assert not app.exception
    assert app.session_state["m137_ai_drafts"] == before
    assert app.session_state["m137_brief_signature"] == signature_before
    assert provider.calls == 4


def test_streamlit_content_studio_invalidates_refinements_when_brief_changes(
    monkeypatch,
):
    from streamlit.testing.v1 import AppTest
    import src.reetha_ai_provider as ai_provider

    class SuccessfulProvider:
        def __init__(self):
            self.calls = 0

        def generate_text(self, prompt):
            self.calls += 1
            return f"Old campaign refinement {self.calls}"

    provider = SuccessfulProvider()
    monkeypatch.setattr(
        ai_provider, "configured_provider", lambda: provider
    )

    app = AppTest.from_string(
        "from src.reetha_content_studio import render_content_studio\n"
        "render_content_studio()\n"
    ).run()

    app.checkbox(key="m137_use_ai").set_value(True).run()
    app.button(key="m137_generate_ai").click().run()

    assert len(app.session_state["m137_ai_drafts"]) == 4

    # Campaign name is the first text input in the current Content Studio UI.
    app.text_input[0].set_value("New Campaign Name").run()

    assert not app.exception
    assert "m137_ai_drafts" not in app.session_state
    assert "m137_brief_signature" not in app.session_state
    assert provider.calls == 4
    assert all(
        "Old campaign refinement" not in item.value
        for item in app.text_area
    )


def test_streamlit_content_studio_resets_approval_when_brief_changes():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_string(
        "from src.reetha_content_studio import render_content_studio\n"
        "render_content_studio()\n"
    ).run()

    app.checkbox(key="m136_content_approval").set_value(True).run()
    assert app.session_state["m136_content_approval"] is True

    app.text_input[0].set_value("New Campaign Name").run()

    assert not app.exception
    assert app.session_state["m136_content_approval"] is False


def test_streamlit_content_studio_resets_approval_when_draft_changes():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_string(
        "from src.reetha_content_studio import render_content_studio\n"
        "render_content_studio()\n"
    ).run()

    app.checkbox(key="m136_content_approval").set_value(True).run()
    assert app.session_state["m136_content_approval"] is True

    original = app.text_area[0].value
    app.text_area[0].set_value(original + " Updated after approval.").run()

    assert not app.exception
    assert app.session_state["m136_content_approval"] is False
