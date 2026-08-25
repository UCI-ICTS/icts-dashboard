#!/usr/bin/env python
# anvil/models.py

from django.db import models
from django.utils import timezone

from metadata.models import TimeStampedModel
#TODO: this shouls move out of metadata into a new top level models file like
#  config/models.py

class AnvilUpload(TimeStampedModel):
    """
    A named Dashboard upload candidate for GREGoR / AnVIL submission.

    This first model intentionally stores only upload identity, model version,
    lifecycle status, and human review notes. 
    
    TODO: Membership, generated table artifacts, validation results, and 
    external AnVIL operations are added in later migrations.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        VALIDATING = "validating", "Validating"
        VALIDATION_FAILED = "validation_failed", "Validation failed"
        READY_FOR_REVIEW = "ready_for_review", "Ready for review"
        APPROVED = "approved", "Approved"
        EXPORTED = "exported", "Exported"

    upload_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text=(
            "Immutable human-readable upload identifier, for example "
            "'UCI_GREGoR_test_upload_v1'."
        ),
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text="Current Dashboard lifecycle state for this upload.",
    )

    gregor_model_version = models.CharField(
        max_length=20,
        default="1.12",
        help_text=(
            "Canonical GREGoR data-model version used when validating and "
            "exporting this upload."
        ),
    )

    notes = models.TextField(
        blank=True,
        help_text="Optional upload-level notes for review or handoff.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AnVIL upload"
        verbose_name_plural = "AnVIL uploads"

    def __str__(self):
        return f"{self.upload_id} ({self.get_status_display()})"
    

class AnvilUploadTable(TimeStampedModel):
    """
    One GREGoR table included in an AnVIL upload package.

    A row is created for each table the upload builder expects to generate.
    It records upload-level table metadata, rather than the individual source
    records that eventually populate that table.
    """

    class GenerationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATING = "generating", "Generating"
        GENERATED = "generated", "Generated"
        FAILED = "failed", "Failed"

    upload = models.ForeignKey(
        AnvilUpload,
        on_delete=models.CASCADE,
        related_name="upload_tables",
    )

    table_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text=(
            "Canonical GREGoR table name, such as participant, experiment, "
            "aligned, or called_variants_dna_short_read."
        ),
    )

    generation_status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
        db_index=True,
    )

    row_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of exported rows in this upload table.",
    )

    column_names = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Ordered list of columns written to the exported TSV. "
            "This preserves the exact generated table shape."
        ),
    )

    source_summary = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "upload-builder summary of source models, source counts, filters, "
            "or other non-authoritative provenance details."
        ),
    )

    generation_error = models.TextField(
        blank=True,
        help_text="Most recent table-generation error, if generation failed.",
    )

    class Meta:
        ordering = ["table_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["upload", "table_name"],
                name="anvil_upload_unique_table_name",
            ),
        ]
        verbose_name = "AnVIL upload table"
        verbose_name_plural = "AnVIL upload tables"

    def __str__(self):
        return f"{self.upload.upload_id}: {self.table_name}"


class AnvilUploadArtifact(TimeStampedModel):
    """
    A concrete generated file associated with an AnVIL upload.

    Examples:
    - participant.tsv
    - experiment.tsv
    - upload_manifest.json
    - validate_gregor_model.inputs.json
    - validation_report.json
    - upload-package.tar.gz

    #TODO: Synthetic BAM, BAI, VCF, and VCF index objects may also be represented here
    later, but the first implementation will focus on generated package files.
    """

    class ArtifactType(models.TextChoices):
        TABLE_TSV = "table_tsv", "Table TSV"
        UPLOAD_MANIFEST = "upload_manifest", "Upload manifest"
        WDL_INPUTS = "wdl_inputs", "Validation WDL inputs"
        VALIDATION_REPORT = "validation_report", "Validation report"
        README = "readme", "README"
        PACKAGE_ARCHIVE = "package_archive", "Package archive"
        OTHER = "other", "Other"

    class GenerationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATED = "generated", "Generated"
        FAILED = "failed", "Failed"
        SUPERSEDED = "superseded", "Superseded"

    upload = models.ForeignKey(
        AnvilUpload,
        on_delete=models.CASCADE,
        related_name="artifacts",
    )

    upload_table = models.ForeignKey(
        AnvilUploadTable,
        on_delete=models.SET_NULL,
        related_name="artifacts",
        null=True,
        blank=True,
        help_text=(
            "Associated upload table for table-specific artifacts. "
            "Blank for upload-wide artifacts such as manifests and reports."
        ),
    )

    artifact_type = models.CharField(
        max_length=40,
        choices=ArtifactType.choices,
        db_index=True,
    )

    generation_status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
        db_index=True,
    )

    relative_path = models.CharField(
        max_length=500,
        help_text=(
            "Path inside the generated upload package, such as "
            "tables/participant.tsv or validation/report.json."
        ),
    )

    file_name = models.CharField(
        max_length=255,
        help_text="File name only, retained for convenient listing and display.",
    )

    content_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME content type, such as text/tab-separated-values.",
    )

    byte_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text="Generated file size in bytes.",
    )

    sha256 = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="SHA-256 digest of the generated artifact.",
    )

    storage_uri = models.CharField(
        max_length=1000,
        blank=True,
        help_text=(
            "Optional storage location. Initially this may be a local package "
            "path; later it may hold a gs:// URI after staging."
        ),
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Additional artifact metadata, such as source table, expected MD5, "
            "or package-generation details."
        ),
    )

    generation_error = models.TextField(
        blank=True,
        help_text="Most recent artifact-generation error, if generation failed.",
    )

    class Meta:
        ordering = ["relative_path"]
        constraints = [
            models.UniqueConstraint(
                fields=["upload", "relative_path"],
                name="anvil_upload_unique_artifact_path",
            ),
        ]
        verbose_name = "AnVIL upload artifact"
        verbose_name_plural = "AnVIL upload artifacts"

    def __str__(self):
        return f"{self.upload.upload_id}: {self.relative_path}"


class AnvilUploadValidationRun(TimeStampedModel):
    """
    One recorded upload-validation attempt.

    #TODO: Dashboard validation runs will be created first. Local Docker validator runs
    and later real AnVIL validate_gregor_model workflow runs use the same model.
    """

    class ValidatorType(models.TextChoices):
        DASHBOARD = "dashboard", "Dashboard upload validator"
        LOCAL = "local", "Local AnVIL intake harness"
        ANVIL = "anvil", "AnVIL validate_gregor_model workflow"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        ERROR = "error", "Error"

    upload = models.ForeignKey(
        AnvilUpload,
        on_delete=models.CASCADE,
        related_name="validation_runs",
    )

    validator_type = models.CharField(
        max_length=20,
        choices=ValidatorType.choices,
        default=ValidatorType.DASHBOARD,
        db_index=True,
    )

    validator_version = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Validator implementation/version, such as dashboard-0.1, "
            "local-harness-0.1, or a Dockstore workflow version."
        ),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    error_count = models.PositiveIntegerField(default=0)
    warning_count = models.PositiveIntegerField(default=0)

    summary = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Machine-readable validation summary, including table counts, "
            "error categories, and validator output metadata."
        ),
    )

    message = models.TextField(
        blank=True,
        help_text="Human-readable validation outcome or failure summary.",
    )

    report_artifact = models.ForeignKey(
        AnvilUploadArtifact,
        on_delete=models.SET_NULL,
        related_name="validation_reports",
        null=True,
        blank=True,
        help_text="Optional generated report artifact for this validation run.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AnVIL upload validation run"
        verbose_name_plural = "AnVIL upload validation runs"

    def __str__(self):
        return (
            f"{self.upload.upload_id}: "
            f"{self.get_validator_type_display()} "
            f"({self.get_status_display()})"
        )

    def mark_running(self):
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.finished_at = None

    def mark_complete(self, *, passed, message="", summary=None):
        self.status = self.Status.PASSED if passed else self.Status.FAILED
        self.finished_at = timezone.now()
        self.message = message

        if summary is not None:
            self.summary = summary