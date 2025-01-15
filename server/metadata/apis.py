#!/usr/bin/env python
# metadata/apis.py

import json
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from config.selectors import (
    TableValidator,
    response_constructor,
    response_status,
    remove_na,
    compare_data,
)

from experiments.models import Experiment
from experiments.services import ExperimentSerializer

from metadata.models import (
    Participant,
    Family,
    Analyte,
    GeneticFindings,
    Phenotype
)
from metadata.services import (
    AnalyteSerializer,
    GeneticFindingsSerializer,
    ParticipantInputSerializer,
    ParticipantOutputSerializer,
    FamilySerializer,
    PhenotypeSerializer,
    get_or_create_sub_models,
)
from metadata.selectors import (
    participant_parser,
    parse_geneti_findings,
    get_family,
    get_phenotype,
    get_analyte,
    get_genetic_findings,
)


class GetMetadataAPI(APIView):
    """[WIP] Placeholder: Does Not Work"""

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

        return Response(status=status.HTTP_200_OK, data=all)


class GetAllTablesAPI(APIView):
    """"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="get_tables",
        responses={
            200: "Submission successfull",
            400: "Bad request",
        },
        tags=["Participant"],
    )

    def get(self, request):
        response_data = []
        try:

            serialized_participants = ParticipantOutputSerializer(Participant.objects.all(), many=True)
            serilized_families = FamilySerializer(Family.objects.all(), many=True)
            serilized_genetic_findings = GeneticFindingsSerializer(GeneticFindings.objects.all(), many=True)
            serialized_analytes = AnalyteSerializer(Analyte.objects.all(), many=True)
            serialized_phenotypes = PhenotypeSerializer(Phenotype.objects.all(), many=True)
            serialized_experiments = ExperimentSerializer(Experiment.objects.all(), many=True)

            serilized_return_data = {
                'participants': serialized_participants.data,
                'families': serilized_families.data,
                'genetic_findings': serilized_genetic_findings.data,
                'analytes': serialized_analytes.data,
                'phenotypes': serialized_phenotypes.data,
                'experiments': serialized_experiments.data
            }

            return Response(status=status.HTTP_200_OK, data=serilized_return_data)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class UpdateParticipantAPI(APIView):
    """"""

    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_id="update_participants",
        request_body=ParticipantInputSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Participant"],
    )
    def post(self, request):
        participant_ids = [datum["participant_id"] for datum in request.data]
        participants = Participant.objects.in_bulk(participant_ids)
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for index, datum in enumerate(request.data):
                identifier = datum["participant_id"]
                participant_instance = participants.get(identifier)
                if participant_instance is None:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            message=f"Participant {identifier} not found."
                        )
                    )
                    rejected_requests = True
                    continue
                datum = participant_parser(participant=datum)
                validator.validate_json(json_object=datum, table_name="participant")
                results = validator.get_validation_results()
                if results["valid"]:
                    old_data=ParticipantOutputSerializer(participant_instance).data
                    changes = compare_data(
                        old_data=old_data,
                        new_data=datum
                    )
                    if not changes:
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                request_status="SUCCESS",
                                code=200,
                                message=f"Participant {identifier} had no changes.",
                                data={
                                    'participant_update': None,
                                    'updated_instance':old_data
                                }
                            )
                        )
                        accepted_requests = True
                        continue                        
                    datum = get_or_create_sub_models(datum=datum)
                    serializer = ParticipantInputSerializer(participant_instance, data=datum)
                    if serializer.is_valid():
                        updated_instance = serializer.save()
                        participant_data = {
                            'participant_update': changes,
                            'updated_instance': ParticipantOutputSerializer(updated_instance).data
                        }

                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                request_status="SUCCESS",
                                code=200,
                                message=f"Participant {identifier} updated.",
                                data=participant_data,
                            )
                        )
                        accepted_requests = True
                        continue
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=results["errors"],
                        )
                    )
                    rejected_requests = True
                    continue
            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0,
                response_constructor(
                    identifier=identifier,
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

       
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
        request_body=ParticipantInputSerializer(many=True),
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
                parsed_participant = participant_parser(participant=datum)
                validator.validate_json(json_object=parsed_participant, table_name="participant")
                results = validator.get_validation_results()
                if results["valid"] is True:
                    parsed_participant = get_or_create_sub_models(datum=parsed_participant)
                    serializer = ParticipantInputSerializer(data=parsed_participant)
                    if serializer.is_valid():
                        
                        try:
                            participant_instance = serializer.create(
                                validated_data=serializer.validated_data
                            )
                            participant_data = ParticipantOutputSerializer(
                                participant_instance
                            ).data

                            response_data.append(
                                response_constructor(
                                    identifier=identifier,
                                   request_status="SUCCESS",
                                    code=200,
                                    message=f"Participant {identifier} created.",
                                    data=participant_data,
                                )
                            )
                            accepted_requests = True

                        except Exception as error:
                            response_data.append(
                                response_constructor(
                                    identifier=identifier,
                                   request_status="BAD REQUEST",
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
                               request_status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=results["errors"],
                        )
                    )
                    rejected_requests = True
                    continue

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateFamilyApi(APIView):
    """
    API view to create or update Family entries.

    This API endpoint accepts a list of family data objects, validates them, and either creates new entries or updates existing ones based on the presence of a 'family_id'.
    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

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
                    family_instance = get_family(family_id=identifier)
                    serializer = FamilySerializer(family_instance, data=datum)

                    if serializer.is_valid():
                        family_instance = serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="UPDATED" if family_instance else "CREATED",
                                code=200 if family_instance else 201,
                                message=(
                                    f"Family {identifier} updated."
                                    if family_instance
                                    else f"Family {identifier} created."
                                ),
                                data=FamilySerializer(family_instance).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: serializer.errors[item]}
                            for item in serializer.errors
                        ]
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=results["errors"],
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
                    identifier=identifier,request_status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdatePhenotypeApi(APIView):
    """
    API view to create or update phenotype entries.

    This API endpoint allows clients to submit multiple phenotype entries at once. Each phenotype can either be
    created or updated depending on whether it already exists. The request must be in the form of a JSON array of
    phenotype objects.

    Attributes:
        swagger_auto_schema: A decorator that provides Swagger UI with metadata about this API endpoint,
            including the expected structure of the request body, possible response statuses, and associated tags.

    Methods:
        post(request): Processes a POST request that submits phenotype data.
    """

    @swagger_auto_schema(
        operation_id="create_phenotype",
        request_body=PhenotypeSerializer(many=True),
        responses={
            200: "All submissions of phenotypes were successfull",
            207: "Some submissions of phenotypes were not successful.",
            400: "Bad request",
        },
        tags=["Phenotype"],
    )
    def post(self, request):
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for datum in request.data:
                identifier = datum["phenotype_id"]
                parsed_phenotype = remove_na(datum=datum)
                validator.validate_json(
                    json_object=parsed_phenotype, table_name="phenotype"
                )
                results = validator.get_validation_results()
                if results["valid"] is True:
                    existing_phenotype = get_phenotype(phenotype_id=identifier)
                    serializer = PhenotypeSerializer(
                        existing_phenotype, data=parsed_phenotype
                    )

                    if serializer.is_valid():
                        phenotype_instance = serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="UPDATED" if existing_phenotype else "CREATED",
                                code=201 if existing_phenotype else 200,
                                message=(
                                    f"Phenotype {identifier} updated."
                                    if existing_phenotype
                                    else f"Phenotype {identifier} created."
                                ),
                                data=PhenotypeSerializer(phenotype_instance).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: serializer.errors[item]}
                            for item in serializer.errors
                        ]
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=results["errors"],
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
                    identifier=identifier,request_status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateAnalyte(APIView):
    """ """

    @swagger_auto_schema(
        operation_id="create_analyte",
        request_body=AnalyteSerializer(many=True),
        responses={
            200: "All submissions of analytes were successfull",
            207: "Some submissions of analytes were not successful.",
            400: "Bad request",
        },
        tags=["Analyte"],
    )
    def post(self, request):
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for datum in request.data:
                identifier = datum["analyte_id"]
                parsed_analyte = remove_na(datum=datum)
                validator.validate_json(
                    json_object=parsed_analyte, table_name="analyte"
                )

                results = validator.get_validation_results()
                if results["valid"] is True:
                    analyte_instance = get_analyte(analyte_id=identifier)
                    serializer = AnalyteSerializer(
                        analyte_instance, data=parsed_analyte
                    )

                    if serializer.is_valid():
                        analyte_instance = serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="UPDATED" if analyte_instance else "CREATED",
                                code=200 if analyte_instance else 201,
                                message=(
                                    f"Analyte {identifier} updated."
                                    if analyte_instance
                                    else f"Analyte {identifier} created."
                                ),
                                data=AnalyteSerializer(analyte_instance).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: serializer.errors[item]}
                            for item in serializer.errors
                        ]
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=results["errors"],
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
                    identifier=identifier,request_status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateGeneticFindings(APIView):
    """ """

    @swagger_auto_schema(
        operation_id="create_genetic_findings",
        request_body=GeneticFindingsSerializer(many=True),
        responses={
            200: "All submissions of genetic findings were successfull",
            207: "Some submissions of genetic findings were not successful.",
            400: "Bad request",
        },
        tags=["Genetic Findings"],
    )
    def post(self, request):
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for datum in request.data:
                identifier = datum["genetic_findings_id"]
                parsed_geneti_findings = parse_geneti_findings(genetic_findings=datum)
                validator.validate_json(
                    json_object=parsed_geneti_findings, table_name="genetic_findings"
                )

                results = validator.get_validation_results()
                if results["valid"] is True:
                    genetic_findings_instance = get_genetic_findings(
                        genetic_findings_id=identifier
                    )
                    serializer = GeneticFindingsSerializer(
                        genetic_findings_instance, data=parsed_geneti_findings
                    )
                    if serializer.is_valid():
                        genetic_findings_instance = serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status=(
                                    "UPDATED"
                                    if genetic_findings_instance
                                    else "CREATED"
                                ),
                                code=200 if genetic_findings_instance else 201,
                                message=(
                                    f"Genetic Findings {identifier} updated."
                                    if genetic_findings_instance
                                    else f"Genetic Findings {identifier} created."
                                ),
                                data=GeneticFindingsSerializer(
                                    genetic_findings_instance
                                ).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: serializer.errors[item]}
                            for item in serializer.errors
                        ]
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=results["errors"],
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
                    identifier=identifier,request_status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
