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
    get_anvil_tables,
    get_all_tables,
    get_summary_stats,
    get_family_detail,
    get_case_queue,
)

from search.services import FamilyDetailInputSerializer


class AllTablesAPI(APIView):
    """"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="get_all_tables",
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Search"],
    )
    def get(self, request):
        response_data = []
        try:
            serilized_return_data = get_all_tables()
            return Response(status=status.HTTP_200_OK, data=serilized_return_data)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class SummaryAPI(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_id="summary",
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
        operation_id="case-queue",
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
            print(participant_ids)
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