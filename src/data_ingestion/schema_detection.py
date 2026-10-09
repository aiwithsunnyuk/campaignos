from dataclasses import dataclass
from typing import Literal


DatasetType = Literal[
    "lead",
    "campaign",
    "engagement",
    "registration",
    "enrollment",
    "unknown",
]


@dataclass(frozen=True)
class SchemaDetectionResult:
    dataset_type: DatasetType
    confidence: float
    required_fields_found: tuple[str, ...]
    missing_fields: tuple[str, ...]
    suggested_column_mapping: tuple[tuple[str, str], ...]


class SchemaDetector:
    SCHEMAS = {
        "lead": {
            "required": ("lead_id", "email"),
            "aliases": {
                "lead_id": ("lead_id", "leadid", "lead id", "id"),
                "email": ("email", "email_address", "emailaddress"),
                "name": ("name", "full_name", "fullname"),
                "phone": ("phone", "phone_number", "mobile"),
            },
        },
        "campaign": {
            "required": ("campaign_id", "campaign_name"),
            "aliases": {
                "campaign_id": ("campaign_id", "campaignid", "campaign id"),
                "campaign_name": ("campaign_name", "campaign", "campaign_name"),
                "status": ("status", "campaign_status"),
            },
        },
        "engagement": {
            "required": ("engagement_id", "lead_id"),
            "aliases": {
                "engagement_id": (
                    "engagement_id",
                    "engagementid",
                    "engagement id",
                ),
                "lead_id": ("lead_id", "leadid", "lead id"),
                "event_type": ("event_type", "event", "activity_type"),
                "channel": ("channel", "engagement_channel"),
            },
        },
        "registration": {
            "required": ("registration_id", "lead_id", "course_id"),
            "aliases": {
                "registration_id": (
                    "registration_id",
                    "registrationid",
                    "registration id",
                ),
                "lead_id": ("lead_id", "leadid", "lead id"),
                "course_id": ("course_id", "courseid", "course id"),
            },
        },
        "enrollment": {
            "required": ("enrollment_id", "lead_id", "course_id"),
            "aliases": {
                "enrollment_id": (
                    "enrollment_id",
                    "enrollmentid",
                    "enrollment id",
                ),
                "lead_id": ("lead_id", "leadid", "lead id"),
                "course_id": ("course_id", "courseid", "course id"),
            },
        },
    }

    def detect(self, columns: tuple[str, ...]) -> SchemaDetectionResult:
        normalized = {
            self._normalize(column): column
            for column in columns
        }

        candidates = []

        for dataset_type, schema in self.SCHEMAS.items():
            mapping = {}

            for canonical, aliases in schema["aliases"].items():
                for alias in aliases:
                    normalized_alias = self._normalize(alias)
                    if normalized_alias in normalized:
                        mapping[canonical] = normalized[normalized_alias]
                        break

            required = schema["required"]
            found = tuple(field for field in required if field in mapping)
            missing = tuple(field for field in required if field not in mapping)

            confidence = len(found) / len(required)

            candidates.append(
                (
                    confidence,
                    len(mapping),
                    dataset_type,
                    found,
                    missing,
                    tuple(mapping.items()),
                )
            )

        best = max(candidates, key=lambda item: (item[0], item[1]))

        confidence, _, dataset_type, found, missing, mapping = best

        if confidence == 0:
            return SchemaDetectionResult(
                dataset_type="unknown",
                confidence=0.0,
                required_fields_found=(),
                missing_fields=(),
                suggested_column_mapping=(),
            )

        return SchemaDetectionResult(
            dataset_type=dataset_type,
            confidence=round(confidence, 4),
            required_fields_found=found,
            missing_fields=missing,
            suggested_column_mapping=mapping,
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return (
            str(value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )
