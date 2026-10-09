from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnMapping:
    canonical_field: str
    source_column: str


@dataclass(frozen=True)
class MappingDecision:
    dataset_id: str
    tenant_id: str
    dataset_type: str
    mappings: tuple[ColumnMapping, ...]
    approved: bool = False
    approved_by: str | None = None


class ColumnMappingService:
    def create_decision(
        self,
        dataset_id: str,
        tenant_id: str,
        dataset_type: str,
        suggested_column_mapping: tuple[tuple[str, str], ...],
    ) -> MappingDecision:
        mappings = tuple(
            ColumnMapping(
                canonical_field=canonical,
                source_column=source,
            )
            for canonical, source in suggested_column_mapping
        )

        return MappingDecision(
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            dataset_type=dataset_type,
            mappings=mappings,
        )

    def approve(
        self,
        decision: MappingDecision,
        approved_by: str,
    ) -> MappingDecision:
        if not approved_by.strip():
            raise ValueError("approved_by is required.")

        if decision.approved:
            raise ValueError("Mapping is already approved.")

        if not decision.mappings:
            raise ValueError("Cannot approve an empty column mapping.")

        return MappingDecision(
            dataset_id=decision.dataset_id,
            tenant_id=decision.tenant_id,
            dataset_type=decision.dataset_type,
            mappings=decision.mappings,
            approved=True,
            approved_by=approved_by,
        )
