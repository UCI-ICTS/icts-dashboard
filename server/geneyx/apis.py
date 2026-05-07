#!/usr/bin/env python
# geneyx/apis.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from geneyx.selectors import (
    get_all_samples,
    get_sample,
    get_all_cases,
    get_case,
    get_case_notes,
)


class GeneyxViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        method="post",
        operation_description="Geneyx APIs",
        responses={200: "Ok", 400: "Bad request"},
        tags=["GeneyxAPIs"],
    )
    @action(detail=False, methods=["post"], url_path="get_samples")
    def get_all_samples(self, request):
        serializer = get_all_samples()
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["post"], url_path="get_sample")
    def get_sample(self, request):
        sample_id = request.data
        sample = get_sample(sample_id)
        return Response(sample, status=200)

    @action(detail=False, methods=["post"], url_path="get_all_cases")
    def get_all_cases(self, request):
        serializer = get_all_cases()
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["post"], url_path="get_case")
    def get_case(self, request):
        case_id = request.data
        case = get_case(case_id)
        return Response(case, status=200)

    @action(detail=False, methods=["post"], url_path="get_case_notes")
    def get_sample(self, request):
        case_id = request.data
        case_notes = get_case_notes(case_id)
        return Response(case_notes, status=200)
