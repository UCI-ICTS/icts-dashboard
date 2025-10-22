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
from config.selectors import response_constructor

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
        phenotypes = phenotype_extraction(data['raw_text'])
        # import pdb; pdb.set_trace()
        # for phenotype in phenotypes:
        #     response_data.append(
        #         response_constructor(
        #             identifier=phenotype["hpo_id"],
        #             request_status="SUCCESS",
        #             code=200,
        #             message=phenotype["rationale"],
        #             data=phenotype

        #         )
        #     )
        try:
            return Response(status=status.HTTP_200_OK, data=phenotypes)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
