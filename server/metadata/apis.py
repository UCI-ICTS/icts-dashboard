# metadata/apis.py

import json
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from metadata.models import Participant, InternalProjectId
from config.selectors import response_constructor, response_status
from metadata.selectors import get_sub_models

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
        all = Participant.objects.all()
        return Response(status=status.HTTP_200_OK, data={"message": "user account created"})
    
class CreateParticipantAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Participant
            fields = '__all__'
    
    class OutputSerializer(serializers.ModelSerializer):
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
        items=openapi.Items(
            type=openapi.TYPE_OBJECT
        )
    )

    @swagger_auto_schema(
        request_body=request_body,
        responses={
            200: "All submissions of participants are successful.",
            207: "Some submissions of participants were not successful.",
            400: "Bad request"
        },
        tags=["Participant"]
    )
    def post(self,request):
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for datum in request.data:
                identifier = datum['participant_id']
                datum = get_sub_models(datum)
                serializer = self.InputSerializer(data=datum)
                if serializer.is_valid() is True:
                    serializer.save()
                    response_data.append(response_constructor(
                        identifier=identifier,
                        status = "SUCCESS",
                        code= 200,
                        message= f"Participant {identifier} created.",
                    ))
                    accepted_requests = True
                else:
                    error_data = []
                    for item in serializer.errors:
                        text = {item: serializer.errors[item][0].title()}
                        error_data.append(text)
                    response_data.append(response_constructor(
                        identifier=identifier,
                        status = "BAD REQUEST",
                        code= 400,
                        data=error_data
                    ))
                    rejected_requests = True
                    continue
            

            
            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={str(error)})