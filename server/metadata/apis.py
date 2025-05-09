#!/usr/bin/env python
# metadata/apis.py

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
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
    Analyte,
    Family,
    GeneticFindings,
    Phenotype,
    Biobank,
    ExperimentStage
)

from metadata.services import (
    AnalyteSerializer,
    GeneticFindingsSerializer,
    ParticipantInputSerializer,
    FamilySerializer,
    PhenotypeSerializer,
    BiobankSerializer,
    ExperimentStageSerializer,
    create_metadata,
    update_metadata,
    delete_metadata
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

            # Handle updating existing families
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

class CreateAnalyteAPI(APIView):
    """
    API view to create Analyte entries.

    This API endpoint accepts a list of analyte data objects, checks that
    the submission does not exist, and creates new entries based on the
    presence of a 'analyte_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="create_analytes",
        request_body=AnalyteSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successful",
            400: "Bad request",
        },
        tags=["Analyte"],
    )

    def post(self, request):
        # Retrieve existing analytes in bulk
        analytes = bulk_model_retrieve(
            request_data=request.data,
            model_class=Analyte,
            id="analyte_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            analyte_id = datum.get("analyte_id")  # Safely retrieve analyte_id
            if analyte_id and analyte_id in analytes:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Handle creating new analytes
            for datum in new_records:
                return_data, result = create_metadata(
                    table_name="analyte",
                    identifier=datum["analyte_id"],
                    datum=datum
                )
                response_data.append(return_data)
                if result == "accepted_request":
                    accepted_requests = True
                else:
                    rejected_requests = True

            # Handle updating existing analytes
            for datum in existing_records:
                response_data.append(
                    response_constructor(
                        identifier=datum["analyte_id"],
                        request_status="BAD REQUEST",
                        code=400,
                        data="Analyte already exists",
                    )
                )
                rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            identifier = datum.get("analyte_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class ReadAnalyteAPI(APIView):
    """
    API view to read Analyte entries.

    This API endpoint requests a list of analyte data objects based on the 'analyte_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="read_analytes",
        operation_description="Retrieve analyte details by their IDs",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of analyte IDs (e.g., A1, A2, A3)",
                type=openapi.TYPE_STRING,
            )
        ],

        responses={
            200: "All queries returned successfull",
            207: "Some queries were not successfull",
            400: "Bad request",
        },
        tags=["Analyte"],
    )

    def get(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch analytes
        analytes = bulk_retrieve(
            model_class=Analyte,
            id_list=id_list,
            id_field="analyte_id"
        )

        try:
            for identifier in id_list:
                if identifier in analytes:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="SUCCESS",
                            code=200,
                            data=analytes[identifier]
                        )
                    )
                    accepted_requests = True
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            data="Analyte not found"
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

class UpdateAnalyteAPI(APIView):
    """
    API view to create or update Analyte entries.

    This API endpoint accepts a list of analyte data objects, validates
     them, and either creates new entries or updates existing ones based on
     the presence of a 'analyte_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_analytes",
        request_body=AnalyteSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Analyte"],
    )

    def post(self, request):
        # Retrieve existing analytes in bulk
        analytes = bulk_model_retrieve(
            request_data=request.data,
            model_class=Analyte,
            id="analyte_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            analyte_id = datum.get("analyte_id")
            if analyte_id and analyte_id in analytes:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Reject non-existent records (Prevent updates to records that don't exist)
            for datum in new_records:
                response_data.append(
                    response_constructor(
                        identifier=datum.get("analyte_id", "UNKNOWN"),
                        request_status="BAD REQUEST",
                        code=400,
                        data="Analyte does not exist and cannot be updated.",
                    )
                )
                rejected_requests = True

            # Handle updating existing analytes
            for datum in existing_records:
                analyte_id = datum["analyte_id"]
                return_data, result = update_metadata(
                    table_name="analyte",
                    identifier=analyte_id,
                    model_instance=analytes.get(analyte_id),
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
            identifier = datum.get("analyte_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class DeleteAnalyteAPI(APIView):
    """
    API view to create or update Analyte entries.

    This API endpoint accepts a list of analyte data objects, validates
     them, and deletes them based on the 'analyte_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="delete_analytes",
        request_body=AnalyteSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Analyte"],
    )

    def delete(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch analytes
        analytes = bulk_retrieve(
            model_class=Analyte,
            id_list=id_list,
            id_field="analyte_id"
        )
        try:
            for identifier in id_list:
                if identifier in analytes:
                    return_data, result = delete_metadata(
                        table_name="analyte",
                        identifier=identifier,
                        id_field="analyte_id"
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
                            data="Analyte not found"
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
        operation_description="Retrieve phenotype details by their IDs",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of phenotype IDs (e.g., P1, P2, P3)",
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

            # Handle updating existing phenotypes
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


class CreateGeneticFindingsAPI(APIView):
    """
    API view to create Genetic Findings entries.

    This API endpoint accepts a list of genetic findings data objects, checks that
    the submission does not exist, and creates new entries based on the
    presence of a 'genetic_findings_id'.
    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="create_genetic_findings",
        request_body=GeneticFindingsSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successful",
            400: "Bad request",
        },
        tags=["Genetic Findings"],
    )

    def post(self, request):
        # Retrieve existing genetic findings in bulk
        genetic_findings = bulk_model_retrieve(
            request_data=request.data,
            model_class=GeneticFindings,
            id="genetic_findings_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            genetic_findings_id = datum.get("genetic_findings_id")  # Safely retrieve genetic_findings_id
            if genetic_findings_id and genetic_findings_id in genetic_findings:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Handle creating new genetic findings
            for datum in new_records:
                return_data, result = create_metadata(
                    table_name="genetic_findings",
                    identifier=datum["genetic_findings_id"],
                    datum=datum
                )
                response_data.append(return_data)
                if result == "accepted_request":
                    accepted_requests = True
                else:
                    rejected_requests = True

            # Handle updating existing genetic findings
            for datum in existing_records:
                response_data.append(
                    response_constructor(
                        identifier=datum["genetic_findings_id"],
                        request_status="BAD REQUEST",
                        code=400,
                        data="Genetic Findings already exists",
                    )
                )
                rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            identifier = datum.get("genetic_findings_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class ReadGeneticFindingsAPI(APIView):
    """
    API view to read Genetic Findings entries.

    This API endpoint requests a list of genetic findings data objects based on the 'genetic_findings_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="read_genetic_findings",
        operation_description="Retrieve genetic findings details by their IDs",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of genetic findings IDs (e.g., F1, F2, F3)",
                type=openapi.TYPE_STRING,
            )
        ],

        responses={
            200: "All queries returned successfull",
            207: "Some queries were not successfull",
            400: "Bad request",
        },
        tags=["Genetic Findings"],
    )

    def get(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch genetic_findings
        genetic_findings = bulk_retrieve(
            model_class=GeneticFindings,
            id_list=id_list,
            id_field="genetic_findings_id"
        )

        try:
            for identifier in id_list:
                if identifier in genetic_findings:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="SUCCESS",
                            code=200,
                            data=genetic_findings[identifier]
                        )
                    )
                    accepted_requests = True
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            data="Genetic Findings not found"
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

class UpdateGeneticFindingsAPI(APIView):
    """
    API view to create or update Genetic Findings entries.

    This API endpoint accepts a list of genetic_findings data objects, validates
     them, and either creates new entries or updates existing ones based on
     the presence of a 'genetic_findings_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_genetic_findings",
        request_body=GeneticFindingsSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Genetic Findings"],
    )

    def post(self, request):
        # Retrieve existing genetic findings in bulk
        genetic_findings = bulk_model_retrieve(
            request_data=request.data,
            model_class=GeneticFindings,
            id="genetic_findings_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            genetic_findings_id = datum.get("genetic_findings_id")
            if genetic_findings_id and genetic_findings_id in genetic_findings:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Reject non-existent records (Prevent updates to records that don't exist)
            for datum in new_records:
                response_data.append(
                    response_constructor(
                        identifier=datum.get("genetic_findings_id", "UNKNOWN"),
                        request_status="BAD REQUEST",
                        code=400,
                        data="Genetic Findings does not exist and cannot be updated.",
                    )
                )
                rejected_requests = True

            # Handle updating existing participants
            for datum in existing_records:
                genetic_findings_id = datum["genetic_findings_id"]
                return_data, result = update_metadata(
                    table_name="genetic_findings",
                    identifier=genetic_findings_id,
                    model_instance=genetic_findings.get(genetic_findings_id),
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
            identifier = datum.get("genetic_findings_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)

class DeleteGeneticFindingsAPI(APIView):
    """
    API view to create or update Genetic Findings entries.

    This API endpoint accepts a list of genetic findings data objects, validates
     them, and deletes them based on the 'genetic_findings_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="delete_genetic_findings",
        request_body=GeneticFindingsSerializer(many=True),
        responses={
            200: "All updates successfull",
            207: "Some updates were not successfull",
            400: "Bad request",
        },
        tags=["Genetic Findings"],
    )

    def delete(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = request.GET.get("ids", "").split(",")

        # Fetch genetic findings
        genetic_findings = bulk_retrieve(
            model_class=GeneticFindings,
            id_list=id_list,
            id_field="genetic_findings_id"
        )
        try:
            for identifier in id_list:
                if identifier in genetic_findings:
                    return_data, result = delete_metadata(
                        table_name="genetic_findings",
                        identifier=identifier,
                        id_field="genetic_findings_id"
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
                            data="Genetic Findings not found"
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


class BiobankViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=BiobankSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["Biobank"]
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_biobank(self, request):
        biobank = bulk_model_retrieve(request.data, Biobank, "biobank_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            biobank_id = datum.get("biobank_id")
            if biobank_id and biobank_id in biobank:
                response_data.append(response_constructor(
                    identifier=biobank_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Biobank entry already exists"
                ))
                rejected = True
            else:
                data, result = create_metadata("biobank", biobank_id, datum)
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "ids", openapi.IN_QUERY, description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["Biobank"]
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        biobank = bulk_retrieve(Biobank, ids, "biobank_id")
        response_data, accepted, rejected = [], False, False

        for biobank_id in ids:
            if biobank_id in biobank:
                response_data.append(response_constructor(
                    identifier=biobank_id,
                    request_status="SUCCESS",
                    code=200,
                    data=biobank[biobank_id]
                ))
                accepted = True
            else:
                response_data.append(response_constructor(
                    identifier=biobank_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=BiobankSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["Biobank"]
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_biobank(self, request):
        biobank = bulk_model_retrieve(request.data, Biobank, "biobank_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            biobank_id = datum.get("biobank_id")
            if biobank_id not in biobank:
                response_data.append(response_constructor(
                    identifier=biobank_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Entry does not exist"
                ))
                rejected = True
            else:
                data, result = update_metadata(
                    "biobank", biobank_id, biobank[biobank_id], datum
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_biobank_entries",
        operation_description="Bulk delete Biobank entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of Biobank IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["Biobank"]
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete Biobank entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        biobank = bulk_retrieve(Biobank, ids, "biobank_id")
        response_data, accepted, rejected = [], False, False

        for biobank_id in ids:
            if biobank_id in biobank:
                data, result = delete_metadata("biobank", biobank_id, "biobank_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(response_constructor(
                    identifier=biobank_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class ExperimentStageViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ExperimentStageSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentStage"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_experiment_stage(self, request):
        experiment_stage = bulk_model_retrieve(request.data, ExperimentStage, "experiment_stage_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_stage_id = datum.get("experiment_stage_id")
            if experiment_stage_id and experiment_stage_id in experiment_stage:
                response_data.append(
                    response_constructor(
                        identifier=experiment_stage_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="ExperimentStage entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_metadata("experiment_stage", experiment_stage_id, datum)
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentStage"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        experiment_stage = bulk_retrieve(ExperimentStage, ids, "experiment_stage_id")
        response_data, accepted, rejected = [], False, False

        for experiment_stage_id in ids:
            if experiment_stage_id in experiment_stage:
                response_data.append(
                    response_constructor(
                        identifier=experiment_stage_id,
                        request_status="SUCCESS",
                        code=200,
                        data=experiment_stage[experiment_stage_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_stage_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=ExperimentStageSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentStage"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_experiment_stage(self, request):
        experiment_stage = bulk_model_retrieve(request.data, ExperimentStage, "experiment_stage_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_stage_id = datum.get("experiment_stage_id")
            if experiment_stage_id not in experiment_stage:
                response_data.append(
                    response_constructor(
                        identifier=experiment_stage_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_metadata(
                    "experiment_stage", experiment_stage_id, experiment_stage[experiment_stage_id], datum
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_experiment_stage_entries",
        operation_description="Bulk delete ExperimentStage entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of ExperimentStage IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["ExperimentStage"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete ExperimentStage entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        experiment_stage = bulk_retrieve(ExperimentStage, ids, "experiment_stage_id")
        response_data, accepted, rejected = [], False, False

        for experiment_stage_id in ids:
            if experiment_stage_id in experiment_stage:
                data, result = delete_metadata("experiment_stage", experiment_stage_id, "experiment_stage_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_stage_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))