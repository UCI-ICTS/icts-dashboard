#!/usr/bin/env python
# metadata/apis.py

import json
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from metadata.models import Participant, InternalProjectId
from config.selectors import response_constructor, response_status
from metadata.services import ParticipantSerializer
from config.selectors import TableValidator
from metadata.services import get_or_create_sub_models

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
        return Response(status=status.HTTP_200_OK, data=all)
    
class CreateParticipantAPI(APIView):
    """
    """
    
    class InputSerializer(serializers.ModelSerializer):
        pmid_ids = serializers.SerializerMethodField()
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
        request_body=InputSerializer(many=True),
        responses={
            200: OutputSerializer(many=True),
            207: "Some submissions of participants were not successful.",
            400: "Bad request"
        },
        tags=["Participant"]
    )

    @transaction.atomic
    def post(self,request):
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for index, datum in enumerate(request.data):
                identifier = datum['participant_id']
                # datum = get_sub_models(datum)
                validator.validate_json(
                    json_object=datum,
                    table_name="participant"
                )
                results = validator.get_validation_results()

                if results['valid'] is True:
                    datum = get_or_create_sub_models(datum=datum)
                    serializer = ParticipantSerializer(data=datum)
                    
                    if serializer.is_valid():
                        serializer.create(validated_data=serializer.validated_data)
                        
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
                            text = {item: serializer.errors[item]}
                            error_data.append(text)
                        response_data.append(response_constructor(
                            identifier=identifier,
                            status = "BAD REQUEST",
                            code= 400,
                            data=error_data
                        ))
                        rejected_requests = True
                        continue

                else:
                    error_data = []
                    for item in results['errors']:
                        text = {[item][0].title()}
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