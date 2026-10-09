from dataclasses import fields, is_dataclass
from typing import Any


class CanonicalHydrationError(ValueError):
    pass


class CanonicalRecord(dict):
    """
    Compatibility record for the current GTM intelligence layer.

    Supports both:
        record["tenant_id"]
    and:
        record.tenant_id
    """

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def hydrate_record(
    record: dict[str, Any],
    model_type: type,
    tenant_id: str,
):
    if not isinstance(record, dict):
        raise CanonicalHydrationError(
            f"Expected dictionary input, got {type(record).__name__}."
        )

    if not is_dataclass(model_type):
        raise CanonicalHydrationError(
            f"{model_type.__name__} must be a dataclass."
        )

    model_fields = fields(model_type)
    field_names = {field.name for field in model_fields}

    values = {
        key: value
        for key, value in record.items()
        if key in field_names
    }

    if "tenant_id" in field_names:
        values["tenant_id"] = tenant_id

    missing = []

    for field in model_fields:
        if field.name not in values:
            if (
                field.default.__class__.__name__ == "_MISSING_TYPE"
                and field.default_factory.__class__.__name__
                == "_MISSING_TYPE"
            ):
                missing.append(field.name)

    if missing:
        raise CanonicalHydrationError(
            f"Missing canonical fields for {model_type.__name__}: "
            f"{sorted(missing)}"
        )

    hydrated = model_type(**values)

    if hasattr(hydrated, "tenant_id"):
        if hydrated.tenant_id != tenant_id:
            raise CanonicalHydrationError(
                "Hydrated record tenant does not match requested tenant."
            )

    return hydrated


def hydrate_records(
    records: list[dict[str, Any]],
    model_type: type,
    tenant_id: str,
):
    return tuple(
        hydrate_record(
            record=record,
            model_type=model_type,
            tenant_id=tenant_id,
        )
        for record in records
    )


def canonicalize_records(
    records: list[dict[str, Any]],
) -> tuple[CanonicalRecord, ...]:
    return tuple(
        CanonicalRecord(record)
        for record in records
    )
