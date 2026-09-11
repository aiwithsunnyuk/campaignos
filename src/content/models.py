from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class ContentStatus(str, Enum):
    DRAFT = "Draft"
    READY = "Ready"
    ARCHIVED = "Archived"


class ContentType(str, Enum):
    EMAIL = "Email"
    LANDING_PAGE = "Landing Page"
    SMS = "SMS"


@dataclass
class PersonalizationToken:
    token: str
    description: str
    default_value: str = ""


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
    metadata: Dict[str, str] = field(default_factory=dict)

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

        token_names = [
            token.token for token in self.personalization_tokens
        ]

        if len(token_names) != len(set(token_names)):
            errors.append(
                "Personalization token names must be unique."
            )

        return errors
