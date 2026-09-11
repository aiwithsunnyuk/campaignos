import sys
from pathlib import Path
from html import escape

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.content.models import Content
from src.content.engine import (
    prepare_preview,
    content_summary,
)


st.set_page_config(
    page_title="CampaignOS | Content Studio",
    page_icon="✉️",
    layout="wide",
)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def build_content(
    content_id: str,
    name: str,
    subject: str,
    preheader: str,
    html_body: str,
) -> Content:
    """
    Create an M6 Content object.

    The Content model is responsible for validation and
    token-aware rendering. The Streamlit page only supplies
    the content configuration.
    """
    return Content(
        content_id=content_id,
        name=name,
        content_type="Email",
        subject=subject,
        preheader=preheader,
        html_body=html_body,
    )


def sample_html() -> str:
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{{product_name}}</title>
<style>
    body {
        margin: 0;
        padding: 0;
        background: #f4f6f8;
        font-family: Arial, sans-serif;
    }

    .container {
        max-width: 680px;
        margin: 30px auto;
        background: #ffffff;
        border-radius: 10px;
        overflow: hidden;
    }

    .header {
        padding: 28px;
        background: #111827;
        color: #ffffff;
    }

    .body {
        padding: 32px;
        color: #1f2937;
        line-height: 1.6;
    }

    .cta {
        display: inline-block;
        padding: 13px 22px;
        background: #2563eb;
        color: #ffffff;
        text-decoration: none;
        border-radius: 6px;
        font-weight: bold;
    }

    .footer {
        padding: 20px 32px;
        background: #f9fafb;
        color: #6b7280;
        font-size: 12px;
    }
</style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>{{product_name}}</h1>
        <p>CampaignOS Marketing Automation</p>
    </div>

    <div class="body">

        <h2>Hello {{first_name}},</h2>

        <p>
            Thank you for your interest in
            <strong>{{product_name}}</strong>.
        </p>

        <p>
            Based on your engagement with our marketing
            program, we thought this information may be
            relevant to you.
        </p>

        <p>
            Explore the next step and discover how
            {{product_name}} can support your goals.
        </p>

        <p>
            <a href="#" class="cta">
                Explore {{product_name}}
            </a>
        </p>

        <p>
            Regards,<br>
            CampaignOS Marketing Team
        </p>

    </div>

    <div class="footer">
        You are receiving this message because you
        subscribed to marketing communications.
    </div>

</div>

</body>
</html>
"""


# -------------------------------------------------------------------
# Page Header
# -------------------------------------------------------------------

st.title("✉️ Content Studio")

st.caption(
    "Create, personalize, validate and preview HTML email "
    "content using the CampaignOS M6 content engine."
)


# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------

st.sidebar.header("Content Configuration")

content_id = st.sidebar.text_input(
    "Content ID",
    value="CNT-M6-001",
)

content_name = st.sidebar.text_input(
    "Content Name",
    value="MQL Welcome Email",
)

subject = st.sidebar.text_input(
    "Subject Line",
    value="Welcome to {{product_name}}, {{first_name}}",
)

preheader = st.sidebar.text_input(
    "Preheader",
    value="Discover what {{product_name}} can do for you.",
)

st.sidebar.divider()

st.sidebar.subheader("Personalization")

st.sidebar.caption(
    "Supported demonstration tokens:"
)

st.sidebar.code(
    "{{first_name}}\n"
    "{{last_name}}\n"
    "{{product_name}}"
)

st.sidebar.divider()

st.sidebar.subheader("Preview Contact")

preview_first_name = st.sidebar.text_input(
    "First Name",
    value="Sunny",
)

preview_last_name = st.sidebar.text_input(
    "Last Name",
    value="UK",
)

preview_product = st.sidebar.text_input(
    "Product Name",
    value="CampaignOS",
)


# -------------------------------------------------------------------
# Content Editor
# -------------------------------------------------------------------

st.subheader("Email Content")

editor_col, preview_col = st.columns(
    [1, 1],
    gap="large",
)


with editor_col:

    st.markdown("### HTML / CSS Editor")

    html_body = st.text_area(
        "Email HTML",
        value=sample_html(),
        height=620,
        label_visibility="collapsed",
    )

    st.caption(
        "Use CampaignOS personalization tokens such as "
        "`{{first_name}}` and `{{product_name}}`."
    )


# -------------------------------------------------------------------
# Build Content Object
# -------------------------------------------------------------------

content = build_content(
    content_id=content_id,
    name=content_name,
    subject=subject,
    preheader=preheader,
    html_body=html_body,
)


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

validation_errors = content.validate()


with preview_col:

    st.markdown("### Content Preview")

    if validation_errors:

        st.error("Content validation failed.")

        for error in validation_errors:
            st.write(f"• {error}")

    else:

        st.success("Content validation passed.")

        preview_contact = {
            "first_name": preview_first_name,
            "last_name": preview_last_name,
            "product_name": preview_product,
        }

        try:

            rendered_html, preview_errors = prepare_preview(
                content,
                preview_contact,
            )

        except Exception as exc:

            rendered_html = ""
            preview_errors = [
                f"Preview generation failed: {exc}"
            ]

        if preview_errors:

            st.warning("Preview requires attention.")

            for error in preview_errors:
                st.write(f"• {error}")

        elif rendered_html:

            st.components.v1.html(
                rendered_html,
                height=620,
                scrolling=True,
            )


# -------------------------------------------------------------------
# Content Summary
# -------------------------------------------------------------------

st.divider()

st.subheader("Content Metadata")

try:

    summary = content_summary(content)

    summary_col1, summary_col2, summary_col3, summary_col4 = (
        st.columns(4)
    )

    summary_col1.metric(
        "Content ID",
        summary.get("content_id", content_id),
    )

    summary_col2.metric(
        "Type",
        summary.get("type", "Email"),
    )

    summary_col3.metric(
        "Tokens",
        summary.get("token_count", 0),
    )

    summary_col4.metric(
        "Validation",
        "Valid" if not validation_errors else "Issues",
    )

except Exception as exc:

    st.warning(
        f"Unable to generate content summary: {exc}"
    )


# -------------------------------------------------------------------
# Personalization Token Test
# -------------------------------------------------------------------

st.subheader("Personalization Test")

token_col1, token_col2, token_col3 = st.columns(3)

with token_col1:
    st.metric(
        "First Name",
        preview_first_name,
    )

with token_col2:
    st.metric(
        "Last Name",
        preview_last_name,
    )

with token_col3:
    st.metric(
        "Product",
        preview_product,
    )

st.info(
    "The preview above demonstrates how CampaignOS "
    "can render reusable marketing content against "
    "individual contact attributes."
)


# -------------------------------------------------------------------
# Subject + Preheader Preview
# -------------------------------------------------------------------

st.subheader("Message Header Preview")

header_col1, header_col2 = st.columns(2)

with header_col1:

    st.markdown("**Subject**")

    rendered_subject = (
        subject
        .replace(
            "{{first_name}}",
            preview_first_name,
        )
        .replace(
            "{{last_name}}",
            preview_last_name,
        )
        .replace(
            "{{product_name}}",
            preview_product,
        )
    )

    st.code(rendered_subject)


with header_col2:

    st.markdown("**Preheader**")

    rendered_preheader = (
        preheader
        .replace(
            "{{first_name}}",
            preview_first_name,
        )
        .replace(
            "{{last_name}}",
            preview_last_name,
        )
        .replace(
            "{{product_name}}",
            preview_product,
        )
    )

    st.code(rendered_preheader)


# -------------------------------------------------------------------
# Export
# -------------------------------------------------------------------

st.subheader("Content Export")

export_col1, export_col2 = st.columns(2)

with export_col1:

    st.download_button(
        label="⬇️ Export HTML",
        data=html_body.encode("utf-8"),
        file_name=(
            f"{content_id.lower()}_email.html"
        ),
        mime="text/html",
        width="stretch",
    )


with export_col2:

    metadata_text = (
        f"Content ID: {content_id}\n"
        f"Content Name: {content_name}\n"
        f"Type: Email\n"
        f"Subject: {subject}\n"
        f"Preheader: {preheader}\n"
        f"Validation: "
        f"{'Valid' if not validation_errors else 'Issues'}\n"
    )

    st.download_button(
        label="⬇️ Export Content Metadata",
        data=metadata_text.encode("utf-8"),
        file_name=(
            f"{content_id.lower()}_metadata.txt"
        ),
        mime="text/plain",
        width="stretch",
    )


# -------------------------------------------------------------------
# Marketing Automation Design Notes
# -------------------------------------------------------------------

st.divider()

st.subheader("Marketing Automation Design Notes")

st.markdown(
    """
### Content Creation

CampaignOS treats email content as a reusable marketing
asset rather than embedding HTML directly into a campaign.

### Personalization

Dynamic tokens such as:

```text
{{first_name}}
{{last_name}}
{{product_name}}

### Preview and Validation

Before content is used in a campaign, CampaignOS validates required fields, resolves personalization tokens, and provides a rendered preview.

### Reusability

Content assets are designed to be reused across campaigns, segments, business types, and regions.

### Vendor-Neutral Design

The content engine does not depend on Oracle Eloqua, Salesforce, Outlook, or another proprietary marketing platform.

CampaignOS demonstrates the underlying marketing automation concepts locally using synthetic data only.
"""
)

