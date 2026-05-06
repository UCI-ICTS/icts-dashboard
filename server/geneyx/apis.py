#!/usr/bin/env python
# geneyx/apis.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from services import GeneyxOutputSerializer
import requests


class GeneyxViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        method="post",
        operation_description="Retrieve all VCF sample entries",
        responses={200: "Ok", 400: "Bad request"},
        tags=["GeneyxGetSamples"],
    )
    @action(detail=False, methods=["post"], url_path="Samples")
    def get_all_samples(self):
        serializer = GeneyxOutputSerializer.get_all_samples()
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        method="post",
        operation_description="Retrieve a VCF sample given its Geneyx sample ID",
        responses={200: "Ok", 400: "Bad request"},
        tags=["GeneyxGetSample"],
    )
    @action(detail=False, methods=["post"], url_path="Sample")
    def get_sample(self):
        serializer = GeneyxOutputSerializer.get_sample(sample_id)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        method="post",
        operation_description="Retrieve all cases",
        responses={200: "Ok", 400: "Bad request"},
        tags=["GeneyxGetCases"],
    )
    @action(detail=False, methods=["post"], url_path="Cases")
    def get_all_cases(self):
        serializer = GeneyxOutputSerializer.get_all_cases()
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        method="post",
        operation_description="Retrieve a case given a Geneyx case ID",
        responses={200: "Ok", 400: "Bad request"},
        tags=["GeneyxGetCase"],
    )
    @action(detail=False, methods=["post"], url_path="Case")
    def get_sample(self):
        serializer = GeneyxOutputSerializer.get_sample(case_id)
        return Response(serializer.data, status=200)
