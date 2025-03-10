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
            207: "Some updates were not successful",
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

        id_list = [id.strip() for id in request.GET.get("ids", "").split(",") if id.strip()]

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
    API view to delete Participant entries.

    This API endpoint delets a list of participant data objects based on
     the 'participant_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="delete_participants",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of participant IDs (e.g., P1-0,P2-1,P3-0)",
                type=openapi.TYPE_STRING,
            )
        ],
        
        responses={
            200: "All queries successfully deleted",
            207: "Some queries were not successfully deleted",
            400: "Bad request",
        },
        tags=["Participant"],
    )

    def delete(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = [id.strip() for id in request.GET.get("ids", "").split(",") if id.strip()]

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

class CreateFamilyAPI(APIView):
    """
    API view to create Family entries.

    This API endpoint accepts a list of family data objects, checks that
    the submission does not exist, and creates new entries based on the
    presence of a 'family_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="create_families",
        request_body=FamilySerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successful",
            400: "Bad request",
        },
        tags=["Family"],
    )

    def post(self, request):
        # Retrieve existing families in bulk
        families = bulk_model_retrieve(
            request_data=request.data,
            model_class=Family,
            id="family_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            family_id = datum.get("family_id")  # Safely retrieve family_id
            if family_id and family_id in families:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Handle creating new families
            for datum in new_records:
                return_data, result = create_metadata(
                    table_name="family",
                    identifier=datum["family_id"],
                    datum=datum
                )
                response_data.append(return_data)
                if result == "accepted_request":
                    accepted_requests = True
                else:
                    rejected_requests = True

            # Handle updating existing families
            for datum in existing_records:
                response_data.append(
                    response_constructor(
                        identifier=datum["family_id"],
                        request_status="BAD REQUEST",
                        code=400,
                        data="Family already exists",
                    )
                )
                rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            identifier = datum.get("family_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class ReadFamilyAPI(APIView):
    """
    API view to read Family entries.

    This API endpoint requests a list of family data objects based on the 'family_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="read_families",
        operation_description="Retrieve families details by their IDs",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of family IDs (e.g., F1, F2, F3)",
                type=openapi.TYPE_STRING,
            )
        ],

        responses={
            200: "All queries returned successfull",
            207: "Some queries were not successfull",
            400: "Bad request",
        },
        tags=["Family"],
    )

    def get(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch families
        families = bulk_retrieve(
            model_class=Family,
            id_list=id_list,
            id_field="family_id"
        )

        try:
            for identifier in id_list:
                if identifier in families:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="SUCCESS",
                            code=200,
                            data=families[identifier]
                        )
                    )
                    accepted_requests = True
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            data="Family not found"
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

class UpdateFamilyAPI(APIView):
    """
    API view to create or update Family entries.

    This API endpoint accepts a list of family data objects, validates
     them, and either creates new entries or updates existing ones based on
     the presence of a 'family_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_families",
        request_body=FamilySerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Family"],
    )

    def post(self, request):
        # Retrieve existing families in bulk
        families = bulk_model_retrieve(
            request_data=request.data,
            model_class=Family,
            id="family_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            family_id = datum.get("family_id")
            if family_id and family_id in families:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Reject non-existent records (Prevent updates to records that don't exist)
            for datum in new_records:
                response_data.append(
                    response_constructor(
                        identifier=datum.get("family_id", "UNKNOWN"),
                        request_status="BAD REQUEST",
                        code=400,
                        data="Family does not exist and cannot be updated.",
                    )
                )
                rejected_requests = True

            # Handle updating existing participants
            for datum in existing_records:
                family_id = datum["family_id"]
                return_data, result = update_metadata(
                    table_name="family",
                    identifier=family_id,
                    model_instance=families.get(family_id),
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
            identifier = datum.get("family_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class DeleteFamilyAPI(APIView):
    """
    API view to create or update Family entries.

    This API endpoint accepts a list of family data objects, validates
     them, and deletes them based on the 'family_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="delete_families",
        request_body=FamilySerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Family"],
    )

    def delete(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch families
        families = bulk_retrieve(
            model_class=Family,
            id_list=id_list,
            id_field="family_id"
        )
        try:
            for identifier in id_list:
                if identifier in families:
                    return_data, result = delete_metadata(
                        table_name="family",
                        identifier=identifier,
                        id_field="family_id"
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
                            data="Family not found"
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

class CreatePhenotypeAPI(APIView):
    """
    API view to create Phenotype entries.

    This API endpoint accepts a list of phenotype data objects, checks that
    the submission does not exist, and creates new entries based on the
    presence of a 'phenotype_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="create_phenotypes",
        request_body=PhenotypeSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successful",
            400: "Bad request",
        },
        tags=["Phenotype"],
    )

    def post(self, request):
        # Retrieve existing phenotypes in bulk
        phenotypes = bulk_model_retrieve(
            request_data=request.data,
            model_class=Phenotype,
            id="phenotype_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            phenotype_id = datum.get("phenotype_id")  # Safely retrieve phenotype_id
            if phenotype_id and phenotype_id in phenotypes:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Handle creating new phenotypes
            for datum in new_records:
                return_data, result = create_metadata(
                    table_name="phenotype",
                    identifier=datum["phenotype_id"],
                    datum=datum
                )
                response_data.append(return_data)
                if result == "accepted_request":
                    accepted_requests = True
                else:
                    rejected_requests = True

            # Handle updating existing phenotypes
            for datum in existing_records:
                response_data.append(
                    response_constructor(
                        identifier=datum["phenotype_id"],
                        request_status="BAD REQUEST",
                        code=400,
                        data="Phenotype already exists",
                    )
                )
                rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            identifier = datum.get("phenotype_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class ReadPhenotypeAPI(APIView):
    """
    API view to read Phenotype entries.

    This API endpoint requests a list of phenotype data objects based on the 'phenotype_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="read_phenotypes",
        operation_description="Retrieve phenotypes details by their IDs",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of phenotype IDs (e.g., F1, F2, F3)",
                type=openapi.TYPE_STRING,
            )
        ],

        responses={
            200: "All queries returned successfull",
            207: "Some queries were not successfull",
            400: "Bad request",
        },
        tags=["Phenotype"],
    )

    def get(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch phenotypes
        phenotypes = bulk_retrieve(
            model_class=Phenotype,
            id_list=id_list,
            id_field="phenotype_id"
        )

        try:
            for identifier in id_list:
                if identifier in phenotypes:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="SUCCESS",
                            code=200,
                            data=phenotypes[identifier]
                        )
                    )
                    accepted_requests = True
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            data="Phenotype not found"
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

class UpdatePhenotypeAPI(APIView):
    """
    API view to create or update Phenotype entries.

    This API endpoint accepts a list of phenotype data objects, validates
     them, and either creates new entries or updates existing ones based on
     the presence of a 'phenotype_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_phenotypes",
        request_body=PhenotypeSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Phenotype"],
    )

    def post(self, request):
        # Retrieve existing phenotypes in bulk
        phenotypes = bulk_model_retrieve(
            request_data=request.data,
            model_class=Phenotype,
            id="phenotype_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            phenotype_id = datum.get("phenotype_id")
            if phenotype_id and phenotype_id in phenotypes:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Reject non-existent records (Prevent updates to records that don't exist)
            for datum in new_records:
                response_data.append(
                    response_constructor(
                        identifier=datum.get("phenotype_id", "UNKNOWN"),
                        request_status="BAD REQUEST",
                        code=400,
                        data="Phenotype does not exist and cannot be updated.",
                    )
                )
                rejected_requests = True

            # Handle updating existing participants
            for datum in existing_records:
                phenotype_id = datum["phenotype_id"]
                return_data, result = update_metadata(
                    table_name="phenotype",
                    identifier=phenotype_id,
                    model_instance=phenotypes.get(phenotype_id),
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
            identifier = datum.get("phenotype_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class DeletePhenotypeAPI(APIView):
    """
    API view to create or update Phenotype entries.

    This API endpoint accepts a list of phenotype data objects, validates
     them, and deletes them based on the 'phenotype_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="delete_phenotypes",
        request_body=PhenotypeSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Phenotype"],
    )

    def delete(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch phenotypes
        phenotypes = bulk_retrieve(
            model_class=Phenotype,
            id_list=id_list,
            id_field="phenotype_id"
        )
        try:
            for identifier in id_list:
                if identifier in phenotypes:
                    return_data, result = delete_metadata(
                        table_name="phenotype",
                        identifier=identifier,
                        id_field="phenotype_id"
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
                            data="Phenotype not found"
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