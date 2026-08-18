#!/usr/bin/env python
# anvil/services.py

import csv
import hashlib
import json
from pathlib import Path
from django.apps import apps
from django.db import transaction
from django.utils import timezone

from config.selectors import TableValidator, remove_na

from anvil.constants import (
    ANVIL_UPLOAD_TABLES,
    ANVIL_UPLOAD_TABLE_MODEL_MAP,
    TSV_CONTENT_TYPE,
    MANIFEST_CONTENT_TYPE,
)
from anvil.models import (
    AnvilUpload,
    AnvilUploadArtifact,
    AnvilUploadTable,
    AnvilUploadValidationRun,
)


@transaction.atomic
def initialize_upload_tables(*, upload:dict, tables:list, changed_by=None):
    """
    Ensure that the upload has one AnvilUploadTable row for every GREGoR table
    expected in the Dashboard-generated AnVIL package.

    This is idempotent.
    """

    selected_tables = _get_selected_upload_tables(tables=tables)
    upload_tables = []

    for table_name in selected_tables:
        upload_table, _created = AnvilUploadTable.objects.get_or_create(
            upload=upload,
            table_name=table_name,
            defaults={
                "changed_by": changed_by,
            },
        )
        upload_tables.append(upload_table)

    return upload_tables


@transaction.atomic
def initialize_upload_tsv_artifacts(*, upload, upload_tables=None, changed_by=None):
    """
    Ensure that the upload has one planned TSV artifact for every expected
    GREGoR upload table.

    This does not write files. It creates artifact records that the TSV generator
    will later fill with byte_size, sha256, storage_uri, and generated status.
    """

    if upload_tables is None:
        upload_tables = initialize_upload_tables(
            upload=upload,
            changed_by=changed_by,
        )

    artifacts = []

    for upload_table in upload_tables:
        file_name = f"{upload_table.table_name}.tsv"
        relative_path = f"tables/{file_name}"

        artifact, _created = AnvilUploadArtifact.objects.get_or_create(
            upload=upload,
            relative_path=relative_path,
            defaults={
                "upload_table": upload_table,
                "artifact_type": AnvilUploadArtifact.ArtifactType.TABLE_TSV,
                "generation_status": AnvilUploadArtifact.GenerationStatus.PENDING,
                "file_name": file_name,
                "content_type": TSV_CONTENT_TYPE,
                "changed_by": changed_by,
            },
        )

        artifacts.append(artifact)

    return artifacts


@transaction.atomic
def initialize_upload_package(*, upload:dict, tables:list=None, changed_by=None):
    """
    Initialize the database records for a deterministic AnVIL upload package.

    This creates:
    - AnvilUploadTable rows
    - planned table TSV artifact rows
    - upload_manifest.json

    It does not write TSV files.
    """

    selected_tables = _get_selected_upload_tables(tables=tables)

    upload_tables = initialize_upload_tables(
        upload=upload,
        tables=selected_tables,
        changed_by=changed_by, 
    )
    tsv_artifacts = initialize_upload_tsv_artifacts(
        upload=upload,
        upload_tables=upload_tables,
        changed_by=changed_by,
    )

    upload_manifest = initialize_upload_manifest_artifact(
        upload=upload,
        selected_tables=selected_tables,
        changed_by=changed_by,
    )

    return {
        "upload": upload,
        "upload_tables": upload_tables,
        "tsv_artifacts": tsv_artifacts,
        "upload_manifest": upload_manifest,
    }


DASHBOARD_ONLY_EXPORT_FIELDS = {
    "created_at",
    "updated_at",
    "needs_review",
    "changed_by",
}


def _get_generation_status(enum_class, name, fallback):
    """
    Small compatibility helper so this service does not break if the model
    enum names are slightly different during early development.
    """

    return getattr(enum_class, name, fallback)


def _get_upload_table_model(*, table_name):
    app_label, model_name = ANVIL_UPLOAD_TABLE_MODEL_MAP[table_name]
    return apps.get_model(app_label, model_name)


def _get_export_fields(model_class):
    """
    First-pass export field selection.

    This intentionally uses concrete Django model fields and excludes Dashboard
    audit/review fields. Later, this can be replaced with schema-defined column
    order from the GREGoR data model.
    """

    fields = []

    for field in model_class._meta.fields:
        if field.name in DASHBOARD_ONLY_EXPORT_FIELDS:
            continue

        fields.append(field)

    return fields


def _serialize_tsv_value(value):
    if value is None:
        return ""

    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True)

    return str(value)


def _row_from_object(*, obj, fields, serialize_for_tsv=False):
    row = {}

    for field in fields:
        column_name = field.column

        value = field.value_from_object(obj)

        if serialize_for_tsv:
            value = _serialize_tsv_value(value=value)

        row[column_name] = value

    return row


def _sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _package_error(
    *,
    code,
    message,
    table=None,
    relative_path=None,
    expected=None,
    observed=None,
):
    return {
        "severity": "error",
        "code": code,
        "table": table,
        "relative_path": relative_path,
        "expected": expected,
        "observed": observed,
        "message": message,
    }


def _read_tsv_header_and_validate_rows(*, artifact):
    """
    Validate one generated TSV file against the DB metadata recorded for its
    AnvilUploadTable and AnvilUploadArtifact.

    This is package-integrity validation, not full GREGoR schema validation.
    """

    errors = []

    upload_table = artifact.upload_table

    if upload_table is None:
        return [
            _package_error(
                code="missing_upload_table_for_artifact",
                relative_path=artifact.relative_path,
                message="TABLE_TSV artifact is not linked to an AnvilUploadTable.",
            )
        ]

    table_name = upload_table.table_name
    path = Path(artifact.storage_uri) if artifact.storage_uri else None

    if path is None:
        return [
            _package_error(
                code="missing_artifact_storage_uri",
                table=table_name,
                relative_path=artifact.relative_path,
                message="Generated TSV artifact is missing storage_uri.",
            )
        ]

    if not path.exists():
        return [
            _package_error(
                code="missing_artifact_file",
                table=table_name,
                relative_path=artifact.relative_path,
                observed=str(path),
                message="Generated TSV artifact file does not exist.",
            )
        ]

    observed_byte_size = path.stat().st_size

    if artifact.byte_size != observed_byte_size:
        errors.append(
            _package_error(
                code="artifact_byte_size_mismatch",
                table=table_name,
                relative_path=artifact.relative_path,
                expected=artifact.byte_size,
                observed=observed_byte_size,
                message="Recorded artifact byte_size does not match file size.",
            )
        )

    observed_sha256 = _sha256_file(path)

    if artifact.sha256 != observed_sha256:
        errors.append(
            _package_error(
                code="artifact_sha256_mismatch",
                table=table_name,
                relative_path=artifact.relative_path,
                expected=artifact.sha256,
                observed=observed_sha256,
                message="Recorded artifact sha256 does not match file contents.",
            )
        )

    model_class = _get_upload_table_model(table_name=table_name)
    primary_key_column = model_class._meta.pk.column

    row_count = 0
    seen_primary_keys = set()
    duplicate_primary_keys = set()

    with path.open("r", newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle, delimiter="\t")
        fieldnames = reader.fieldnames or []

        if fieldnames != upload_table.column_names:
            errors.append(
                _package_error(
                    code="tsv_header_mismatch",
                    table=table_name,
                    relative_path=artifact.relative_path,
                    expected=upload_table.column_names,
                    observed=fieldnames,
                    message=(
                        "TSV header does not match AnvilUploadTable.column_names."
                    ),
                )
            )

        if primary_key_column not in fieldnames:
            errors.append(
                _package_error(
                    code="tsv_missing_primary_key_column",
                    table=table_name,
                    relative_path=artifact.relative_path,
                    expected=primary_key_column,
                    observed=fieldnames,
                    message="TSV is missing the source model primary-key column.",
                )
            )

        for row in reader:
            row_count += 1

            if primary_key_column not in fieldnames:
                continue

            primary_key_value = row.get(primary_key_column)

            if primary_key_value in seen_primary_keys:
                duplicate_primary_keys.add(primary_key_value)

            seen_primary_keys.add(primary_key_value)

    if row_count != upload_table.row_count:
        errors.append(
            _package_error(
                code="tsv_row_count_mismatch",
                table=table_name,
                relative_path=artifact.relative_path,
                expected=upload_table.row_count,
                observed=row_count,
                message="TSV row count does not match AnvilUploadTable.row_count.",
            )
        )

    if duplicate_primary_keys:
        errors.append(
            _package_error(
                code="duplicate_tsv_primary_keys",
                table=table_name,
                relative_path=artifact.relative_path,
                expected="unique primary keys",
                observed=sorted(duplicate_primary_keys),
                message="TSV contains duplicate primary-key values.",
            )
        )

    return errors


def _validate_table_tsv_artifacts(*, upload):
    errors = []

    expected_relative_paths = {
        f"tables/{table_name}.tsv"
        for table_name in ANVIL_UPLOAD_TABLES
    }

    artifacts = list(
        upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
        )
        .select_related("upload_table")
        .order_by("relative_path")
    )

    observed_relative_paths = {
        artifact.relative_path
        for artifact in artifacts
    }

    missing_paths = sorted(expected_relative_paths - observed_relative_paths)
    unexpected_paths = sorted(observed_relative_paths - expected_relative_paths)

    if missing_paths:
        errors.append(
            _package_error(
                code="missing_table_tsv_artifacts",
                expected=sorted(expected_relative_paths),
                observed=sorted(observed_relative_paths),
                message=f"Missing expected TABLE_TSV artifacts: {missing_paths}",
            )
        )

    if unexpected_paths:
        errors.append(
            _package_error(
                code="unexpected_table_tsv_artifacts",
                expected=sorted(expected_relative_paths),
                observed=sorted(observed_relative_paths),
                message=f"Unexpected TABLE_TSV artifacts found: {unexpected_paths}",
            )
        )

    for artifact in artifacts:
        errors.extend(_read_tsv_header_and_validate_rows(artifact=artifact))

    return errors


def _load_manifest_payload(*, upload):
    manifest_artifacts = list(
        upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST,
        ).order_by("relative_path")
    )

    if len(manifest_artifacts) == 0:
        return None, [
            _package_error(
                code="missing_upload_manifest_artifact",
                expected="one UPLOAD_MANIFEST artifact",
                observed=0,
                message=(
                    "Upload package is missing an UPLOAD_MANIFEST artifact. "
                    "Run generate_upload_manifest first."
                ),
            )
        ]

    if len(manifest_artifacts) > 1:
        return None, [
            _package_error(
                code="multiple_upload_manifest_artifacts",
                expected=1,
                observed=len(manifest_artifacts),
                message="Upload package has multiple UPLOAD_MANIFEST artifacts.",
            )
        ]

    artifact = manifest_artifacts[0]
    path = Path(artifact.storage_uri) if artifact.storage_uri else None

    errors = []

    if path is None:
        errors.append(
            _package_error(
                code="missing_manifest_storage_uri",
                relative_path=artifact.relative_path,
                message="UPLOAD_MANIFEST artifact is missing storage_uri.",
            )
        )
        return None, errors

    if not path.exists():
        errors.append(
            _package_error(
                code="missing_manifest_file",
                relative_path=artifact.relative_path,
                observed=str(path),
                message="Manifest file does not exist.",
            )
        )
        return None, errors

    observed_byte_size = path.stat().st_size

    if artifact.byte_size != observed_byte_size:
        errors.append(
            _package_error(
                code="manifest_byte_size_mismatch",
                relative_path=artifact.relative_path,
                expected=artifact.byte_size,
                observed=observed_byte_size,
                message="Recorded manifest byte_size does not match file size.",
            )
        )

    observed_sha256 = _sha256_file(path)

    if artifact.sha256 != observed_sha256:
        errors.append(
            _package_error(
                code="manifest_sha256_mismatch",
                relative_path=artifact.relative_path,
                expected=artifact.sha256,
                observed=observed_sha256,
                message="Recorded manifest sha256 does not match file contents.",
            )
        )

    try:
        with path.open("r", encoding="utf-8") as file_handle:
            manifest = json.load(file_handle)
    except json.JSONDecodeError as error:
        errors.append(
            _package_error(
                code="invalid_manifest_json",
                relative_path=artifact.relative_path,
                message=f"Manifest file is not valid JSON: {error}",
            )
        )
        return None, errors

    return manifest, errors


def _validate_manifest_payload(*, upload):
    manifest, errors = _load_manifest_payload(upload=upload)

    if manifest is None:
        return errors

    summary = manifest.get("summary", {})

    if summary.get("table_count") != len(ANVIL_UPLOAD_TABLES):
        errors.append(
            _package_error(
                code="manifest_table_count_mismatch",
                expected=len(ANVIL_UPLOAD_TABLES),
                observed=summary.get("table_count"),
                message="Manifest table_count does not match expected table count.",
            )
        )

    if summary.get("table_tsv_artifact_count") != len(ANVIL_UPLOAD_TABLES):
        errors.append(
            _package_error(
                code="manifest_table_tsv_artifact_count_mismatch",
                expected=len(ANVIL_UPLOAD_TABLES),
                observed=summary.get("table_tsv_artifact_count"),
                message=(
                    "Manifest table_tsv_artifact_count does not match expected "
                    "TSV artifact count."
                ),
            )
        )

    manifest_table_names = {
        table_entry.get("table_name")
        for table_entry in manifest.get("tables", [])
    }

    expected_table_names = set(ANVIL_UPLOAD_TABLES)

    if manifest_table_names != expected_table_names:
        errors.append(
            _package_error(
                code="manifest_table_names_mismatch",
                expected=sorted(expected_table_names),
                observed=sorted(manifest_table_names),
                message="Manifest table names do not match expected upload tables.",
            )
        )

    db_tables_by_name = {
        upload_table.table_name: upload_table
        for upload_table in upload.upload_tables.all()
    }

    for table_entry in manifest.get("tables", []):
        table_name = table_entry.get("table_name")
        upload_table = db_tables_by_name.get(table_name)

        if upload_table is None:
            continue

        if table_entry.get("row_count") != upload_table.row_count:
            errors.append(
                _package_error(
                    code="manifest_table_row_count_mismatch",
                    table=table_name,
                    expected=upload_table.row_count,
                    observed=table_entry.get("row_count"),
                    message=(
                        "Manifest table row_count does not match "
                        "AnvilUploadTable.row_count."
                    ),
                )
            )

        if table_entry.get("column_names") != upload_table.column_names:
            errors.append(
                _package_error(
                    code="manifest_table_column_names_mismatch",
                    table=table_name,
                    expected=upload_table.column_names,
                    observed=table_entry.get("column_names"),
                    message=(
                        "Manifest table column_names do not match "
                        "AnvilUploadTable.column_names."
                    ),
                )
            )

    manifest_artifacts_by_path = {
        artifact_entry.get("relative_path"): artifact_entry
        for artifact_entry in manifest.get("table_tsv_artifacts", [])
    }

    db_tsv_artifacts = upload.artifacts.filter(
        artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
    ).order_by("relative_path")

    expected_artifact_paths = {
        artifact.relative_path
        for artifact in db_tsv_artifacts
    }

    observed_artifact_paths = set(manifest_artifacts_by_path)

    if observed_artifact_paths != expected_artifact_paths:
        errors.append(
            _package_error(
                code="manifest_artifact_paths_mismatch",
                expected=sorted(expected_artifact_paths),
                observed=sorted(observed_artifact_paths),
                message=(
                    "Manifest table_tsv_artifacts do not match generated "
                    "TABLE_TSV artifacts."
                ),
            )
        )

    for artifact in db_tsv_artifacts:
        manifest_artifact = manifest_artifacts_by_path.get(artifact.relative_path)

        if manifest_artifact is None:
            continue

        if manifest_artifact.get("byte_size") != artifact.byte_size:
            errors.append(
                _package_error(
                    code="manifest_artifact_byte_size_mismatch",
                    table=artifact.upload_table.table_name if artifact.upload_table_id else None,
                    relative_path=artifact.relative_path,
                    expected=artifact.byte_size,
                    observed=manifest_artifact.get("byte_size"),
                    message=(
                        "Manifest artifact byte_size does not match "
                        "AnvilUploadArtifact.byte_size."
                    ),
                )
            )

        if manifest_artifact.get("sha256") != artifact.sha256:
            errors.append(
                _package_error(
                    code="manifest_artifact_sha256_mismatch",
                    table=artifact.upload_table.table_name if artifact.upload_table_id else None,
                    relative_path=artifact.relative_path,
                    expected=artifact.sha256,
                    observed=manifest_artifact.get("sha256"),
                    message=(
                        "Manifest artifact sha256 does not match "
                        "AnvilUploadArtifact.sha256."
                    ),
                )
            )

    return errors


def _get_selected_upload_tables(*, tables=None):
    if tables is None:
        return list(ANVIL_UPLOAD_TABLES)

    selected_tables = list(dict.fromkeys(tables))
    invalid_tables = sorted(set(selected_tables) - set(ANVIL_UPLOAD_TABLES))

    if invalid_tables:
        raise ValueError(f"Invalid AnVIL upload tables: {invalid_tables}")

    return selected_tables


def _json_safe_datetime(value):
    if value is None:
        return None

    return value.isoformat()


def _get_generated_table_tsv_artifacts(*, upload):
    return (
        upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
        )
        .select_related("upload_table")
        .order_by("relative_path")
    )


def _ensure_tsv_artifacts_are_generated(*, upload):
    artifacts = list(_get_generated_table_tsv_artifacts(upload=upload))

    if len(artifacts) != len(ANVIL_UPLOAD_TABLES):
        raise ValueError(
            f"Expected {len(ANVIL_UPLOAD_TABLES)} TSV artifacts, "
            f"found {len(artifacts)}. Run generate_upload_tsvs first."
        )

    missing_metadata = [
        artifact.relative_path
        for artifact in artifacts
        if (
            not artifact.storage_uri
            or not artifact.sha256
            or artifact.byte_size is None
        )
    ]

    if missing_metadata:
        raise ValueError(
            "Some TSV artifacts are missing generated file metadata. "
            f"Run generate_upload_tsvs first. Missing: {missing_metadata}"
        )

    return artifacts


def _build_upload_manifest_dict(*, upload):
    """
    Build manifest data for the generated table TSV package.

    Important: this manifest describes the generated TSV artifacts. It does not
    include the manifest artifact itself, because doing that would create a
    self-referential checksum problem.
    """

    upload.refresh_from_db()

    table_tsv_artifacts = _ensure_tsv_artifacts_are_generated(upload=upload)
    upload_tables = upload.upload_tables.order_by("table_name")
    validation_runs = upload.validation_runs.order_by("started_at")

    table_entries = []

    for upload_table in upload_tables:
        table_entries.append(
            {
                "table_name": upload_table.table_name,
                "generation_status": upload_table.generation_status,
                "row_count": upload_table.row_count,
                "column_names": upload_table.column_names,
                "source_summary": upload_table.source_summary,
                "generation_error": upload_table.generation_error,
            }
        )

    artifact_entries = []

    for artifact in table_tsv_artifacts:
        artifact_entries.append(
            {
                "relative_path": artifact.relative_path,
                "file_name": artifact.file_name,
                "artifact_type": artifact.artifact_type,
                "generation_status": artifact.generation_status,
                "content_type": artifact.content_type,
                "byte_size": artifact.byte_size,
                "sha256": artifact.sha256,
                "storage_uri": artifact.storage_uri,
                "upload_table": (
                    artifact.upload_table.table_name
                    if artifact.upload_table_id
                    else None
                ),
                "generation_error": artifact.generation_error,
                "metadata": artifact.metadata,
            }
        )

    validation_entries = []

    for validation_run in validation_runs:
        validation_entries.append(
            {
                "validator_type": validation_run.validator_type,
                "validator_version": validation_run.validator_version,
                "status": validation_run.status,
                "started_at": _json_safe_datetime(validation_run.started_at),
                "finished_at": _json_safe_datetime(validation_run.finished_at),
                "error_count": validation_run.error_count,
                "warning_count": validation_run.warning_count,
                "message": validation_run.message,
            }
        )

    return {
        "manifest_version": "dashboard-anvil-upload-manifest-v0.1",
        "generated_at": timezone.now().isoformat(),
        "upload": {
            "upload_id": str(upload.upload_id),
            "status": upload.status,
            "gregor_model_version": upload.gregor_model_version,
            "created_at": _json_safe_datetime(upload.created_at),
            "updated_at": _json_safe_datetime(upload.updated_at),
        },
        "summary": {
            "table_count": upload_tables.count(),
            "table_tsv_artifact_count": len(table_tsv_artifacts),
            "validation_run_count": validation_runs.count(),
        },
        "tables": table_entries,
        "table_tsv_artifacts": artifact_entries,
        "validation_runs": validation_entries,
    }


def _build_initialized_manifest(*, upload, selected_tables):
    excluded_tables = [
        {
            "table_name": table_name,
            "reason": "not selected at initialization",
        }
        for table_name in ANVIL_UPLOAD_TABLES
        if table_name not in selected_tables
    ]

    return {
        "manifest_version": "dashboard-anvil-upload-manifest-v0.1",
        "manifest_state": "initialized",
        "upload": {
            "upload_id": str(upload.upload_id),
            "status": upload.status,
            "gregor_model_version": upload.gregor_model_version,
            "created_at": _json_safe_datetime(upload.created_at),
            "updated_at": _json_safe_datetime(upload.updated_at),
        },
        "tables": {
            "included": selected_tables,
            "excluded": excluded_tables,
        },
        "validation": {
            "source": None,
            "package": None,
        },
        "artifacts": {
            "table_tsvs": [],
            "manifest": None,
        },
    }


def collect_upload_package_validation_errors(*, upload):
    """
    Validate generated upload package files and recorded package metadata.

    This checks local package integrity only. It does not perform full GREGoR
    schema validation, cross-table foreign-key validation, WDL validation, GCS
    checks, or AnVIL submission checks.
    """

    errors = []
    errors.extend(_validate_table_tsv_artifacts(upload=upload))
    errors.extend(_validate_manifest_payload(upload=upload))

    return errors


@transaction.atomic
def validate_upload_package(*, upload, changed_by=None):
    """
    Validate generated package files and metadata for one upload.

    This is the Dashboard package-integrity validator. It assumes TSV generation
    and manifest generation have already run.
    """

    validation_run = AnvilUploadValidationRun.objects.create(
        upload=upload,
        validator_type=AnvilUploadValidationRun.ValidatorType.DASHBOARD,
        validator_version="dashboard-package-v0.1",
        changed_by=changed_by,
    )

    validation_run.mark_running()
    validation_run.save()

    errors = collect_upload_package_validation_errors(upload=upload)
    passed = len(errors) == 0

    summary = {
        "validator": "dashboard-package-v0.1",
        "passed": passed,
        "error_count": len(errors),
        "warning_count": 0,
        "errors": errors,
    }

    validation_run.error_count = len(errors)
    validation_run.warning_count = 0
    validation_run.mark_complete(
        passed=passed,
        message=(
            "Dashboard package validation passed."
            if passed
            else "Dashboard package validation failed."
        ),
        summary=summary,
    )
    validation_run.save()

    upload.status = (
        AnvilUpload.Status.READY_FOR_REVIEW
        if passed
        else AnvilUpload.Status.VALIDATION_FAILED
    )

    if changed_by is not None:
        upload.changed_by = changed_by

    upload.save()

    return validation_run


@transaction.atomic
def validate_upload_source_data(*, upload, changed_by=None):
    """
    Validate currently loaded Dashboard source data for an AnVIL upload.

    Creates an AnvilUploadValidationRun and marks the upload as either failed
    validation or ready for review.
    """

    manifest_artifact = get_upload_manifest_artifact(upload=upload)

    if manifest_artifact is None:
        raise ValueError("Upload manifest does not exist. Run initialize first.")

    manifest = manifest_artifact.metadata or {}
    selected_tables = manifest.get("tables", {}).get("included", [])

    validation_run = AnvilUploadValidationRun.objects.create(
        upload=upload,
        validator_type=AnvilUploadValidationRun.ValidatorType.DASHBOARD,
        validator_version="dashboard-source-data-v0.2",
        changed_by=changed_by,
    )

    validation_run.mark_running()
    validation_run.save()

    table_results = {}
    table_summaries = {}
    error_count = 0
    warning_count = 0

    for table_name in selected_tables:
        model_class = _get_upload_table_model(table_name=table_name)
        fields = _get_export_fields(model_class=model_class)
        queryset = model_class.objects.all().order_by(model_class._meta.pk.name)

        source_row_count = queryset.count()
        excluded_rows = []

        for obj in queryset:
            row = _row_from_object(obj=obj, fields=fields)

            validator = TableValidator()
            validator.validate_json(remove_na(row), table_name)
            validation_results = validator.get_validation_results()

            if not validation_results["valid"]:
                import pdb; pdb.set_trace()
                excluded_rows.append(
                    {
                        "pk": str(obj.pk),
                        "reason": "schema validation failed",
                        "errors": validation_results["errors"],
                    }
                )

        excluded_row_count = len(excluded_rows)
        included_row_count = source_row_count - excluded_row_count
        table_error_count = excluded_row_count

        source_status = "passed" if table_error_count == 0 else "failed"

        table_summary = {
            "source_status": source_status,
            "source_row_count": source_row_count,
            "included_row_count": included_row_count,
            "excluded_row_count": excluded_row_count,
            "error_count": table_error_count,
        }

        table_results[table_name] = {
            "selected": True,
            **table_summary,
            "excluded_rows": excluded_rows,
        }

        table_summaries[table_name] = table_summary

        upload_table = upload.upload_tables.filter(table_name=table_name).first()

        if upload_table is not None:
            upload_table.source_summary = table_summary

            if changed_by is not None:
                upload_table.changed_by = changed_by

            upload_table.save()

        error_count += table_error_count

    passed = error_count == 0

    summary = {
        "validator": "dashboard-source-data-v0.2",
        "passed": passed,
        "error_count": error_count,
        "warning_count": warning_count,
        "tables": table_summaries,
    }

    manifest.setdefault("tables", {})
    manifest["tables"]["by_name"] = table_results

    manifest.setdefault("validation", {})
    manifest["validation"]["source"] = {
        "status": "passed" if passed else "failed",
        "validator": "dashboard-source-data-v0.2",
        "error_count": error_count,
        "warning_count": warning_count,
        "run_id": validation_run.id,
    }

    manifest["manifest_state"] = (
        "source_validated" if passed else "source_validation_failed"
    )

    manifest_artifact.metadata = manifest
    manifest_artifact.generation_status = (
        AnvilUploadArtifact.GenerationStatus.GENERATED
        if passed
        else AnvilUploadArtifact.GenerationStatus.FAILED
    )

    if changed_by is not None:
        manifest_artifact.changed_by = changed_by

    manifest_artifact.save()

    validation_run.error_count = error_count
    validation_run.warning_count = warning_count
    validation_run.summary = summary
    validation_run.mark_complete(
        passed=passed,
        message=(
            "Dashboard source-data validation passed."
            if passed
            else "Dashboard source-data validation failed."
        ),
        summary=summary,
    )
    validation_run.summary = summary
    validation_run.save()

    upload.status = (
        AnvilUpload.Status.READY_FOR_REVIEW
        if passed
        else AnvilUpload.Status.VALIDATION_FAILED
    )

    if changed_by is not None:
        upload.changed_by = changed_by

    upload.save()

    return validation_run


@transaction.atomic
def generate_upload_tsvs(*, upload, output_dir, changed_by=None):
    """
    Generate TSV files for the initialized AnVIL upload package.

    This is the first real file-writing slice. It does not yet attempt to be a
    complete GREGoR schema exporter. It writes deterministic TSVs from current
    Django model fields and updates AnvilUploadTable / AnvilUploadArtifact
    metadata.

    Later slices can replace _get_export_fields() with schema-defined GREGoR
    column ordering.
    """

    manifest_artifact = get_upload_manifest_artifact(upload=upload)

    manifest = manifest_artifact.metadata or {}
    selected_tables = manifest.get("tables", {}).get("include", [])

    upload_tables_by_name = {
        upload_table.table_name: upload_table
        for upload_table in upload.upload_tables.filter(table_name__in=selected_tables)
    }

    artifacts_by_table_name = {
        artifact.upload_table.table_name: artifact
        for artifact in upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            upload_table__table_name__in=selected_tables,
        ).select_related("upload_table")
    }

    package_dir = Path(output_dir) / str(upload.upload_id)
    tables_dir = package_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    generated = []

    for table_name in selected_tables:
        model_class = _get_upload_table_model(table_name=table_name)
        fields = _get_export_fields(model_class)

        column_names = [field.column for field in fields]

        queryset = model_class.objects.all().order_by(model_class._meta.pk.name)

        upload_table = upload_tables_by_name[table_name]
        artifact = artifacts_by_table_name[table_name]

        file_path = tables_dir / f"{table_name}.tsv"

        row_count = 0

        with file_path.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(
                file_handle,
                fieldnames=column_names,
                delimiter="\t",
                lineterminator="\n",
                extrasaction="ignore",
            )
            writer.writeheader()

            for obj in queryset:
                writer.writerow(
                    _row_from_object(
                        obj=obj,
                        fields=fields,
                        serialize_for_tsv=True,
                    )
                )
                row_count += 1

        upload_table.row_count = row_count
        upload_table.column_names = column_names
        upload_table.generation_status = AnvilUploadTable.GenerationStatus.GENERATED

        if changed_by is not None:
            upload_table.changed_by = changed_by

        upload_table.save()

        artifact.file_name = f"{table_name}.tsv"
        artifact.relative_path = f"tables/{table_name}.tsv"
        artifact.content_type = TSV_CONTENT_TYPE
        artifact.byte_size = file_path.stat().st_size
        artifact.sha256 = _sha256_file(file_path)
        artifact.storage_uri = str(file_path)
        artifact.generation_status = _get_generation_status(
            AnvilUploadArtifact.GenerationStatus,
            "GENERATED",
            "generated",
        )

        if changed_by is not None:
            artifact.changed_by = changed_by

        artifact.save()

        generated.append(
            {
                "table_name": table_name,
                "relative_path": artifact.relative_path,
                "file_path": str(file_path),
                "row_count": row_count,
                "column_names": column_names,
                "sha256": artifact.sha256,
                "byte_size": artifact.byte_size,
            }
        )

    return {
        "upload": upload,
        "package_dir": str(package_dir),
        "tables_dir": str(tables_dir),
        "generated": generated,
    }


@transaction.atomic
def generate_upload_manifest(*, upload, output_dir, changed_by=None):
    """
    Generate manifest.json for a Dashboard-generated AnVIL upload package.

    """

    package_dir = Path(output_dir) / str(upload.upload_id)
    package_dir.mkdir(parents=True, exist_ok=True)

    manifest = _build_upload_manifest_dict(upload=upload)
    manifest_path = package_dir / "manifest.json"

    with manifest_path.open("w", encoding="utf-8") as file_handle:
        json.dump(
            manifest,
            file_handle,
            indent=2,
            sort_keys=True,
        )
        file_handle.write("\n")

    artifact, _created = AnvilUploadArtifact.objects.get_or_create(
        upload=upload,
        relative_path="manifest.json",
        defaults={
            "artifact_type": AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST,
            "generation_status": AnvilUploadArtifact.GenerationStatus.PENDING,
            "file_name": "manifest.json",
            "content_type": MANIFEST_CONTENT_TYPE,
            "changed_by": changed_by,
        },
    )

    artifact.artifact_type = AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST
    artifact.generation_status = _get_generation_status(
        AnvilUploadArtifact.GenerationStatus,
        "GENERATED",
        "generated",
    )
    artifact.file_name = "manifest.json"
    artifact.content_type = MANIFEST_CONTENT_TYPE
    artifact.byte_size = manifest_path.stat().st_size
    artifact.sha256 = _sha256_file(manifest_path)
    artifact.storage_uri = str(manifest_path)
    artifact.metadata = {
        "manifest_version": manifest["manifest_version"],
        "table_count": manifest["summary"]["table_count"],
        "table_tsv_artifact_count": manifest["summary"]["table_tsv_artifact_count"],
        "validation_run_count": manifest["summary"]["validation_run_count"],
    }

    if changed_by is not None:
        artifact.changed_by = changed_by

    artifact.save()

    return {
        "upload": upload,
        "manifest": manifest,
        "manifest_path": str(manifest_path),
        "artifact": artifact,
    }


def initialize_upload_manifest_artifact(*, upload, selected_tables, changed_by=None):
    manifest = _build_initialized_manifest(
        upload=upload,
        selected_tables=selected_tables,
    )

    artifact, _created = AnvilUploadArtifact.objects.get_or_create(
        upload=upload,
        relative_path="manifest.json",
        defaults={
            "artifact_type": AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST,
            "generation_status": AnvilUploadArtifact.GenerationStatus.PENDING,
            "file_name": "manifest.json",
            "content_type": MANIFEST_CONTENT_TYPE,
            "metadata": manifest,
            "changed_by": changed_by,
        },
    )

    artifact.artifact_type = AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST
    artifact.generation_status = AnvilUploadArtifact.GenerationStatus.PENDING
    artifact.file_name = "manifest.json"
    artifact.content_type = MANIFEST_CONTENT_TYPE
    artifact.metadata = manifest

    if changed_by is not None:
        artifact.changed_by = changed_by

    artifact.save()

    return artifact


def get_upload_manifest_artifact(upload):
    return (
        upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST,
            relative_path="manifest.json",
        )
        .order_by("-updated_at", "-created_at")
        .first()
    )
