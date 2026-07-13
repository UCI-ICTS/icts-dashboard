#!/usr/bin/env python
# anvil/services.py

from django.apps import apps
from django.db import transaction

from anvil.models import (
    AnvilUploadTable,
    AnvilUploadArtifact,
    AnvilUpload,
    AnvilUploadValidationRun,
)


ANVIL_UPLOAD_TABLES = [
    "family",
    "participant",
    "phenotype",
    "analyte",
    "genetic_findings",
    "experiment",
    "experiment_dna_short_read",
    "experiment_rna_short_read",
    "experiment_nanopore",
    "experiment_pac_bio",
    "aligned",
    "aligned_dna_short_read",
    "aligned_rna_short_read",
    "aligned_nanopore",
    "aligned_pac_bio",
    "aligned_dna_short_read_set",
    "aligned_nanopore_set",
    "aligned_pac_bio_set",
    "called_variants_dna_short_read",
    "called_variants_nanopore",
    "called_variants_pac_bio",
]

TSV_CONTENT_TYPE = "text/tab-separated-values"

@transaction.atomic
def initialize_upload_tables(*, upload, changed_by=None):
    """
    Ensure that the upload has one AnvilUploadTable row for every GREGoR table
    expected in the Dashboard-generated AnVIL package.

    This is idempotent: calling it multiple times for the same upload will not
    create duplicate table rows.
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
def initialize_upload_tsv_artifacts(*, upload, changed_by=None):
    """
    Ensure that the upload has one planned TSV artifact for every expected
    GREGoR upload table.

    #TODO: This does not write files yet. It creates the durable artifact package that the
    exporter will later fill with byte_size, sha256, storage_uri, and generated
    status.
    """
    upload_tables =initialize_upload_tables(
        upload=upload,
        changed_by=changed_by
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
                "changed_by": changed_by
            }
        )
        artifacts.append(artifact)

    return artifacts

@transaction.atomic
def build_upload_tsv_package(*, upload, changed_by=None):
    """
    Build the first deterministic AnVIL upload package.

    For now, this only creates:
    - 21 AnvilUploadTable rows
    - 21 planned table TSV artifacts

    #TODO: Make this function can call the real TSV row serializers.
    """

    upload_tables = initialize_upload_tables(
        upload=upload,
        changed_by=changed_by,
    )
    tsv_artifacts = initialize_upload_tsv_artifacts(
        upload=upload,
        changed_by=changed_by,
    )

    return {
        "upload": upload,
        "upload_tables": upload_tables,
        "tsv_artifacts": tsv_artifacts,
    }


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
    """

    This catches the known invalid participant fixture issue without attempting
    to fully reimplement JSON Schema validation yet.
    """

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
    """
    GREGoR v1.12 does not allow onset_age_range='unknown'.

    Blank is acceptable for the Dashboard fixture, but the literal value
    'unknown' should be blocked.
    """

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
    The upload-source fixture should not include delete-marked alignment set
    rows for the generated GREGoR upload tables.

    This intentionally checks the alignment set tables only. The current valid
    fixture may still contain a delete-marked metadata.family row, which is a
    separate policy question and not part of this first validator.
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
                        "included in an AnVIL upload source fixture."
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