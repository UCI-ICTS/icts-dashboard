#!/usr/bin/env python
# geneyx/apis.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from geneyx.services import (
    fetch_vcf_samples,
    fetch_vcf_sample,
    fetch_cases,
    fetch_case,
    fetch_case_notes,
)


class GetAllVCFSamples(APIView):
    """"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="get_all_vcf_samples",
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Geneyx"]
    )

    def get(self, request):
        try:
            vcf_samples = fetch_vcf_samples()
            return Response(status=status.HTTP_200_OK, data=vcf_samples)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetVCFSample(APIView):
    """"""
    permission_classes = [AllowAny]

    participant_id = openapi.Parameter(
        "participant_id",
        openapi.IN_QUERY,
        description="participant_id",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        operation_id="get_vcf_sample",
        manual_parameters=[participant_id],
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Geneyx"]
    )

    def get(self, request):
        try:
            participant_id = request.query_params["participant_id"]
            vcf_sample = fetch_vcf_sample(participant_id)
            return Response(status=status.HTTP_200_OK, data=vcf_sample)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetAllCases(APIView):
    """"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="get_all_cases",
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Geneyx"]
    )

    def get(self, request):
        try:
            cases = fetch_cases()
            return Response(status=status.HTTP_200_OK, data=cases)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetCase(APIView):
    """"""
    permission_classes = [AllowAny]

    participant_id = openapi.Parameter(
        "participant_id",
        openapi.IN_QUERY,
        description="participant_id",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        operation_id="get_case",
        manual_parameters=[participant_id],
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Geneyx"]
    )

    def get(self, request):
        try:
            participant_id = request.query_params["participant_id"]
            case = fetch_case(participant_id)
            return Response(status=status.HTTP_200_OK, data=case)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetCaseNotes(APIView):
    """"""
    permission_classes = [AllowAny]

    participant_id = openapi.Parameter(
        "participant_id",
        openapi.IN_QUERY,
        description="participant_id",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        operation_id="get_case",
        manual_parameters=[participant_id],
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Geneyx"]
    )

    def get(self, request):
        try:
            participant_id = request.query_params["participant_id"]
            case_notes = fetch_case_notes(participant_id)
            return Response(status=status.HTTP_200_OK, data=case_notes)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)