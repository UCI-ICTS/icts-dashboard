#!/usr/bin/env python
# anvil/services.py

import csv
import datetime
import hashlib
import json
import re
from pathlib import Path
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from config.selectors import (
    TableValidator,
    get_model_schema_path,
    load_table_schema,
    remove_na
)

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


SOURCE_VALIDATOR_VERSION = "dashboard-source-data-v0.4"
PACKAGE_VALIDATOR_VERSION = "dashboard-package-v0.1"

FILE_VALIDATOR_VERSION = "dashboard-file-checks-v0.1"

FILE_CHECK_TABLES = {
    "aligned_dna_short_read": {
        "kind": "alignment",
        "file_field": "aligned_dna_short_read_file",
        "index_field": "aligned_dna_short_read_index_file",
        "experiment_field": "experiment_dna_short_read_id",
    },
    "aligned_rna_short_read": {
        "kind": "alignment",
        "file_field": "aligned_rna_short_read_file",
        "index_field": "aligned_rna_short_read_index_file",
        "experiment_field": "experiment_rna_short_read_id",
    },
    "aligned_nanopore": {
        "kind": "alignment",
        "file_field": "aligned_nanopore_file",
        "index_field": "aligned_nanopore_index_file",
        "experiment_field": "experiment_nanopore_id",
    },
    "aligned_pac_bio": {
        "kind": "alignment",
        "file_field": "aligned_pac_bio_file",
        "index_field": "aligned_pac_bio_index_file",
        "experiment_field": "experiment_pac_bio_id",
    },
    "called_variants_dna_short_read": {
        "kind": "vcf",
        "file_field": "called_variants_dna_file",
        "set_field": "aligned_dna_short_read_set_id",
        "members_field": "aligned_dna_short_read_id",
        "experiment_field": "experiment_dna_short_read_id",
    },
    "called_variants_nanopore": {
        "kind": "vcf",
        "file_field": "called_variants_dna_file",
        "set_field": "aligned_nanopore_set_id",
        "members_field": "aligned_nanopore_id",
        "experiment_field": "experiment_nanopore_id",
    },
    "called_variants_pac_bio": {
        "kind": "vcf",
        "file_field": "called_variants_dna_file",
        "set_field": "aligned_pac_bio_set_id",
        "members_field": "aligned_pac_bio_id",
        "experiment_field": "experiment_pac_bio_id",
    },
}

# Phenotype term_id format per ontology. These mirror the DCC's
# validate_gregor_model check_term_id task (gregor-file-checks), so a term
# rejected here would also be rejected by the AnVIL-side workflow.
# The DCC keeps these regexes in R code, not the data model — so we did the 
# same rather than inventing schema annotations upstream doesn't have. If 
# GREGoR ever adds term patterns to the canonical model, this constant is 
# the one thing to delete. 

PHENOTYPE_TERM_ID_PATTERNS = {
    "HPO": re.compile(r"^HP:[0-9]{7}$"),
    "MONDO": re.compile(r"^MONDO:[0-9]{7}$"),
    "OMIM": re.compile(r"^OMIM:[0-9]{6}$"),
    "ORPHANET": re.compile(r"^ORPHA:[0-9]+$"),
    "SNOMED": re.compile(r"^SCTID:[0-9]+$"),
    "ICD10": re.compile(r"^[A-Z][0-9]{2}([.][0-9]+)?$"),
}


def _collect_term_format_errors(*, row: dict) -> list[dict]:
    """
    Check a phenotype row's term_id format against its declared ontology.

    Unknown ontologies are the schema enum's job; blank values are the
    schema required-ness check's job. This check only asserts that a present
    term_id matches its present ontology's identifier format.
    """

    ontology = row.get("ontology")
    term_id = row.get("term_id")
    pattern = PHENOTYPE_TERM_ID_PATTERNS.get(ontology)

    if not term_id or pattern is None:
        return []

    if pattern.fullmatch(str(term_id)):
        return []

    return [
        {
            "field": "term_id",
            "error": (
                f"'{term_id}' does not match the {ontology} identifier "
                f"format ({pattern.pattern})"
            ),
        }
    ]


@transaction.atomic
def initialize_upload_tables(
    *,
    upload: AnvilUpload,
    tables: list[str] | None = None,
    changed_by: User | None = None,
) -> list[AnvilUploadTable]:
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
def initialize_upload_tsv_artifacts(
    *,
    upload: AnvilUpload,
    upload_tables: list[AnvilUploadTable] | None = None,
    changed_by: User | None = None,
) -> list[AnvilUploadArtifact]:
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
def initialize_upload_package(*,
    upload: AnvilUpload,
    tables: list[str] | None = None,
    changed_by: User| None = None
) -> dict:
    """
    Initialize the database records for a deterministic AnVIL upload package.

    This creates:
    - AnvilUploadTable rows
    - planned table TSV artifact rows
    - upload_manifest.json

    It does not write TSV files.
    """

    # Initialization freezes the model version for this upload. Reject an
    # unavailable version before creating any table or artifact bookkeeping.
    get_model_schema_path(upload.gregor_model_version)

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


def _get_schema_foreign_keys(
    *,
    model_version: str,
    table_names: list[str],
) -> dict[str, list[dict]]:
    """Return the canonical FK edges for the selected table schemas."""

    foreign_keys = {}

    for table_name in table_names:
        schema = load_table_schema(
            model_version=model_version,
            table_name=table_name,
        )
        edges = []

        for column_name, column_schema in schema.get("properties", {}).items():
            reference = column_schema.get("x-references", "")

            if not (isinstance(reference, str) and reference.startswith(">")):
                continue

            referenced_table, separator, referenced_column = (
                reference.lstrip("> ").strip().partition(".")
            )

            if not separator:
                continue

            edges.append(
                {
                    "column": column_name,
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column,
                }
            )

        if edges:
            foreign_keys[table_name] = edges

    return foreign_keys


def _get_foreign_key_values(value) -> list[str]:
    """Normalize one scalar or multi-valued FK column into string values."""

    if value in (None, "", "NA"):
        return []

    if isinstance(value, list):
        return [
            str(item)
            for item in value
            if item not in (None, "", "NA")
        ]

    return [str(value)]


def _collect_foreign_key_errors(
    *,
    included_rows: list[tuple[str, dict]],
    foreign_keys: list[dict],
    included_rows_by_table: dict[str, list[tuple[str, dict]]],
) -> dict[str, list[dict]]:
    """
    Find references that do not resolve among rows included in this upload.

    References to unselected tables are skipped. The DCC can resolve those
    against tables already present in an AnVIL workspace; Dashboard support
    for that behavior requires workspace access and belongs to a later stage.
    """

    errors_by_pk = {}

    for foreign_key in foreign_keys:
        referenced_table = foreign_key["referenced_table"]

        if referenced_table not in included_rows_by_table:
            continue

        valid_values = {
            str(row.get(foreign_key["referenced_column"]))
            for _pk, row in included_rows_by_table[referenced_table]
        }

        for pk, row in included_rows:
            values = _get_foreign_key_values(row.get(foreign_key["column"]))

            for value in values:
                if value in valid_values:
                    continue

                errors_by_pk.setdefault(pk, []).append(
                    {
                        "field": foreign_key["column"],
                        "error": (
                            f"'{value}' not found in "
                            f"{referenced_table}."
                            f"{foreign_key['referenced_column']} among rows "
                            "included in this upload"
                        ),
                    }
                )

    return errors_by_pk


def _get_upload_table_model(*, table_name: str) -> type:
    app_label, model_name = ANVIL_UPLOAD_TABLE_MODEL_MAP[table_name]
    return apps.get_model(app_label, model_name)


def _get_export_fields(model_class: type) -> list:
    """
    First-pass export field selection.

    Uses concrete fields plus many-to-many fields (GREGoR set tables and
    multi-valued columns are M2M on the Django models but schema arrays),
    excluding Dashboard audit/review fields. Later, this can be replaced with
    schema-defined column order from the GREGoR data model.
    """

    fields = []

    for field in list(model_class._meta.fields) + list(model_class._meta.many_to_many):
        if field.name in DASHBOARD_ONLY_EXPORT_FIELDS:
            continue
            
        fields.append(field)

    return fields


def _serialize_tsv_value(value) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        # GREGoR TSV convention: multi-valued fields are pipe-delimited.
        return "|".join(str(item) for item in value)

    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)

    return str(value)


def _rows_from_object(
    *,
    obj,
    fields: list,
    schema: dict,
    serialize_for_tsv: bool = False,
) -> list[dict]:
    """
    Build one or more GREGoR rows from one Django object.

    Uses field.name (not field.column) so ForeignKey fields export as the
    GREGoR schema key ("family_id"), not the database column ("family_id_id").

    Django M2M fields map to two GREGoR representations:
    - schema arrays remain one pipe-delimited TSV value
    - schema scalars (set membership tables) expand to one TSV row per member
    """

    rows = [{}]
    schema_properties = schema.get("properties", {})

    for field in fields:
        column_name = field.name
        value = field.value_from_object(obj)

        if field.many_to_many:
            related_pk_is_auto = field.related_model._meta.pk.auto_created

            value = [
                (
                    str(getattr(item, "name", item.pk))
                    if related_pk_is_auto
                    else str(item.pk)
                )
                for item in value
            ]

            if schema_properties.get(column_name, {}).get("type") != "array":
                values = value or [None]

                rows = [
                    {**row, column_name: item}
                    for row in rows
                    for item in values
                ]
                continue

        elif isinstance(value, (datetime.date, datetime.datetime)):
            value = value.isoformat()

        for row in rows:
            row[column_name] = value

    if serialize_for_tsv:
        return [
            {
                column_name: _serialize_tsv_value(value=value)
                for column_name, value in row.items()
            }
            for row in rows
        ]

    return rows


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _get_package_dir(*, upload: AnvilUpload) -> Path:
    """
    Resolve the durable package directory for one upload.

    Packages live under settings.ANVIL_PACKAGE_ROOT, one directory per
    upload_id. They are permanent upload snapshots and are never auto-deleted.
    This helper is the single path-resolution seam; a future cloud storage
    backend replaces this function, not its callers.
    """

    return Path(settings.ANVIL_PACKAGE_ROOT) / str(upload.upload_id)


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

    # Set-table TSVs intentionally repeat the set_id once per member. The
    # DCC's AnvilDataModels::check_primary_keys skips *_set tables for the
    # same reason.
    if duplicate_primary_keys and not table_name.endswith("_set"):

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


def _get_manifest_selected_tables(*, upload:AnvilUpload)->list[str]:
    """
    Selected tables from the plan manifest; falls back to all upload tables
    if no manifest exists (missing manifest is reported separately).
    """

    manifest_artifact = get_upload_manifest_artifact(upload=upload)

    if manifest_artifact is None or not manifest_artifact.metadata:
        return list(ANVIL_UPLOAD_TABLES)

    return manifest_artifact.metadata.get("tables", {}).get("included", [])


def _validate_table_tsv_artifacts(*, upload):
    errors = []

    selected_tables = _get_manifest_selected_tables(upload=upload)

    expected_relative_paths = {
        f"tables/{table_name}.tsv"
        for table_name in selected_tables
    }

    artifacts = list(
        upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            upload_table__table_name__in=selected_tables,
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
                    "Run initialize first."
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

    selected_tables = _get_manifest_selected_tables(upload=upload)

    manifest_table_names = set(manifest.get("tables", {}).get("included", []))
    expected_table_names = set(selected_tables)

    if manifest_table_names != expected_table_names:
        errors.append(
            _package_error(
                code="manifest_table_names_mismatch",
                expected=sorted(expected_table_names),
                observed=sorted(manifest_table_names),
                message="Manifest table names do not match selected upload tables.",
            )
        )

    db_tables_by_name = {
        upload_table.table_name: upload_table
        for upload_table in upload.upload_tables.filter(
            table_name__in=selected_tables,
        )
    }

    manifest_artifacts_by_path = {}

    for artifact_entry in manifest.get("artifacts", {}).get("table_tsvs", []):
        manifest_artifacts_by_path[artifact_entry.get("relative_path")] = artifact_entry

        table_name = artifact_entry.get("table_name")
        upload_table = db_tables_by_name.get(table_name)

        if upload_table is None:
            continue

        if artifact_entry.get("row_count") != upload_table.row_count:
            errors.append(
                _package_error(
                    code="manifest_table_row_count_mismatch",
                    table=table_name,
                    expected=upload_table.row_count,
                    observed=artifact_entry.get("row_count"),
                    message=(
                        "Manifest table row_count does not match "
                        "AnvilUploadTable.row_count."
                    ),
                )
            )

        if artifact_entry.get("column_names") != upload_table.column_names:
            errors.append(
                _package_error(
                    code="manifest_table_column_names_mismatch",
                    table=table_name,
                    expected=upload_table.column_names,
                    observed=artifact_entry.get("column_names"),
                    message=(
                        "Manifest table column_names do not match "
                        "AnvilUploadTable.column_names."
                    ),
                )
            )

    db_tsv_artifacts = upload.artifacts.filter(
        artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
        upload_table__table_name__in=selected_tables,
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


def _get_selected_upload_tables(*, tables:list[str]|None=None)->list[str]:
    if tables is None:
        return list(ANVIL_UPLOAD_TABLES)

    selected_tables = list(dict.fromkeys(tables))
    invalid_tables = sorted(set(selected_tables) - set(ANVIL_UPLOAD_TABLES))

    if invalid_tables:
        raise ValueError(f"Invalid AnVIL upload tables: {invalid_tables}")

    return selected_tables


def _json_safe_datetime(value)->str|None:
    if value is None:
        return None

    return value.isoformat()


def _get_selected_tsv_artifacts(
    *,
    upload: AnvilUpload,
    selected_tables: list[str],
) -> list[AnvilUploadArtifact]:
    """
    Return generated TABLE_TSV artifacts for the selected tables, raising if
    any are missing or lack generated file metadata.
    """

    artifacts = list(
        upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.TABLE_TSV,
            upload_table__table_name__in=selected_tables,
        )
        .select_related("upload_table")
        .order_by("relative_path")
    )

    not_generated = [
        artifact.relative_path
        for artifact in artifacts
        if (
            not artifact.storage_uri
            or not artifact.sha256
            or artifact.byte_size is None
        )
    ]

    if len(artifacts) != len(selected_tables) or not_generated:
        raise ValueError(
            f"Expected {len(selected_tables)} generated TSV artifacts, found "
            f"{len(artifacts)} with {len(not_generated)} missing file metadata. "
            "Run generate_upload_tsvs first."
        )

    return artifacts


MANIFEST_VERSION = "dashboard-anvil-upload-manifest-v0.2"

# Pipeline stages recorded in manifest["validation"]. Ordering defines the
# derived upload status: any failed stage fails the upload; the upload is
# ready for review only when every present stage has passed.
MANIFEST_VALIDATION_STAGES = ["source", "files", "package"]


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
        "manifest_version": MANIFEST_VERSION,
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
            "files": None,
            "package": None,
        },
        "artifacts": {
            "table_tsvs": [],
            "manifest": {"relative_path": "manifest.json"},
        },
    }


def _record_stage_result(
    *,
    manifest: dict,
    stage: str,
    passed: bool,
    validator: str,
    run_id: int,
    error_count: int,
    warning_count: int = 0,
    extra: dict | None = None,
) -> None:
    """
    Record one pipeline stage's latest result in manifest["validation"].

    Stages only ever write their own key; the validation dict itself is never
    rebuilt, so results from other stages survive reruns of any single stage.
    """

    entry = {
        "status": "passed" if passed else "failed",
        "validator": validator,
        "run_id": run_id,
        "error_count": error_count,
        "warning_count": warning_count,
        "completed_at": timezone.now().isoformat(),
    }

    if extra:
        entry.update(extra)

    manifest.setdefault(
        "validation",
        {stage_name: None for stage_name in MANIFEST_VALIDATION_STAGES},
    )
    manifest["validation"][stage] = entry
    manifest["manifest_state"] = (
        f"{stage}_validated" if passed else f"{stage}_validation_failed"
    )


def derive_upload_status(*, manifest: dict) -> str:
    """
    Derive the upload lifecycle status from the latest result of every
    pipeline stage, instead of letting the last stage to run clobber it.
    """

    stage_results = [
        manifest.get("validation", {}).get(stage)
        for stage in MANIFEST_VALIDATION_STAGES
    ]
    completed = [entry for entry in stage_results if entry is not None]

    if any(entry["status"] == "failed" for entry in completed):
        return AnvilUpload.Status.VALIDATION_FAILED

    if completed:
        return AnvilUpload.Status.READY_FOR_REVIEW

    return AnvilUpload.Status.DRAFT


def _apply_derived_upload_status(*, upload, manifest, changed_by=None) -> None:
    upload.status = derive_upload_status(manifest=manifest)

    if changed_by is not None:
        upload.changed_by = changed_by

    upload.save()


def _sync_manifest_to_disk(*, upload, artifact) -> Path:
    """
    Serialize the manifest artifact's metadata to <package>/manifest.json.

    Every stage that mutates the manifest calls this last, so the on-disk
    file always matches the database record and there is no separate
    "generate manifest" step to forget.
    """

    package_dir = _get_package_dir(upload=upload)
    package_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = package_dir / "manifest.json"

    with manifest_path.open("w", encoding="utf-8") as file_handle:
        json.dump(artifact.metadata, file_handle, indent=2, sort_keys=True)
        file_handle.write("\n")

    artifact.byte_size = manifest_path.stat().st_size
    artifact.sha256 = _sha256_file(manifest_path)
    artifact.storage_uri = str(manifest_path)

    return manifest_path


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
def validate_upload_package(
    *,
    upload: AnvilUpload,
    changed_by: User | None = None
) -> AnvilUploadValidationRun:
    """
    Validate generated package files and metadata for one upload.

    This is the Dashboard package-integrity validator. It assumes TSV generation
    and manifest generation have already run.
    """

    validation_run = AnvilUploadValidationRun.objects.create(
        upload=upload,
        validator_type=AnvilUploadValidationRun.ValidatorType.DASHBOARD,
        validator_version=PACKAGE_VALIDATOR_VERSION,
        changed_by=changed_by,
    )

    validation_run.mark_running()
    validation_run.save()

    errors = collect_upload_package_validation_errors(upload=upload)
    passed = len(errors) == 0

    summary = {
        "validator": PACKAGE_VALIDATOR_VERSION,
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

    manifest_artifact = get_upload_manifest_artifact(upload=upload)

    if manifest_artifact is not None:
        manifest = manifest_artifact.metadata or {}

        _record_stage_result(
            manifest=manifest,
            stage="package",
            passed=passed,
            validator=PACKAGE_VALIDATOR_VERSION,
            run_id=validation_run.id,
            error_count=len(errors),
        )

        manifest_artifact.metadata = manifest

        if changed_by is not None:
            manifest_artifact.changed_by = changed_by

        _sync_manifest_to_disk(upload=upload, artifact=manifest_artifact)
        manifest_artifact.save()

        _apply_derived_upload_status(
            upload=upload,
            manifest=manifest,
            changed_by=changed_by,
        )

    return validation_run


@transaction.atomic
def validate_upload_source_data(
    *,
    upload: AnvilUpload,
    changed_by: User | None = None
) -> AnvilUploadValidationRun:
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
        validator_version=SOURCE_VALIDATOR_VERSION,
        changed_by=changed_by,
    )

    validation_run.mark_running()
    validation_run.save()

    table_results = {}
    table_summaries = {}
    source_row_counts = {}
    included_rows_by_table = {}
    excluded_rows_by_table = {}
    error_count = 0
    warning_count = 0

    foreign_keys_by_table = _get_schema_foreign_keys(
        model_version=upload.gregor_model_version,
        table_names=selected_tables,
    )

    # Pass 1: validate each row against its versioned JSON schema. Passing
    # rows become candidates for cross-table reference validation.
    for table_name in selected_tables:
        model_class = _get_upload_table_model(table_name=table_name)
        fields = _get_export_fields(model_class=model_class)
        schema = load_table_schema(
            model_version=upload.gregor_model_version,
            table_name=table_name,
        )
        queryset = model_class.objects.all().order_by(model_class._meta.pk.name)

        source_row_counts[table_name] = queryset.count()
        included_rows = []
        excluded_rows = []

        for obj in queryset:
            object_rows = _rows_from_object(
                obj=obj,
                fields=fields,
                schema=schema,
            )
            row_errors = []

            for row in object_rows:
                validator = TableValidator(
                    model_version=upload.gregor_model_version
                )
                validator.validate_json(remove_na(row), table_name)
                validation_results = validator.get_validation_results()

                if not validation_results["valid"]:
                    row_errors.extend(validation_results["errors"])
                if table_name == "phenotype":
                    row_errors.extend(_collect_term_format_errors(row=row))

            if row_errors:
                excluded_rows.append(
                    {
                        "pk": str(obj.pk),
                        "reason": "schema validation failed",
                        "errors": row_errors,
                    }
                )
            else:
                included_rows.extend(
                    (str(obj.pk), row)
                    for row in object_rows
                )

        included_rows_by_table[table_name] = included_rows
        excluded_rows_by_table[table_name] = excluded_rows

    # Pass 2: resolve FKs against rows that remain included after schema
    # validation. Canonical table order is parent-first, so exclusions cascade
    # from family -> participant -> phenotype and through experiment chains.
    foreign_key_order = [
        table_name
        for table_name in ANVIL_UPLOAD_TABLES
        if table_name in selected_tables
    ]

    for table_name in foreign_key_order:
        foreign_key_errors = _collect_foreign_key_errors(
            included_rows=included_rows_by_table[table_name],
            foreign_keys=foreign_keys_by_table.get(table_name, []),
            included_rows_by_table=included_rows_by_table,
        )

        failed_pks = set(foreign_key_errors)

        remaining_rows = [
            (pk, row)
            for pk, row in included_rows_by_table[table_name]
            if pk not in failed_pks
        ]

        for pk, errors in foreign_key_errors.items():
            excluded_rows_by_table[table_name].append(
                {
                    "pk": pk,
                    "reason": "foreign key validation failed",
                    "errors": errors,
                }
            )

        included_rows_by_table[table_name] = remaining_rows

    # Persist the combined schema and FK decisions.
    for table_name in selected_tables:
        source_row_count = source_row_counts[table_name]
        excluded_rows = excluded_rows_by_table[table_name]
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

        # The manifest is summary-first: full per-row detail only appears for
        # failures. Clean tables stay as counts.
        table_results[table_name] = {
            "selected": True,
            **table_summary,
            "excluded_rows": excluded_rows,
        }

        table_summaries[table_name] = table_summary

        upload_table = upload.upload_tables.filter(
            table_name=table_name
        ).first()

        if upload_table is not None:
            upload_table.source_summary = table_summary

            if changed_by is not None:
                upload_table.changed_by = changed_by

            upload_table.save()

        error_count += table_error_count

    passed = error_count == 0

    summary = {
        "validator": SOURCE_VALIDATOR_VERSION,
        "passed": passed,
        "error_count": error_count,
        "warning_count": warning_count,
        "tables": table_summaries,
    }

    manifest.setdefault("tables", {})
    manifest["tables"]["by_name"] = table_results

    _record_stage_result(
        manifest=manifest,
        stage="source",
        passed=passed,
        validator=SOURCE_VALIDATOR_VERSION,
        run_id=validation_run.id,
        error_count=error_count,
        warning_count=warning_count,
    )

    # Rerunning source validation supersedes any downstream results: the
    # included-row plan they were computed from may have changed.
    manifest["validation"]["files"] = None
    manifest["validation"]["package"] = None

    manifest_artifact.metadata = manifest
    manifest_artifact.generation_status = (
        AnvilUploadArtifact.GenerationStatus.GENERATED
        if passed
        else AnvilUploadArtifact.GenerationStatus.FAILED
    )

    if changed_by is not None:
        manifest_artifact.changed_by = changed_by

    _sync_manifest_to_disk(upload=upload, artifact=manifest_artifact)
    manifest_artifact.save()

    validation_run.error_count = error_count
    validation_run.warning_count = warning_count
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

    _apply_derived_upload_status(
        upload=upload,
        manifest=manifest,
        changed_by=changed_by,
    )

    return validation_run


@transaction.atomic
def generate_upload_tsvs(
    *,
    upload: AnvilUpload,
    changed_by: User | None = None
) -> dict:
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

    if manifest_artifact is None:
        raise ValueError("Upload manifest does not exist. Run initialize first.")

    manifest = manifest_artifact.metadata or {}
    selected_tables = manifest.get("tables", {}).get("included", [])

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

    package_dir = _get_package_dir(upload=upload)
    tables_dir = package_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    tables_by_name = manifest.get("tables", {}).get("by_name", {})

    generated = []

    for table_name in selected_tables:
        model_class = _get_upload_table_model(table_name=table_name)
        fields = _get_export_fields(model_class)

        schema = load_table_schema(
            model_version=upload.gregor_model_version,
            table_name=table_name,
        )

        column_names = [field.name for field in fields]

        queryset = model_class.objects.all().order_by(model_class._meta.pk.name)

        excluded_pks = {
            excluded_row["pk"]
            for excluded_row in tables_by_name.get(table_name, {}).get("excluded_rows", [])
        }

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
                if str(obj.pk) in excluded_pks:
                    continue

                rows = _rows_from_object(
                    obj=obj,
                    fields=fields,
                    schema=schema,
                    serialize_for_tsv=True,
                )

                writer.writerows(rows)
                row_count += len(rows)

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
        artifact.generation_status = AnvilUploadArtifact.GenerationStatus.GENERATED

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

    # Embed the artifact catalog in the manifest and write it to disk here:
    # the manifest describes the files this stage just produced, so there is
    # no separate "generate manifest" step.
    manifest.setdefault("artifacts", {})
    manifest["artifacts"]["table_tsvs"] = [
        {
            "table_name": entry["table_name"],
            "relative_path": entry["relative_path"],
            "file_name": f"{entry['table_name']}.tsv",
            "content_type": TSV_CONTENT_TYPE,
            "byte_size": entry["byte_size"],
            "sha256": entry["sha256"],
            "storage_uri": entry["file_path"],
            "row_count": entry["row_count"],
            "column_names": entry["column_names"],
        }
        for entry in generated
    ]
    manifest["artifacts"]["manifest"] = {"relative_path": "manifest.json"}
    manifest["generated_at"] = timezone.now().isoformat()
    manifest["manifest_state"] = "package_generated"

    # Regenerated TSVs invalidate any prior file/package validation results.
    manifest.setdefault("validation", {})
    manifest["validation"]["files"] = None
    manifest["validation"]["package"] = None

    manifest_artifact.metadata = manifest
    manifest_artifact.generation_status = (
        AnvilUploadArtifact.GenerationStatus.GENERATED
    )

    if changed_by is not None:
        manifest_artifact.changed_by = changed_by

    manifest_path = _sync_manifest_to_disk(
        upload=upload,
        artifact=manifest_artifact,
    )
    manifest_artifact.save()

    return {
        "upload": upload,
        "package_dir": str(package_dir),
        "tables_dir": str(tables_dir),
        "manifest": manifest,
        "manifest_path": str(manifest_path),
        "generated": generated,
    }


def initialize_upload_manifest_artifact(
    *,
    upload:AnvilUpload,
    selected_tables: list[str],
    changed_by: User | None = None
)-> AnvilUploadArtifact:
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

    _sync_manifest_to_disk(upload=upload, artifact=artifact)
    artifact.save()

    return artifact


def get_upload_manifest_artifact(upload: AnvilUpload) -> AnvilUploadArtifact | None:
    return (
        upload.artifacts.filter(
            artifact_type=AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST,
            relative_path="manifest.json",
        )
        .order_by("-updated_at", "-created_at")
        .first()
    )

def _expected_file_samples(*, obj, config: dict) -> list[str]:
    if config["kind"] == "alignment":
        experiment = getattr(obj, config["experiment_field"])
        return [experiment.experiment_sample_id]

    aligned_set = getattr(obj, config["set_field"])
    samples = []
    for aligned in getattr(aligned_set, config["members_field"]).all():
        experiment = getattr(aligned, config["experiment_field"])
        sample = experiment.experiment_sample_id
        if sample not in samples:
            samples.append(sample)
    return samples


@transaction.atomic
def validate_upload_files(
    *,
    upload: AnvilUpload,
    changed_by: User | None = None,
    provider=None,
) -> AnvilUploadValidationRun:
    from anvil.file_checks import (
        FAIL,
        UNVERIFIED,
        LocalFileProvider,
        check_alignment_samples,
        check_file_md5,
        check_index_uri,
        check_vcf_sample_set,
    )

    manifest_artifact = get_upload_manifest_artifact(upload=upload)
    if manifest_artifact is None:
        raise ValueError("Upload manifest does not exist. Run initialize first.")

    if provider is None:
        provider = LocalFileProvider(root=settings.ANVIL_FILE_STAGING_ROOT)

    manifest = manifest_artifact.metadata or {}
    selected_tables = manifest.get("tables", {}).get("included", [])
    table_plans = manifest.get("tables", {}).get("by_name", {})
    excluded = {
        table: {row["pk"] for row in plan.get("excluded_rows", [])}
        for table, plan in table_plans.items()
    }

    run = AnvilUploadValidationRun.objects.create(
        upload=upload,
        validator_type=AnvilUploadValidationRun.ValidatorType.LOCAL,
        validator_version=FILE_VALIDATOR_VERSION,
        changed_by=changed_by,
    )
    run.mark_running()
    run.save()

    error_count = 0
    warning_count = 0
    table_results = {}

    for table_name in selected_tables:
        config = FILE_CHECK_TABLES.get(table_name)
        if config is None:
            continue

        model = _get_upload_table_model(table_name=table_name)
        results = []
        for obj in model.objects.all().order_by(model._meta.pk.name):
            if str(obj.pk) in excluded.get(table_name, set()):
                continue

            file_uri = getattr(obj, config["file_field"]) or ""
            local_path = provider.materialize(uri=file_uri)
            checks = []

            index_field = config.get("index_field")
            if index_field:
                index_check = check_index_uri(
                    file_uri=file_uri,
                    index_uri=getattr(obj, index_field) or "",
                )
                if index_check:
                    checks.append(index_check)

            checks.append(
                check_file_md5(
                    local_path=local_path,
                    declared_md5=obj.md5sum or "",
                )
            )
            expected_samples = _expected_file_samples(obj=obj, config=config)
            if config["kind"] == "alignment":
                checks.append(
                    check_alignment_samples(
                        local_path=local_path,
                        expected_samples=expected_samples,
                    )
                )
            else:
                checks.append(
                    check_vcf_sample_set(
                        local_path=local_path,
                        expected_samples=expected_samples,
                    )
                )

            statuses = {check["status"] for check in checks}
            row_status = (
                FAIL if FAIL in statuses
                else UNVERIFIED if UNVERIFIED in statuses
                else "PASS"
            )
            if row_status == FAIL:
                error_count += 1
            elif row_status == UNVERIFIED:
                warning_count += 1

            results.append(
                {
                    "pk": str(obj.pk),
                    "file_uri": file_uri,
                    "status": row_status,
                    "checks": checks,
                }
            )

        table_results[table_name] = {
            "checked_row_count": len(results),
            "passed_row_count": sum(r["status"] == "PASS" for r in results),
            "failed_row_count": sum(r["status"] == FAIL for r in results),
            "unverified_row_count": sum(
                r["status"] == UNVERIFIED for r in results
            ),
            "rows": results,
        }

    passed = error_count == 0
    summary = {
        "validator": FILE_VALIDATOR_VERSION,
        "provider": provider.name,
        "passed": passed,
        "error_count": error_count,
        "warning_count": warning_count,
        "tables": table_results,
    }

    # Per-table file results in the manifest: summary counts always, full
    # per-row detail only for non-passing rows. The complete row-level record
    # (including passes) lives in the validation run's summary.
    for table_name, result in table_results.items():
        table_entry = manifest.setdefault("tables", {}).setdefault(
            "by_name", {}
        ).setdefault(table_name, {"selected": True})

        table_entry["files"] = {
            "checked_row_count": result["checked_row_count"],
            "passed_row_count": result["passed_row_count"],
            "failed_row_count": result["failed_row_count"],
            "unverified_row_count": result["unverified_row_count"],
        }
        table_entry["file_check_failures"] = [
            {
                "pk": row["pk"],
                "file_uri": row["file_uri"],
                "status": row["status"],
                "checks": [
                    check
                    for check in row["checks"]
                    if check["status"] != "PASS"
                ],
            }
            for row in result["rows"]
            if row["status"] != "PASS"
        ]

    _record_stage_result(
        manifest=manifest,
        stage="files",
        passed=passed,
        validator=FILE_VALIDATOR_VERSION,
        run_id=run.id,
        error_count=error_count,
        warning_count=warning_count,
        extra={"provider": provider.name},
    )

    manifest_artifact.metadata = manifest
    if changed_by is not None:
        manifest_artifact.changed_by = changed_by
    _sync_manifest_to_disk(upload=upload, artifact=manifest_artifact)
    manifest_artifact.save()

    run.error_count = error_count
    run.warning_count = warning_count
    run.mark_complete(
        passed=passed,
        message=(
            "Pre-flight file validation passed."
            if passed
            else "Pre-flight file validation failed."
        ),
        summary=summary,
    )
    run.save()

    _apply_derived_upload_status(
        upload=upload,
        manifest=manifest,
        changed_by=changed_by,
    )

    return run
