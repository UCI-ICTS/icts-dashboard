# metadata/apis.py

import json
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from metadata.models import Participant

class GetMetadataAPI(APIView):
    
    def get(self, request):
        print(request)
        return_values = [
            "internal_project_id",
            "gregor_center",
            "consent_code",
            "recontactable",
            "prior_testing",
            "pmid_id",
            "family_id",
            "paternal_id",
            "maternal_id",
            "twin_id",
            "proband_relationship",
            "proband_relationship_detail",
            "sex",
            "sex_detail",
            "reported_race",
            "reported_ethnicity",
            "ancestry_detail",
            "age_at_last_observation",
            "affected_status",
            "phenotype_description",
            "age_at_enrollment"
        ]
        
        return Response(status=status.HTTP_200_OK, data={"message": "user account created"})
    
class SubmitMetadataAPI(APIView):

    def post(self,request):
        print(request)
        return Response(status=status.HTTP_200_OK, data={"message":"it worked"})