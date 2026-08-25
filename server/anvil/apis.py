#!/usr/bin/env python
# anvil/apis.py

from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.selectors import ModelVersionError

from anvil.models import AnvilUpload
from anvil.serializers import (
    AnvilUploadCreateSerializer,
    AnvilUploadDetailSerializer,
    AnvilUploadListSerializer,
    AnvilUploadInitializeSerializer,
)
from anvil.services import (
    generate_upload_tsvs,
    initialize_upload_package,
    validate_upload_files,
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
    permission_classes = [AllowAny]

    def _changed_by(self) -> User | None:
        """changed_by FKs require a User instance; map AnonymousUser to None."""
        user = self.request.user
        return user if user.is_authenticated else None

    def get_serializer_class(self):
        if self.action == "create":
            return AnvilUploadCreateSerializer

        if self.action == "list":
            return AnvilUploadListSerializer

        return AnvilUploadDetailSerializer

    def perform_create(self, serializer):
        serializer.save(changed_by=self._changed_by())

    @swagger_auto_schema(
        request_body=AnvilUploadInitializeSerializer,
        responses={200: AnvilUploadDetailSerializer},
        operation_description=(
            "Initialize an AnVIL upload package. Optionally accepts a list of "
            "GREGoR table names to include. If no tables are provided, all "
            "standard upload tables are included."
        ),
        tags=["AnVIL Uploads"],
    )
    @action(detail=True, methods=["post"], url_path="initialize")
    def initialize_package(self, request, upload_id=None):
        upload = self.get_object()

        input_serializer = AnvilUploadInitializeSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        tables = input_serializer.validated_data.get("tables")
        try:
            initialize_upload_package(
                upload=upload,
                tables=tables,
                changed_by=self._changed_by(),
            )
        except ModelVersionError as error:
            raise ValidationError(
                {"gregor_model_version": str(error)}
            ) from error

        upload = (
            self.get_queryset()
            .get(upload_id=upload.upload_id)
        )

        serializer = AnvilUploadDetailSerializer(
            upload,
            context={"request": request},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="validate-source")
    def validate_source(self, request, upload_id=None):
        upload = self.get_object()

        validation_run = validate_upload_source_data(
            upload=upload,
            changed_by=self._changed_by(),
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

        result = generate_upload_tsvs(
            upload=upload,
            changed_by=self._changed_by(),
        )

        upload.refresh_from_db()
        serializer = self.get_serializer(upload)

        manifest = result["manifest"]

        return Response(
            {
                "upload": serializer.data,
                "package_dir": result["package_dir"],
                "tables_dir": result["tables_dir"],
                "manifest_path": result["manifest_path"],
                "manifest_state": manifest.get("manifest_state"),
                "generated_count": len(result["generated"]),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="validate-files")
    def validate_files(self, request, upload_id=None):
        upload = self.get_object()
        validation_run = validate_upload_files(
            upload=upload,
            changed_by=self._changed_by(),
        )
        upload.refresh_from_db()

        return Response(
            {
                "upload": self.get_serializer(upload).data,
                "validation_run_id": validation_run.pk,
                "passed": validation_run.status == validation_run.Status.PASSED,
                "error_count": validation_run.error_count,
                "warning_count": validation_run.warning_count,
                "summary": validation_run.summary,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="validate-package")
    def validate_package(self, request, upload_id=None):
        upload = self.get_object()

        validation_run = validate_upload_package(
            upload=upload,
            changed_by=self._changed_by(),
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

    