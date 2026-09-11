import re
from typing import Dict, List, Tuple

from src.content.models import ContentAsset


TOKEN_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")


def extract_tokens(html_body: str) -> List[str]:
    if not html_body:
        return []

    return sorted(set(TOKEN_PATTERN.findall(html_body)))


def render_personalization(
    content: str,
    values: Dict[str, str],
) -> str:
    if not content:
        return ""

    def replace_token(match):
        token = match.group(1)
        return str(values.get(token, match.group(0)))

    return TOKEN_PATTERN.sub(replace_token, content)


def validate_html(content: str) -> List[str]:
    errors: List[str] = []

    if not content.strip():
        errors.append("HTML content cannot be empty.")

    if "<html" not in content.lower():
        errors.append("HTML document should contain an <html> element.")

    if "<body" not in content.lower():
        errors.append("HTML document should contain a <body> element.")

    if "<style" not in content.lower():
        errors.append("Email should contain a <style> block.")

    return errors


def validate_personalization(
    content: ContentAsset,
) -> List[str]:
    errors: List[str] = []

    declared_tokens = {
        token.token
        for token in content.personalization_tokens
    }

    used_tokens = set(extract_tokens(content.html_body))

    undeclared = used_tokens - declared_tokens

    if undeclared:
        errors.append(
            "Undeclared personalization tokens: "
            + ", ".join(sorted(undeclared))
        )

    return errors


def prepare_preview(
    content: ContentAsset,
    values: Dict[str, str],
) -> Tuple[str, List[str]]:
    errors = []

    errors.extend(content.validate())
    errors.extend(validate_html(content.html_body))
    errors.extend(validate_personalization(content))

    rendered = render_personalization(
        content.html_body,
        values,
    )

    return rendered, errors


def content_summary(
    content: ContentAsset,
) -> Dict[str, object]:
    return {
        "content_id": content.content_id,
        "name": content.name,
        "type": content.content_type.value,
        "status": content.status.value,
        "subject": content.subject,
        "preheader": content.preheader,
        "tokens": extract_tokens(content.html_body),
        "token_count": len(
            extract_tokens(content.html_body)
        ),
        "html_length": len(content.html_body),
    }
