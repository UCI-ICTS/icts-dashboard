#!/usr/bin/env python
# metadata/apis.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from config.selectors import (
    response_constructor,
    response_status,
    bulk_retrieve,
    bulk_model_retrieve
)

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
    FamilySerializer,
    PhenotypeSerializer,
    create_metadata,
    update_metadata,
    delete_metadata,
    create_or_update_metadata
)


class CrearteParticipantAPI(APIView):
    """
    API view to create Participant entries.

    This API endpoint accepts a list of participant data objects, checks that 
    the submission does not exist, and creates new entries based on the 
    presence of a 'participant_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="create_participants",
        request_body=ParticipantInputSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Participant"],
    )

    def post(self, request):
        # Retrieve existing participants in bulk
        participants = bulk_model_retrieve(
            request_data=request.data,
            model_class=Participant,
            id="participant_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []
        
        # Split request data into new and existing records
        for datum in request.data:
            participant_id = datum.get("participant_id")  # Safely retrieve participant_id
            if participant_id and participant_id in participants:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Handle creating new participants
            for datum in new_records:
                return_data, result = create_metadata(
                    table_name="participant",
                    identifier=datum["participant_id"],
                    datum=datum
                )
                response_data.append(return_data)
                if result == "accepted_request":
                    accepted_requests = True
                else:
                    rejected_requests = True

            # Handle updating existing participants
            for datum in existing_records:
                response_data.append(
                    response_constructor(
                        identifier=datum["participant_id"],
                        request_status="BAD REQUEST",
                        code=400,
                        data="Participant already exists",
                    )
                )
                rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            identifier = datum.get("participant_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class ReadParticipantAPI(APIView):
    """
    API view to read Participant entries.

    This API endpoint requests a list of participant data objects based on
     the 'participant_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="read_participants",
        operation_description="Retrieve participant details by their IDs",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of participant IDs (e.g., P1-0,P2-1,P3-0)",
                type=openapi.TYPE_STRING,
            )
        ],
        
        responses={
            200: "All queries returned successfull",
            207: "Some queries were not successfull",
            400: "Bad request",
        },
        tags=["Participant"],
    )

    def get(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch participants
        participants = bulk_retrieve(
            model_class=Participant,
            id_list=id_list,
            id_field="participant_id"
        )

        try:
            for identifier in id_list:
                if identifier in participants:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="SUCCESS",
                            code=200,
                            data=participants[identifier]
                        )
                    )
                    accepted_requests = True
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            data="Participant not found"
                        )
                    )
                    rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0,
                response_constructor(
                    identifier=id_list,
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
   

class UpdateParticipantAPI(APIView):
    """
    API view to create or update Participant entries.

    This API endpoint accepts a list of participant data objects, validates
     them, and either creates new entries or updates existing ones based on
     the presence of a 'participant_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
        # Retrieve existing participants in bulk
        participants = bulk_model_retrieve(
            request_data=request.data,
            model_class=Participant,
            id="participant_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            participant_id = datum.get("participant_id")  
            if participant_id and participant_id in participants:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Reject non-existent records (Prevent updates to records that don't exist)
            for datum in new_records:
                response_data.append(
                    response_constructor(
                        identifier=datum.get("participant_id", "UNKNOWN"),
                        request_status="BAD REQUEST",
                        code=400,
                        data="Participant does not exist and cannot be updated.",
                    )
                )
                rejected_requests = True

            # Handle updating existing participants
            for datum in existing_records:
                participant_id = datum["participant_id"]
                return_data, result = update_metadata(
                    table_name="participant",
                    identifier=participant_id,
                    model_instance=participants.get(participant_id),
                    datum=datum
                )
                response_data.append(return_data)
                if result == "accepted_request":
                    accepted_requests = True
                else:
                    rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            identifier = datum.get("participant_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class DeleteParticipantAPI(APIView):
    """
    API view to create or update Participant entries.

    This API endpoint accepts a list of participant data objects, validates
     them, and either creates new entries or updates existing ones based on
     the presence of a 'participant_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="delete_participants",
        request_body=ParticipantInputSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Participant"],
    )

    def delete(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch participants
        participants = bulk_retrieve(
            model_class=Participant,
            id_list=id_list,
            id_field="participant_id"
        ) 
        try:
            for identifier in id_list:
                if identifier in participants:
                    return_data, result = delete_metadata(
                        table_name="participant",
                        identifier=identifier, 
                        id_field="participant_id"
                    )
                    response_data.append(return_data)

                    if result == "accepted_request":
                        accepted_requests = True
                    else:
                        rejected_requests = True
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            data="Participant not found"
                        )
                    )
                    rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0,
                response_constructor(
                    identifier=id_list,
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
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

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_family",
        request_body=FamilySerializer(many=True),
        responses={
            200: "All submissions of families were successfull",
            207: "Some submissions of families were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        families = bulk_model_retrieve(
            request_data=request.data,
            model_class=Family,
            id="family_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False
        
        try:
            for index, datum in enumerate(request.data):
                identifier = datum["family_id"]
                return_data, result = create_or_update_metadata(
                    table_name="family",
                    identifier=datum["family_id"],
                    model_instance=families.get(datum["family_id"]),
                    datum=datum
                )

                if result == "accepted_request":
                    accepted_requests = True
                elif result == "rejected_request":
                    rejected_requests = True
                response_data.append(return_data)

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
    """
    API view to create or update Analyte entries.

    This API endpoint accepts a list of analyte data objects, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'genetic_findings_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    @swagger_auto_schema(
        operation_id="submit_analyte",
        request_body=AnalyteSerializer(many=True),
        responses={
            200: "All submissions of genetic findings were successfull",
            207: "Some submissions of genetic findings were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )
    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        analytes = bulk_model_retrieve(
            request_data=request.data,
            model_class=Analyte,
            id="analyte_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_metadata(
                    table_name="analyte",
                    identifier = datum["analyte_id"],
                    model_instance = analytes.get(datum["analyte_id"]),
                    datum = datum
                )

                if result == "accepted_request":
                    accepted_requests = True
                elif result == "rejected_request":
                    rejected_requests = True
                response_data.append(return_data)
                continue

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0,
                response_constructor(
                    identifier=datum["analyte_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdatePhenotypeApi(APIView):
    """
    API view to create or update phenotype entries.

    This API endpoint allows clients to submit multiple phenotype entries at 
    once. Each phenotype can either be created or updated depending on whether 
    it already exists. The request must be in the form of a JSON array of
    phenotype objects.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    @swagger_auto_schema(
        operation_id="create_phenotype",
        request_body=PhenotypeSerializer(many=True),
        responses={
            200: "All submissions of phenotypes were successfull",
            207: "Some submissions of phenotypes were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        phenotypes = bulk_model_retrieve(
            request_data=request.data,
            model_class=Phenotype,
            id="phenotype_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_metadata(
                    table_name="phenotype",
                    identifier = datum["phenotype_id"],
                    model_instance = phenotypes.get(datum["phenotype_id"]),
                    datum = datum
                )

                if result == "accepted_request":
                    accepted_requests = True
                elif result == "rejected_request":
                    rejected_requests = True
                response_data.append(return_data)
                continue

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0,
                response_constructor(
                    identifier=datum["phenotype_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
        

class CreateOrUpdateGeneticFindings(APIView):
    """
    API view to create or update Genetic Findings entries.

    This API endpoint accepts a list of genetic findings data objects, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'genetic_findings_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    @swagger_auto_schema(
        operation_id="submit_genetic_findings",
        request_body=GeneticFindingsSerializer(many=True),
        responses={
            200: "All submissions of genetic findings were successfull",
            207: "Some submissions of genetic findings were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )
    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        genetic_findings = bulk_model_retrieve(
            request_data=request.data,
            model_class=GeneticFindings,
            id="genetic_findings_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_metadata(
                    table_name="genetic_findings",
                    identifier = datum["genetic_findings_id"],
                    model_instance = genetic_findings.get(datum["genetic_findings_id"]),
                    datum = datum
                )

                if result == "accepted_request":
                    accepted_requests = True
                elif result == "rejected_request":
                    rejected_requests = True
                response_data.append(return_data)
                continue

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            response_data.insert(0,
                response_constructor(
                    identifier=datum["genetic_findings_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

