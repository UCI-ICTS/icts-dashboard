#!/usr/bin/env python
# anvil/serializers.py

from rest_framework import serializers

from anvil.constants import ANVIL_UPLOAD_TABLES
from anvil.models import (
    AnvilUpload,
    AnvilUploadArtifact,
    AnvilUploadTable,
    AnvilUploadValidationRun,
)


class AnvilUploadTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnvilUploadTable
        fields = [
            "id",
            "table_name",
            "generation_status",
            "row_count",
            "column_names",
            "source_summary",
            "generation_error",
            "created_at",
            "updated_at",
        ]


class AnvilUploadArtifactSerializer(serializers.ModelSerializer):
    upload_table = serializers.SlugRelatedField(
        slug_field="table_name",
        read_only=True,
    )

    class Meta:
        model = AnvilUploadArtifact
        fields = [
            "id",
            "upload_table",
            "artifact_type",
            "generation_status",
            "relative_path",
            "file_name",
            "content_type",
            "byte_size",
            "sha256",
            "storage_uri",
            "metadata",
            "generation_error",
            "created_at",
            "updated_at",
        ]


class AnvilUploadValidationRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnvilUploadValidationRun
        fields = [
            "id",
            "validator_type",
            "validator_version",
            "status",
            "started_at",
            "finished_at",
            "error_count",
            "warning_count",
            "message",
            "summary",
            "created_at",
            "updated_at",
        ]


class AnvilUploadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnvilUpload
        fields = [
            "upload_id",
            "gregor_model_version",
            "notes",
        ]


class AnvilUploadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnvilUpload
        fields = [
            "upload_id",
            "status",
            "gregor_model_version",
            "notes",
            "created_at",
            "updated_at",
        ]


class AnvilUploadDetailSerializer(serializers.ModelSerializer):
    upload_tables = AnvilUploadTableSerializer(many=True, read_only=True)
    artifacts = AnvilUploadArtifactSerializer(many=True, read_only=True)
    validation_runs = AnvilUploadValidationRunSerializer(many=True, read_only=True)
    manifest = serializers.SerializerMethodField()

    class Meta:
        model = AnvilUpload
        fields = [
            "upload_id",
            "status",
            "gregor_model_version",
            "notes",
            "created_at",
            "updated_at",
            "manifest",
            "upload_tables",
            "artifacts",
            "validation_runs",
        ]

    def get_manifest(self, upload):
        """
        The manifest document is the single source of truth for pipeline
        state; the UI renders stage status and failure detail directly
        from it.
        """

        manifest_artifact = next(
            (
                artifact
                for artifact in upload.artifacts.all()
                if artifact.artifact_type
                == AnvilUploadArtifact.ArtifactType.UPLOAD_MANIFEST
                and artifact.relative_path == "manifest.json"
            ),
            None,
        )

        if manifest_artifact is None:
            return None

        return manifest_artifact.metadata or None

class AnvilUploadInitializeSerializer(serializers.Serializer):
    tables = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[(table_name, table_name) for table_name in ANVIL_UPLOAD_TABLES]
        ),
        required=False,
        allow_empty=False,
        help_text=(
            "Optional list of GREGoR tables to include in this upload. "
            "If omitted, all standard AnVIL upload tables are included."
        ),
    )
