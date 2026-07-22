#!/usr/bin/env python
# anvil/apis.py

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from anvil.models import AnvilUpload
from anvil.serializers import (
    AnvilUploadCreateSerializer,
    AnvilUploadDetailSerializer,
    AnvilUploadListSerializer,
)
from anvil.services import (
    generate_upload_manifest,
    generate_upload_tsvs,
    initialize_upload_package,
    validate_upload_package,
    validate_upload_source_data,
)


class AnvilUploadViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        AnvilUpload.objects.all()
        .prefetch_related(
            "upload_tables",
            "artifacts",
            "validation_runs",
        )
        .order_by("-created_at")
    )
    lookup_field = "upload_id"

    def get_serializer_class(self):
        if self.action == "create":
            return AnvilUploadCreateSerializer

        if self.action == "list":
            return AnvilUploadListSerializer

        return AnvilUploadDetailSerializer

    def perform_create(self, serializer):
        serializer.save(changed_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="initialize")
    def initialize_package(self, request, upload_id=None):
        upload = self.get_object()

        initialize_upload_package(
            upload=upload,
            changed_by=request.user,
        )

        serializer = self.get_serializer(upload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="validate-source")
    def validate_source(self, request, upload_id=None):
        upload = self.get_object()

        validation_run = validate_upload_source_data(
            upload=upload,
            changed_by=request.user,
        )

        upload.refresh_from_db()
        serializer = self.get_serializer(upload)

        return Response(
            {
                "upload": serializer.data,
                "validation_run_id": validation_run.pk,
                "passed": validation_run.status == validation_run.Status.PASSED,
                "error_count": validation_run.error_count,
                "summary": validation_run.summary,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="generate-tsvs")
    def generate_tsvs(self, request, upload_id=None):
        upload = self.get_object()

        output_dir = request.data.get("output_dir", "/tmp/anvil_uploads")

        result = generate_upload_tsvs(
            upload=upload,
            output_dir=output_dir,
            changed_by=request.user,
        )

        upload.refresh_from_db()
        serializer = self.get_serializer(upload)

        return Response(
            {
                "upload": serializer.data,
                "package_dir": result["package_dir"],
                "tables_dir": result["tables_dir"],
                "generated_count": len(result["generated"]),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="generate-manifest")
    def generate_manifest(self, request, upload_id=None):
        upload = self.get_object()

        output_dir = request.data.get("output_dir", "/tmp/anvil_uploads")

        result = generate_upload_manifest(
            upload=upload,
            output_dir=output_dir,
            changed_by=request.user,
        )

        upload.refresh_from_db()
        serializer = self.get_serializer(upload)

        return Response(
            {
                "upload": serializer.data,
                "manifest_path": result["manifest_path"],
                "artifact_id": result["artifact"].pk,
                "summary": result["manifest"]["summary"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="validate-package")
    def validate_package(self, request, upload_id=None):
        upload = self.get_object()

        validation_run = validate_upload_package(
            upload=upload,
            changed_by=request.user,
        )

        upload.refresh_from_db()
        serializer = self.get_serializer(upload)

        return Response(
            {
                "upload": serializer.data,
                "validation_run_id": validation_run.pk,
                "passed": validation_run.status == validation_run.Status.PASSED,
                "error_count": validation_run.error_count,
                "summary": validation_run.summary,
            },
            status=status.HTTP_200_OK,
        )

    