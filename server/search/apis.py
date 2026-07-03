#!/usr/bin/env python
# search/apis.py

from collections import Counter, defaultdict
from django.apps import apps
from django.db.models import Q, Count
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from itertools import chain, groupby
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from search.selectors import (
    get_all_tables,
    get_summary_stats,
    get_family_detail,
    get_case_queue,
)

from search.services import FamilyDetailInputSerializer


class AllTablesZipAPI(APIView):
    """
    Download all registered GREGoR data tables as a ZIP archive.

    The ZIP archive contains one JSON file per table and a manifest file
    describing the exported files.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="download_all_tables_zip",
        operation_summary="Download all tables as ZIP",
        operation_description=(
            "Builds and returns a ZIP archive containing one JSON file per "
            "registered GREGoR data table, plus a manifest.json file."
        ),
        produces=["application/zip"],
        responses={
            200: openapi.Response(
                description="ZIP archive containing exported table JSON files.",
                schema=openapi.Schema(type=openapi.TYPE_FILE),
            ),
            400: openapi.Response(description="Failed to build ZIP archive."),
            401: openapi.Response(description="Authentication required."),
        },
        tags=["Search"],
    )
    def get(self, request):
        try:
            zip_buffer = get_all_tables()

            response = HttpResponse(
                zip_buffer.getvalue(),
                content_type="application/zip",
            )
            response["Content-Disposition"] = (
                'attachment; filename="gregor_all_tables.zip"'
            )
            return response

        except Exception as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SummaryAPI(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_id="summary",
        operation_summary="Summary statistics",
        operation_description=(
            "Builds and returns aggregate summary statistics for the project. "
            "The response includes high-level entity counts, solve status counts, "
            "biobank and analyte summaries, sequencing versus alignment counts, "
            "family type summaries, experiment category counts, pediatric proband "
            "counts, long-read family summaries, reported race summaries, and "
            "ontology term frequencies."
        ),
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Search"],
    )

    def get(self, request):
        try:
            response = get_summary_stats()

            return Response(status=status.HTTP_200_OK, data=response)

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FamilyDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of `participant_id`s ",
                type=openapi.TYPE_STRING,
            )
        ],
        operation_id="get_family_detail",
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Search"],
    )
    def get(self, request):
        response = []
        superuser = self.request.user.is_superuser
        try:
            participant_ids = request.GET.get("ids", "").split(",")
            for participant_id in participant_ids:
                response.append(get_family_detail(participant_id, superuser))

            return Response(status=status.HTTP_200_OK, data=response)

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CaseQueue(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of `participant_id`s ",
                type=openapi.TYPE_STRING,
            )
        ],
        operation_id="case_queue",
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Search"],
    )
    def get(self, request):
        response = []
        try:
            participant_ids = request.GET.get("ids", "").split(",")
            for participant_id in participant_ids:
                response.append(get_case_queue(participant_id))

            return Response(status=status.HTTP_200_OK, data=response)

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )


## DEACTIVATED APIs
class DownloadTablesAPI(APIView):
    """AnVIL upload table generation."""

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_id="get_anvil_tables",
        responses={
            200: "Submission successfull",
            400: "Bad request",
        },
        tags=["Search"],
    )
    def get(self, request):
        zip_buffer = get_anvil_tables()

        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="data.zip"'

        return response


class SearchTablesAPI(APIView):
    """"""

    permission_classes = [AllowAny]
    model_name_param = openapi.Parameter(
        "model_name",
        openapi.IN_PATH,
        description="Name of the model to query",
        type=openapi.TYPE_STRING,
    )
    slow_client_param = openapi.Parameter(
        "slowClient",
        openapi.IN_QUERY,
        description="Flag to indicate slow client handling",
        type=openapi.TYPE_BOOLEAN,
        required=False,
    )

    @swagger_auto_schema(
        manual_parameters=[model_name_param, slow_client_param],
        responses={200: "JSON response of model data"},
        auto_schema=None,
    )
    def get(self, request, model_name):
        try:
            model = apps.get_model("metadata", model_name)
        except LookupError:
            return Response(
                {"error": "Model not found."}, status=status.HTTP_404_NOT_FOUND
            )

        query_params = request.query_params
        filter_kwargs = {k: v for k, v in query_params.items() if hasattr(model, k)}

        queryset = model.objects.filter(**filter_kwargs)
        data = chain(queryset.values())

        return Response(data)