import pandas as pd

from src.segmentation.models import (
    SegmentDefinition,
    SegmentResult,
)


SUPPORTED_OPERATORS = {
    "equals",
    "not_equals",
    "contains",
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "in",
}


def _apply_rule(
    dataframe: pd.DataFrame,
    field: str,
    operator: str,
    value,
) -> pd.Series:

    if field not in dataframe.columns:
        raise ValueError(f"Unknown segmentation field: {field}")

    if operator not in SUPPORTED_OPERATORS:
        raise ValueError(f"Unsupported operator: {operator}")

    series = dataframe[field]

    if operator == "equals":
        return series == value

    if operator == "not_equals":
        return series != value

    if operator == "contains":
        return series.astype(str).str.contains(
            str(value),
            case=False,
            na=False,
        )

    if operator == "greater_than":
        return series >= value

    if operator == "greater_than_or_equal":
        return series >= value

    if operator == "less_than":
        return series < value

    if operator == "less_than_or_equal":
        return series <= value

    if operator == "in":
        if not isinstance(value, (list, tuple, set)):
            raise ValueError(
                "'in' operator requires a list, tuple, or set."
            )
        return series.isin(value)

    raise ValueError(f"Unsupported operator: {operator}")


def build_segment(
    contacts: pd.DataFrame,
    segment: SegmentDefinition,
) -> SegmentResult:

    segment.validate()

    if contacts.empty:
        return SegmentResult(
            segment_id=segment.segment_id,
            segment_name=segment.segment_name,
            audience_count=0,
            audience_percentage=0.0,
            contacts=contacts.copy(),
        )

    masks = []

    for rule in segment.rules:
        masks.append(
            _apply_rule(
                contacts,
                rule.field,
                rule.operator,
                rule.value,
            )
        )

    if segment.logic == "AND":
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask & mask
    else:
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask | mask

    matched_contacts = contacts.loc[combined_mask].copy()

    audience_count = len(matched_contacts)

    audience_percentage = (
        audience_count / len(contacts) * 100
        if len(contacts) > 0
        else 0.0
    )

    return SegmentResult(
        segment_id=segment.segment_id,
        segment_name=segment.segment_name,
        audience_count=audience_count,
        audience_percentage=round(audience_percentage, 2),
        contacts=matched_contacts,
    )