from dataclasses import dataclass

import pytest

from src.data_sources.canonical import (
    CanonicalHydrationError,
    hydrate_record,
    hydrate_records,
)


@dataclass(frozen=True)
class ExampleLead:
    lead_id: str
    tenant_id: str
    email: str


def test_hydrates_dictionary_into_canonical_object():
    result = hydrate_record(
        record={
            "lead_id": "L1",
            "tenant_id": "wrong-value",
            "email": "one@example.com",
            "extra_source_field": "ignored",
        },
        model_type=ExampleLead,
        tenant_id="reetha",
    )

    assert isinstance(result, ExampleLead)
    assert result.lead_id == "L1"
    assert result.email == "one@example.com"
    assert result.tenant_id == "reetha"


def test_hydrates_multiple_records():
    result = hydrate_records(
        records=[
            {
                "lead_id": "L1",
                "tenant_id": "reetha",
                "email": "one@example.com",
            },
            {
                "lead_id": "L2",
                "tenant_id": "reetha",
                "email": "two@example.com",
            },
        ],
        model_type=ExampleLead,
        tenant_id="reetha",
    )

    assert len(result) == 2
    assert all(isinstance(item, ExampleLead) for item in result)


def test_missing_required_field_is_rejected():
    with pytest.raises(
        CanonicalHydrationError,
        match="Missing canonical fields",
    ):
        hydrate_record(
            record={
                "lead_id": "L1",
            },
            model_type=ExampleLead,
            tenant_id="reetha",
        )


def test_non_dictionary_is_rejected():
    with pytest.raises(
        CanonicalHydrationError,
        match="Expected dictionary",
    ):
        hydrate_record(
            record=[],
            model_type=ExampleLead,
            tenant_id="reetha",
        )
