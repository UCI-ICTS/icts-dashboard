#!/usr/bin/env python
# search/apis.py

import json
from django.apps import apps
from django.db.models import Q
from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from itertools import chain
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class TestConnection(APIView):
    """Test Connection

    API for testing connections to DB
    """
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_id="test_connection",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={}
            )
        ),
        responses={
            200: "All submissions of analytes were successfull",
            207: "Some submissions of analytes were not successful.",
            400: "Bad request",
        },
        tags=["Test"],
    )

    def post(self, request):
        
        data = {"request":str(request.data)}


        return Response(data)


class SearchTablesAPI(APIView):
    """ """

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
