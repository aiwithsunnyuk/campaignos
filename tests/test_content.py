from src.content.engine import (
    content_summary,
    extract_tokens,
    prepare_preview,
    render_personalization,
    validate_html,
    validate_personalization,
)
from src.content.models import (
    ContentAsset,
    ContentStatus,
    ContentType,
    PersonalizationToken,
)


def sample_content():
    return ContentAsset(
        content_id="CNT-001",
        name="MQL Welcome Email",
        content_type=ContentType.EMAIL,
        subject="Welcome {{first_name}}",
        preheader="Your next step starts here.",
        html_body="""
        <html>
        <head>
            <style>
                body { font-family: Arial; }
            </style>
        </head>
        <body>
            <h1>Hello {{first_name}}</h1>
            <p>Welcome to {{product_name}}.</p>
        </body>
        </html>
        """,
        status=ContentStatus.DRAFT,
        personalization_tokens=[
            PersonalizationToken(
                token="first_name",
                description="Contact first name",
                default_value="there",
            ),
            PersonalizationToken(
                token="product_name",
                description="Product name",
                default_value="CampaignOS",
            ),
        ],
    )


def test_extract_tokens():
    content = """
    Hello {{first_name}}.
    Welcome to {{product_name}}.
    """

    assert extract_tokens(content) == [
        "first_name",
        "product_name",
    ]


def test_render_personalization():
    content = "Hello {{first_name}}"

    rendered = render_personalization(
        content,
        {"first_name": "Sunny"},
    )

    assert rendered == "Hello Sunny"


def test_unknown_token_is_preserved():
    content = "Hello {{first_name}}"

    rendered = render_personalization(
        content,
        {},
    )

    assert rendered == "Hello {{first_name}}"


def test_html_validation():
    content = sample_content()

    errors = validate_html(content.html_body)

    assert errors == []


def test_html_validation_detects_missing_structure():
    errors = validate_html("<p>Hello</p>")

    assert "HTML document should contain an <html> element." in errors
    assert "HTML document should contain a <body> element." in errors
    assert "Email should contain a <style> block." in errors


def test_personalization_validation():
    content = sample_content()

    assert validate_personalization(content) == []


def test_undeclared_token_validation():
    content = sample_content()
    content.html_body = content.html_body.replace(
        "{{product_name}}",
        "{{campaign_name}}",
    )

    errors = validate_personalization(content)

    assert any(
        "campaign_name" in error
        for error in errors
    )


def test_content_validation():
    content = sample_content()

    assert content.validate() == []


def test_content_validation_requires_subject():
    content = sample_content()
    content.subject = ""

    errors = content.validate()

    assert "Subject line is required." in errors


def test_content_summary():
    content = sample_content()

    summary = content_summary(content)

    assert summary["content_id"] == "CNT-001"
    assert summary["type"] == "Email"
    assert summary["token_count"] == 2


def test_prepare_preview():
    content = sample_content()

    rendered, errors = prepare_preview(
        content,
        {
            "first_name": "Sunny",
            "product_name": "CampaignOS",
        },
    )

    assert errors == []
    assert "Hello Sunny" in rendered
    assert "CampaignOS" in rendered
