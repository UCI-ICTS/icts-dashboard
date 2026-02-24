#!/usr/bin/env python
# geneyx/apis.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from geneyx.services import get_ga_cases, get_ga_case


class GetCases(APIView):
    """
    Get list of Geneyx case IDs. Note that these may not always include the UCI participant ID
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="get_cases",
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["Geneyx"]
    )

    def get(self, request):
        manifest = get_ga_cases()
        try:
            return Response(status=status.HTTP_200_OK, data=manifest)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetCase(APIView):
    """
    Get json object of one Geneyx case and its attributes
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="get_case",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Geneyx case ID",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["Geneyx"],
    )

    def get(self, request):
        case_id = request.GET.get('id', '')
        manifest = get_ga_case(case_id)
        try:
            return Response(status=status.HTTP_200_OK, data=manifest)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetCaseNotes(APIView):
    """
    Get json object of one Geneyx case's notes
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="get_case_notes",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="Get Geneyx case notes as embedded HTML",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["Geneyx"],
    )

    def get(self, request):
        case_id = request.GET.get('id', '')
        manifest = get_ga_case(case_id)
        try:
            return Response(status=status.HTTP_200_OK, data=manifest)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)