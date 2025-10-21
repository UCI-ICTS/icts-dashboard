#!/usr/bin/env python
# hpo/apis.py

import json
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from hpo.services import phenotype_extraction

class GetHPOs(APIView):
    """
    """

    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_id="get_hpos",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "raw_text": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Text to decode for HPO terms",
                    example="gait instability with ataxia and seizures since childhood"
                )
            }
        ),
        responses={
            200: "Submission successfull",
            400: "Bad request",
        },
        tags = ["HPO"]
    )

    def post(self, request):
        response_data = []
        data = request.data
        print(data['raw_text'])
        # import pdb; pdb.set_trace()
        res = phenotype_extraction(data['raw_text'])
        for r in res:
            print(r)
            response_data.append(r)
        try:
            return Response(status=status.HTTP_200_OK, data=response_data)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
