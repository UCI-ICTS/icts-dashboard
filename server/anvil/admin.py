#!/usr/bin/env python
# anvil/admin.py


from django.contrib import admin

from anvil.models import (
    AnvilUpload,
    AnvilUploadArtifact,
    AnvilUploadTable,
    AnvilUploadValidationRun,
)


class AnvilUploadTableInline(admin.TabularInline):
    model = AnvilUploadTable
    extra = 0
    readonly_fields = (
        "created_at",
        "updated_at",
    )


class AnvilUploadArtifactInline(admin.TabularInline):
    model = AnvilUploadArtifact
    extra = 0
    readonly_fields = (
        "created_at",
        "updated_at",
    )


class AnvilUploadValidationRunInline(admin.TabularInline):
    model = AnvilUploadValidationRun
    extra = 0
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(AnvilUpload)
class AnvilUploadAdmin(admin.ModelAdmin):
    list_display = (
        "upload_id",
        "status",
        "gregor_model_version",
        "needs_review",
        "changed_by",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "gregor_model_version",
        "needs_review",
    )
    search_fields = (
        "upload_id",
        "changed_by__username",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = (
        AnvilUploadTableInline,
        AnvilUploadArtifactInline,
        AnvilUploadValidationRunInline,
    )

@admin.register(AnvilUploadTable)
class AnvilUploadTableAdmin(admin.ModelAdmin):
    list_display = (
        "upload",
        "table_name",
        "generation_status",
        "row_count",
        "needs_review",
        "changed_by",
    )
    list_filter = (
        "generation_status",
        "needs_review",
    )
    search_fields = (
        "upload__upload_id",
        "table_name",
    )


@admin.register(AnvilUploadArtifact)
class AnvilUploadArtifactAdmin(admin.ModelAdmin):
    list_display = (
        "upload",
        "relative_path",
        "artifact_type",
        "generation_status",
        "byte_size",
        "sha256",
    )
    list_filter = (
        "artifact_type",
        "generation_status",
    )
    search_fields = (
        "upload__upload_id",
        "relative_path",
        "sha256",
    )


@admin.register(AnvilUploadValidationRun)
class AnvilUploadValidationRunAdmin(admin.ModelAdmin):
    list_display = (
        "upload",
        "validator_type",
        "validator_version",
        "status",
        "error_count",
        "warning_count",
        "created_at",
    )
    list_filter = (
        "validator_type",
        "status",
    )
    search_fields = (
        "upload__upload_id",
        "validator_version",
        "message",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )