#!/usr/bin/env python
# anvil/services.py

import csv
import hashlib
import json
from pathlib import Path
from django.apps import apps
from django.db import transaction

from anvil.constants import (
    ANVIL_UPLOAD_TABLES,
    ANVIL_UPLOAD_TABLE_MODEL_MAP,
    TSV_CONTENT_TYPE,   
)
from anvil.models import (
    AnvilUpload,
    AnvilUploadArtifact,
    AnvilUploadTable,
    AnvilUploadValidationRun,
)


@transaction.atomic
def initialize_upload_tables(*, upload, changed_by=None):
    """
    Ensure that the upload has one AnvilUploadTable row for every GREGoR table
    expected in the Dashboard-generated AnVIL package.

    This is idempotent.
    """

    upload_tables = []

    for table_name in ANVIL_UPLOAD_TABLES:
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
def initialize_upload_package(*, upload, changed_by=None):
    """
    Initialize the database records for a deterministic AnVIL upload package.

    This creates:
    - 21 AnvilUploadTable rows
    - 21 planned table TSV artifact rows

    It does not write TSV files yet.
    """

    upload_tables = initialize_upload_tables(
        upload=upload,
        changed_by=changed_by,
    )
    tsv_artifacts = initialize_upload_tsv_artifacts(
        upload=upload,
        upload_tables=upload_tables,
        changed_by=changed_by,
    )

    return {
        "upload": upload,
        "upload_tables": upload_tables,
        "tsv_artifacts": tsv_artifacts,
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


def _row_from_object(*, obj, fields):
    row = {}

    for field in fields:
        column_name = field.column

        # field.value_from_object handles ForeignKey fields correctly by using
        # the underlying attname value rather than the related object instance.
        value = field.value_from_object(obj)

        row[column_name] = _serialize_tsv_value(value)

    return row


def _sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()

def _get_model(app_label, model_name):
    return apps.get_model(app_label, model_name)


def _error(
    *,
    code,
    table,
    model,
    pk,
    field=None,
    value=None,
    message,
):
    return {
        "severity": "error",
        "code": code,
        "table": table,
        "model": model,
        "pk": str(pk),
        "field": field,
        "value": value,
        "message": message,
    }


def _validate_participant_solve_status():
    Participant = _get_model("metadata", "participant")

    errors = []

    for participant in Participant.objects.filter(solve_status="Affected"):
        errors.append(
            _error(
                code="invalid_solve_status",
                table="participant",
                model="metadata.Participant",
                pk=participant.pk,
                field="solve_status",
                value=participant.solve_status,
                message=(
                    "Participant solve_status cannot be 'Affected'. "
                    "Use a GREGoR solve status such as 'Unsolved' instead."
                ),
            )
        )

    return errors


def _validate_phenotype_onset_age_range():
    Phenotype = _get_model("metadata", "phenotype")

    errors = []

    for phenotype in Phenotype.objects.filter(onset_age_range__iexact="unknown"):
        errors.append(
            _error(
                code="invalid_onset_age_range",
                table="phenotype",
                model="metadata.Phenotype",
                pk=phenotype.pk,
                field="onset_age_range",
                value=phenotype.onset_age_range,
                message=(
                    "Phenotype onset_age_range cannot be 'unknown'. "
                    "Use a valid HPO onset term or leave the field blank."
                ),
            )
        )

    return errors


def _validate_delete_marked_alignment_sets():
    """
    Delete-marked alignment set rows should not be exported into generated
    GREGoR upload tables.

    This check is intentionally narrow and only applies to alignment set tables.
    """

    checks = [
        (
            "aligned_dna_short_read_set",
            "experiments",
            "aligneddnashortreadset",
            "experiments.AlignedDnaShortReadSet",
        ),
        (
            "aligned_nanopore_set",
            "experiments",
            "alignednanoporeset",
            "experiments.AlignedNanoporeSet",
        ),
        (
            "aligned_pac_bio_set",
            "experiments",
            "alignedpacbioset",
            "experiments.AlignedPacBioSet",
        ),
    ]

    errors = []

    for table_name, app_label, model_name, display_model in checks:
        model_class = _get_model(app_label, model_name)

        for obj in model_class.objects.filter(pk__contains="-delete"):
            errors.append(
                _error(
                    code="delete_marked_alignment_set",
                    table=table_name,
                    model=display_model,
                    pk=obj.pk,
                    field="pk",
                    value=str(obj.pk),
                    message=(
                        "Delete-marked alignment set records should not be "
                        "included in an AnVIL upload."
                    ),
                )
            )

    return errors


def collect_upload_source_validation_errors():
    """
    Collect known source-data errors that should block AnVIL upload generation.

    This is intentionally narrow. It is the first Dashboard-side validator, not
    a full replacement for GREGoR JSON Schema validation or the DCC validator.
    """

    errors = []
    errors.extend(_validate_participant_solve_status())
    errors.extend(_validate_phenotype_onset_age_range())
    errors.extend(_validate_delete_marked_alignment_sets())

    return errors


@transaction.atomic
def validate_upload_source_data(*, upload, changed_by=None):
    """
    Validate currently loaded Dashboard source data for an AnVIL upload.

    Creates an AnvilUploadValidationRun and marks the upload as either failed
    validation or ready for review.
    """

    validation_run = AnvilUploadValidationRun.objects.create(
        upload=upload,
        validator_type=AnvilUploadValidationRun.ValidatorType.DASHBOARD,
        validator_version="dashboard-source-data-v0.1",
        changed_by=changed_by,
    )

    validation_run.mark_running()
    validation_run.save()

    errors = collect_upload_source_validation_errors()
    passed = len(errors) == 0

    summary = {
        "validator": "dashboard-source-data-v0.1",
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
            "Dashboard source-data validation passed."
            if passed
            else "Dashboard source-data validation failed."
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

    package = initialize_upload_package(
        upload=upload,
        changed_by=changed_by,
    )

    upload_tables_by_name = {
        upload_table.table_name: upload_table
        for upload_table in package["upload_tables"]
    }

    artifacts_by_table_name = {
        artifact.upload_table.table_name: artifact
        for artifact in package["tsv_artifacts"]
    }

    package_dir = Path(output_dir) / str(upload.upload_id)
    tables_dir = package_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    generated = []

    for table_name in ANVIL_UPLOAD_TABLES:
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
                    )
                )
                row_count += 1

        upload_table.row_count = row_count
        upload_table.column_names = column_names
        upload_table.generation_status = _get_generation_status(
            AnvilUploadTable.GenerationStatus,
            "GENERATED",
            "generated",
        )

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