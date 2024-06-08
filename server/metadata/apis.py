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
from config.selectors import TableValidator, response_constructor, response_status
from metadata.models import Participant, Family
from metadata.services import ParticipantSerializer, FamilySerializer, get_or_create_sub_models
from metadata.selectors import parse_participant


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
            "age_at_enrollment",
        ]
        all = Participant.objects.all()
        import pdb

        pdb.set_trace()
        return Response(status=status.HTTP_200_OK, data=all)


class CreateParticipantAPI(APIView):
    """
    API endpoint for creating Participant entries in the database. [Bulk Enabled]

    This API allows for bulk creation of participants through a POST request. Each participant's data is validated against a JSON schema, and then processed to either create a new Participant entry or return an error if the data is invalid. The API uses Django REST Framework's atomic transactions to ensure data integrity during creation operations.

    Authentication and permissions:
    - No authentication or permissions are required to access this endpoint in the current setup. (This should be configured according to your security requirements.)

    Request body:
    - The request expects an array of participant objects. Each participant object must include all necessary fields as defined in the Participant model.
    - Fields include participant_id, gregor_center, consent_code, and other participant-related information.

    Responses:
    - 200 OK: Returns a list of created participant objects along with their details if all submissions are successful.
    - 207 Multi-Status: Returns when some of the participant submissions are successful, and some are not. Each participant entry in the response specifies whether it was successfully created or not.
    - 400 Bad Request: Returns when there are validation errors in the incoming data or other processing errors occur.

    The API also provides detailed error messages to help diagnose issues with the submitted data.
    """

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_id="create_participants",
        request_body=ParticipantSerializer(many=True),
        responses={
            200: "All submissions successfull",
            207: "Some submissions of participants were not successful.",
            400: "Bad request",
        },
        tags=["Participant"],
    )
    @transaction.atomic
    def post(self, request):
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for index, datum in enumerate(request.data):
                identifier = datum["participant_id"]
                datum = parse_participant(participant=datum)
                validator.validate_json(json_object=datum, table_name="participant")
                results = validator.get_validation_results()

                if results["valid"] is True:
                    datum = get_or_create_sub_models(datum=datum)
                    serializer = ParticipantSerializer(data=datum)

                    if serializer.is_valid():
                        try:
                            participant_instance = serializer.create(
                                validated_data=serializer.validated_data
                            )
                            participant_data = ParticipantSerializer(
                                participant_instance
                            ).data
                            # response_data.append(
                            #     response_constructor(
                            #         identifier=identifier,
                            #         status="SUCCESS",
                            #         code=200,
                            #         message=f"Participant {identifier} created.",
                            #         data=participant_data,
                            #     )
                            # )
                            accepted_requests = True
                        except Exception as error:
                            response_data.append(
                                response_constructor(
                                    identifier=identifier,
                                    status="BAD REQUEST",
                                    code=400,
                                    data=str(error),
                                )
                            )
                            rejected_requests = True
                            continue
                    else:
                        error_data = []
                        for item in serializer.errors:
                            text = {item: serializer.errors[item]}
                            error_data.append(text)
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    error_data = []
                    for item in results["errors"]:
                        text = {[item][0].title()}
                        error_data.append(text)
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            status="BAD REQUEST",
                            code=400,
                            data=error_data,
                        )
                    )
                    rejected_requests = True
                    continue

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateFamilyApi(APIView):
    """ """

    @swagger_auto_schema(
        operation_id="create_family",
        request_body=FamilySerializer(many=True),
        responses={
            200: "All submissions of families were successfull",
            207: "Some submissions of families were not successful.",
            400: "Bad request",
        },
        tags=["Family"],
    )
    def post(self, request):
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for index, datum in enumerate(request.data):
                identifier = datum["family_id"]
                validator.validate_json(json_object=datum, table_name="family")
                results = validator.get_validation_results()

                if results["valid"] is True:
                    serializer = FamilySerializer(data=datum)
                    if serializer.is_valid():
                        validated_data = serializer.validated_data
                        family_instance = serializer.create(
                            validated_data=serializer.validated_data
                        )
                        family_data = FamilySerializer(family_instance).data
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                status="SUCCESS",
                                code=200,
                                message=f"Family {identifier} created.",
                                data=family_data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = []
                        for item in serializer.errors:
                            text = {item: serializer.errors[item]}
                            error_data.append(text)
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    error_data = []
                    for item in results["errors"]:
                        text = {[item][0].title()}
                        error_data.append(text)
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            status="BAD REQUEST",
                            code=400,
                            data=error_data,
                        )
                    )
                    rejected_requests = True
                    continue

            status_code = response_status(accepted_requests, rejected_requests)

            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(
                0,
                response_constructor(
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
