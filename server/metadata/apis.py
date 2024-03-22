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
from utilities.api_response import ApiResponse
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
        # import pdb; pdb.set_trace()
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
        api_response = ApiResponse(operation="create_participants")
        try:
            for datum in request.data:
                identifier = datum['participant_id']
                datum = get_sub_models(datum)
                serializer = self.InputSerializer(data=datum)
                if serializer.is_valid() is True:
                    api_response.add_success(identifier)
                    serializer.save()
                else:
                    for item in serializer.errors:
                        text = {item: serializer.errors[item][0].title()}
                        api_response.add_error(identifier, text)

            response_data = api_response.get_response()

            if len(response_data['errors']) == 0:
                return Response(status=status.HTTP_200_OK, data=response_data)
            else:
                return Response(status=status.HTTP_207_MULTI_STATUS, data=response_data)
        
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={str(error)})