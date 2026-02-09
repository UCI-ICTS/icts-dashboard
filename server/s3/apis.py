#!/usr/bin/env python
# s3/apis.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from s3.services import fetch_manifest, presign_view_url

class GetManifestAPI(APIView):
    """"""
    # authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="get_manifest",
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["AWS S3"]
    )

    def get(self, request):
        manifest = fetch_manifest("icts-dashboard-analysis-files")
        # response_data = [manifest]
        try:
            # serilized_return_data = [response_data]
            return Response(status=status.HTTP_200_OK, data=manifest)
        except Exception as error:
            # response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST)

class GetPresignedView(APIView):
    """"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    bucket_param = openapi.Parameter(
        "bucket",
        openapi.IN_QUERY,
        description="S3 bucket name",
        type=openapi.TYPE_STRING,
        default="icts-dashboard-analysis-files"
    )

    key_param = openapi.Parameter(
        "key",
        openapi.IN_QUERY,
        description="S3 object key within the bucket",
        type=openapi.TYPE_STRING,
        default="test-data/rna/fake-file-1.txt"
    )

    @swagger_auto_schema(
        operation_id="get_aws_file",
        manual_parameters=[bucket_param, key_param],
        responses={
            200: "Submission successful",
            400: "Bad request",
        },
        tags=["AWS S3"]
    )

    def get(self, request):

        try:
            bucket = request.query_params["bucket"]
            key = request.query_params["key"]
            url = presign_view_url(bucket=bucket, key=key, expires_seconds=300)
            return Response({"url": url})
        except Exception as error:
            print(error)
            # response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST)