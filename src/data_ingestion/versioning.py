from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetVersion:
    dataset_id: str
    tenant_id: str
    dataset_type: str
    version: int
    file_name: str
    previous_version: int | None
    promoted_by: str | None = None


class DatasetVersionService:
    def create_version(
        self,
        dataset_id: str,
        tenant_id: str,
        dataset_type: str,
        file_name: str,
        existing_versions: tuple[DatasetVersion, ...] = (),
    ) -> DatasetVersion:
        tenant_versions = tuple(
            version
            for version in existing_versions
            if version.dataset_id == dataset_id
            and version.tenant_id == tenant_id
        )

        next_version = (
            max(version.version for version in tenant_versions) + 1
            if tenant_versions
            else 1
        )

        previous_version = (
            next_version - 1
            if tenant_versions
            else None
        )

        return DatasetVersion(
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            dataset_type=dataset_type,
            version=next_version,
            file_name=file_name,
            previous_version=previous_version,
        )

    def promote(
        self,
        version: DatasetVersion,
        promoted_by: str,
    ) -> DatasetVersion:
        if not promoted_by.strip():
            raise ValueError("promoted_by is required.")

        return DatasetVersion(
            dataset_id=version.dataset_id,
            tenant_id=version.tenant_id,
            dataset_type=version.dataset_type,
            version=version.version,
            file_name=version.file_name,
            previous_version=version.previous_version,
            promoted_by=promoted_by,
        )
