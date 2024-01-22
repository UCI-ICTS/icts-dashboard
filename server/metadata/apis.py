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
    
class SubmitParticipantAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Participant
            fields = '__all__'

    authentication_classes = []
    permission_classes = []

    request_body = openapi.Schema(
        type=openapi.TYPE_ARRAY,
        title="Participant Submission",
        description="",
        required=[""],
        items=openapi.Items(type=openapi.TYPE_OBJECT)
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "All submissions of participants are successful.",
            400: "Bad request"
        }
    )
    def post(self,request):
        results = {}
        for datum in request.data:
            identifier = datum['participant_id']
            results[identifier] = {"number_of_errors": 0, "error_detail": []}
            serializer = self.InputSerializer(data=datum)
            if serializer.is_valid() is True:
                results[identifier] = {"number_of_errors": 0, "error_detail": "Item saved"}
                serializer.save()
            else:
                for item in serializer.errors:
                    results[identifier]["number_of_errors"] += 1
                    text = {item: serializer.errors[item][0].title()}
                    results[identifier]['error_detail'].append(text)
        return Response(status=status.HTTP_200_OK, data=results)