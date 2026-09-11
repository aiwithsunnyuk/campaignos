from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ContentType(str, Enum):
    EMAIL = "Email"
    LANDING_PAGE = "Landing Page"
    SMS = "SMS"
    SOCIAL = "Social"
    WEBINAR = "Webinar"


class ContentStatus(str, Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    ARCHIVED = "Archived"


@dataclass
class PersonalizationToken:
    token: str
    description: str = ""
    default_value: str = ""

    def render(self, contact: Dict[str, Any]) -> str:
        value = contact.get(self.token)

        if value is None or str(value).strip() == "":
            return self.default_value

        return str(value)


@dataclass
class ContentAsset:
    content_id: str
    name: str
    content_type: ContentType = ContentType.EMAIL
    subject: str = ""
    preheader: str = ""
    html_body: str = ""
    status: ContentStatus = ContentStatus.DRAFT
    personalization_tokens: List[PersonalizationToken] = field(
        default_factory=list
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.content_id:
            errors.append("Content ID is required.")

        if not self.name:
            errors.append("Content name is required.")

        if not self.subject:
            errors.append("Subject line is required.")

        if not self.html_body:
            errors.append("HTML body is required.")

        declared_tokens = {
            token.token
            for token in self.personalization_tokens
        }

        supported_tokens = set()

        for token in self.personalization_tokens:
            if not token.token:
                errors.append(
                    "Personalization token name is required."
                )

        import re

        detected_tokens = set(
            re.findall(
                r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}",
                self.html_body,
            )
        )

        supported_tokens.update(detected_tokens)

        undeclared = detected_tokens - declared_tokens

        for token in sorted(undeclared):
            errors.append(
                f"Undeclared personalization token: "
                f"{{{{{token}}}}}"
            )

        return errors

    def render(self, contact: Dict[str, Any]) -> str:
        rendered = self.html_body

        for token in self.personalization_tokens:
            placeholder = "{{" + token.token + "}}"
            rendered = rendered.replace(
                placeholder,
                token.render(contact),
            )

        return rendered


# Backward-compatible alias used by some application code.
Content = ContentAsset
