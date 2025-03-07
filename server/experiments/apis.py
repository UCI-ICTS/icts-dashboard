#!/usr/bin/env python3
# experiments/apis.py

from config.selectors import TableValidator, response_constructor, response_status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.selectors import bulk_model_retrieve, bulk_retrieve

from experiments.models import (
    AlignedRNAShortRead,
    AlignedPacBio,
    AlignedDNAShortRead,
    AlignedNanopore,
    ExperimentDNAShortRead,
    ExperimentNanopore,
    ExperimentPacBio,
    ExperimentRNAShortRead
)
from experiments.services import (
    AlignedDNAShortReadSerializer,
    AlignedNanoporeSerializer,
    AlignedPacBioSerializer,
    AlignedRnaSerializer,
    ExperimentSerializer,
    ExperimentShortReadSerializer,
    ExperimentNanoporeSerializer,
    ExperimentPacBioSerializer,
    ExperimentRnaInputSerializer,
    create_experiment,
    update_experiment,
    # delete_experiment,
    create_or_update_experiment,
    create_or_update_alignment
)
from experiments.selectors import get_experiment


class CreateOrUpdateAlignedShortRead(APIView):
    """Create or Update Aligned DNA Short Read Records

    This API endpoint accepts a list of short read RNA experiment entries, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'aligned_dna_short_read_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="submit_aligned_dna",
        request_body=AlignedDNAShortReadSerializer(many=True),
        responses={
            200: "All submissions of RNA short read experiments were successfull",
            207: "Some submissions of RNA short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        aligned_dna_short_read = bulk_model_retrieve(
            request_data=request.data,
            model_class=AlignedDNAShortRead,
            id="aligned_dna_short_read_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_alignment(
                    table_name="aligned_dna_short_read",
                    identifier = datum["aligned_dna_short_read_id"],
                    model_instance = aligned_dna_short_read.get(datum["aligned_dna_short_read_id"]),
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
                    identifier=datum["aligned_dna_short_read_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentShortReadApi(APIView):
    """API endpoint for creating or updating DNA short read experiment entries.

    This API endpoint accepts a list of DNA short read experiment entries, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'experiment_dna_short_read_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_dna_short_read",
        request_body=ExperimentShortReadSerializer(many=True),
        responses={
            200: "All submissions of DNA short read experiments were successfull",
            207: "Some submissions of DNA short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        dna_short_read = bulk_model_retrieve(
            request_data=request.data,
            model_class=ExperimentDNAShortRead,
            id="experiment_dna_short_read_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_experiment(
                    table_name="experiment_dna_short_read",
                    identifier = datum["experiment_dna_short_read_id"],
                    model_instance = dna_short_read.get(datum["experiment_dna_short_read_id"]),
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
                    identifier=datum["experiment_dna_short_read_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateAlignedPacBio(APIView):
    """Create or Update Aligned PacBio

        This API endpoint accepts a list of short read PacBio experiment entries, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'aligned_pac_bio_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="aligned_pac_bio",
        request_body=AlignedPacBioSerializer(many=True),
        responses={
            200: "All submissions of PacBio experiments were successfull",
            207: "Some submissions of PacBio experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        aligned_pac_bio = bulk_model_retrieve(
            request_data=request.data,
            model_class=AlignedPacBio,
            id="aligned_pac_bio_id"
        )

        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_alignment(
                    table_name="aligned_pac_bio",
                    identifier = datum["aligned_pac_bio_id"],
                    model_instance = aligned_pac_bio.get(datum["aligned_pac_bio_id"]),
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
                    identifier=datum["aligned_pac_bio_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentPacBio(APIView):
    """API view to create or update PacBio experiments.

    This API endpoint accepts a list of PacBio experiment entries, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'experiment_pac_bio_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="submit_experiment_pac_bio",
        request_body=ExperimentPacBioSerializer(many=True),
        responses={
            200: "All submissions of PacBio experiments were successfull",
            207: "Some submissions of PacBio experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        experiment_pac_bio = bulk_model_retrieve(
            request_data=request.data,
            model_class=ExperimentPacBio,
            id="experiment_pac_bio_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_experiment(
                    table_name="experiment_pac_bio",
                    identifier = datum["experiment_pac_bio_id"],
                    model_instance = experiment_pac_bio.get(datum["experiment_pac_bio_id"]),
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
                    identifier=datum["experiment_pac_bio_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateAlignedNanopore(APIView):
    """Create or Update Aligned Nanopore

    This API endpoint accepts a list of aligned NanoPore experiment entries, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'aligned_nanopore_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="submit_aligned_nanopore",
        request_body=AlignedNanoporeSerializer(many=True),
        responses={
            200: "All submissions of NanoPore short read experiments were successfull",
            207: "Some submissions of NanoPore short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        aligned_nanopore = bulk_model_retrieve(
            request_data=request.data,
            model_class=AlignedNanopore,
            id="aligned_nanopore_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_alignment(
                    table_name="aligned_nanopore",
                    identifier = datum["aligned_nanopore_id"],
                    model_instance = aligned_nanopore.get(datum["aligned_nanopore_id"]),
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
                    identifier=datum["aligned_nanopore_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentNanopore(APIView):
    """API view to create or update Nanopore experiments.

    This API endpoint accepts a list of Nanopore experiment entries, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'experiment_nanopore_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="submit_experiment_nanopore",
        request_body=ExperimentNanoporeSerializer(many=True),
        responses={
            200: "All submissions of Nanopore experiments were successfull",
            207: "Some submissions of Nanopore experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        dna_short_read = bulk_model_retrieve(
            request_data=request.data,
            model_class=ExperimentNanopore,
            id="experiment_nanopore_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_experiment(
                    table_name="experiment_nanopore",
                    identifier = datum["experiment_nanopore_id"],
                    model_instance = dna_short_read.get(datum["experiment_nanopore_id"]),
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
                    identifier=datum["experiment_nanopore_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateAlignedRna(APIView):
    """
    API view to create or update Aligned RNA entries.

    This API endpoint accepts a list of aligned RNA data objects, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'aligned_rna_short_read_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    @swagger_auto_schema(
        operation_id="submit_aligned_rna",
        request_body=AlignedRnaSerializer(many=True),
        responses={
            200: "All submissions of genetic findings were successfull",
            207: "Some submissions of genetic findings were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )
    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        aligned_rna = bulk_model_retrieve(
            request_data=request.data,
            model_class=AlignedRNAShortRead,
            id="aligned_rna_short_read_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_alignment(
                    table_name="aligned_rna_short_read",
                    identifier = datum["aligned_rna_short_read_id"],
                    model_instance = aligned_rna.get(datum["aligned_rna_short_read_id"]),
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
                    identifier=datum["aligned_rna_short_read_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateExperimentRnaShortRead(APIView):
    """API view to create short read RNA experiments.

    This API endpoint accepts a list of short read RNA experiment entries, 
    validates them, and creates new entries based on the presence of a 
    'experiment_dna_short_read_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="create_experiment_rna_short_read",
        request_body=ExperimentRnaInputSerializer(many=True),
        responses={
            200: "All submissions of RNA short read experiments were successfull",
            207: "Some submissions of RNA short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["ExperimentRnaShortRead"],
    )

    def post(self, request):
        experiment_rna_short_read = bulk_model_retrieve(
            request_data=request.data,
            model_class=ExperimentRNAShortRead,
            id="experiment_rna_short_read_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []
        for datum in request.data:
            experiment_rna_short_read_id = datum.get("experiment_rna_short_read_id")
            if experiment_rna_short_read_id and experiment_rna_short_read_id in experiment_rna_short_read:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Handle creating new participants
            for datum in new_records:
                return_data, result = create_experiment(
                    table_name="experiment_rna_short_read",
                    identifier=datum["experiment_rna_short_read_id"],
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
                        identifier=datum["experiment_rna_short_read_id"],
                        request_status="BAD REQUEST",
                        code=400,
                        data="RNA short read experiment already exists",
                    )
                )
                rejected_requests = True

            status_code = response_status(accepted_requests, rejected_requests)
            return Response(status=status_code, data=response_data)

        except Exception as error:
            identifier = datum.get("experiment_rna_short_read_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
        

class ReadExperimentRnaShortRead(APIView):
    """
    API view to read short read RNA experiments.

    This API endpoint requests a list of short read RNA experiment data 
    objects based on the 'experiment_rna_short_read_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="read_experiment_rna_short_read",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of short read RNA IDs (e.g., P1-0,P2-1,P3-0)",
                type=openapi.TYPE_STRING,
            )
        ],
        
        responses={
            200: "All queries returned successfull",
            207: "Some queries were not successfull",
            400: "Bad request",
        },
        tags=["ExperimentRnaShortRead"],
    )

    def get(self, request):
        response_data = []
        rejected_requests = False
        accepted_requests = False

        id_list = [id.strip() for id in request.GET.get("ids", "").split(",") if id.strip()]

        # Fetch participants
        experiment_rna_short_read = bulk_retrieve(
            model_class=ExperimentRNAShortRead,
            id_list=id_list,
            id_field="experiment_rna_short_read_id"
        )

        try:
            for identifier in id_list:
                if identifier in experiment_rna_short_read:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="SUCCESS",
                            code=200,
                            data=experiment_rna_short_read[identifier]
                        )
                    )
                    accepted_requests = True
                else:
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            request_status="NOT FOUND",
                            code=404,
                            data="Short read RNA experiment not found"
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


class UpdateExperimentRnaShortRead(APIView):
    """API view to update short read RNA experiments.

    This API endpoint accepts a list of short read RNA experiment entries, 
    validates them, and update existing entries based on the presence of 
    a 'experiment_dna_short_read_id'.

    Responses vary based on the results of the update:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_experiment_rna_short_read",
        request_body=ExperimentRnaInputSerializer(many=True),
        responses={
            200: "All updates of RNA short read experiments were successfull",
            207: "Some updates of RNA short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["ExperimentRnaShortRead"],
    )

    def post(self, request):
        # Retrieve existing participants in bulk
        experiment_rna_short_read = bulk_model_retrieve(
            request_data=request.data,
            model_class=ExperimentRNAShortRead,
            id="experiment_rna_short_read_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        new_records = []
        existing_records = []

        # Split request data into new and existing records
        for datum in request.data:
            experiment_rna_short_read_id = datum.get("experiment_rna_short_read_id")  
            if experiment_rna_short_read_id and experiment_rna_short_read_id \
                in experiment_rna_short_read:
                existing_records.append(datum)
            else:
                new_records.append(datum)

        try:
            # Reject non-existent records (Prevent updates to records that don't exist)
            for datum in new_records:
                response_data.append(
                    response_constructor(
                        identifier=datum.get("experiment_rna_short_read_id", "UNKNOWN"),
                        request_status="BAD REQUEST",
                        code=400,
                        data="Short Read RNA experiment does not exist and cannot be updated.",
                    )
                )
                rejected_requests = True

            # Handle updating existing participants
            for datum in existing_records:
                participant_id = datum["experiment_rna_short_read_id"]
                return_data, result = update_experiment(
                    table_name="experiment_rna_short_read",
                    identifier=participant_id,
                    model_instance=experiment_rna_short_read.get(participant_id),
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
            identifier = datum.get("experiment_rna_short_read_id", "UNKNOWN IDENTIFIER")
            response_data.insert(0, response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


# class DeleteExperimentRnaShortRead(APIView):
#     """
#     API view to delete short read RNA experiments.

#     This API endpoint delets a list of short read RNA experiments based on
#      the 'experiment_rna_short_read_id'.

#     Responses vary based on the results of the submissions:
#     - Returns HTTP 200 if all operations are successful.
#     - Returns HTTP 207 if some operations fail.
#     - Returns HTTP 400 for bad input formats or validation failures.
#     """

#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_id="delete_participants",
#         manual_parameters=[
#             openapi.Parameter(
#                 "ids",
#                 openapi.IN_QUERY,
#                 description="Comma-separated list of participant IDs (e.g., P1-0,P2-1,P3-0)",
#                 type=openapi.TYPE_STRING,
#             )
#         ],
        
#         responses={
#             200: "All queries successfully deleted",
#             207: "Some queries were not successfully deleted",
#             400: "Bad request",
#         },
#         tags=["ExperimentRnaShortRead"],
#     )

#     def delete(self, request):
#         response_data = []
#         rejected_requests = False
#         accepted_requests = False

#         id_list = [id.strip() for id in request.GET.get("ids", "").split(",") if id.strip()]

#         # Fetch participants
#         participants = bulk_retrieve(
#             model_class=ExperimentRNAShortRead,
#             id_list=id_list,
#             id_field="experiment_rna_short_read_id"
#         ) 
#         try:
#             for identifier in id_list:
#                 if identifier in participants:
#                     # return_data, result = delete_experiment(
#                     #     table_name="participant",
#                     #     identifier=identifier, 
#                     #     id_field="participant_id"
#                     # )
#                     response_data.append(return_data)

#                     if result == "accepted_request":
#                         accepted_requests = True
#                     else:
#                         rejected_requests = True
#                 else:
#                     response_data.append(
#                         response_constructor(
#                             identifier=identifier,
#                             request_status="NOT FOUND",
#                             code=404,
#                             data="Participant not found"
#                         )
#                     )
#                     rejected_requests = True

#             status_code = response_status(accepted_requests, rejected_requests)
#             return Response(status=status_code, data=response_data)

#         except Exception as error:
#             response_data.insert(0,
#                 response_constructor(
#                     identifier=id_list,
#                     request_status="SERVER ERROR",
#                     code=500,
#                     data=str(error),
#                 )
#             )
#             return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
        
        
class CreateOrUpdateExperimentRna(APIView):
    """API view to create or update short read RNA experiments.

    This API endpoint accepts a list of short read RNA experiment entries, 
    validates them, and either creates new entries or updates existing ones 
    based on the presence of a 'experiment_dna_short_read_id'.

    Responses vary based on the results of the submissions:
    - Returns HTTP 200 if all operations are successful.
    - Returns HTTP 207 if some operations fail.
    - Returns HTTP 400 for bad input formats or validation failures.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_rna_short_read",
        request_body=ExperimentRnaInputSerializer(many=True),
        responses={
            200: "All submissions of RNA short read experiments were successfull",
            207: "Some submissions of RNA short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        rna_short_read = bulk_model_retrieve(
            request_data=request.data,
            model_class=ExperimentRNAShortRead,
            id="experiment_rna_short_read_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update_experiment(
                    table_name="experiment_rna_short_read",
                    identifier = datum["experiment_rna_short_read_id"],
                    model_instance = rna_short_read.get(datum["experiment_rna_short_read_id"]),
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
                    identifier=datum["experiment_rna_short_read_id"],
                    request_status="SERVER ERROR",
                    code=500,
                    data=str(error),
                )
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentApi(APIView):
    """"""

    @swagger_auto_schema(
        operation_id="create_phenotype",
        request_body=ExperimentSerializer(many=True),
        responses={
            200: "All submissions of experiments were successfull",
            207: "Some submissions of experiments were not successful.",
            400: "Bad request",
        },
        tags=["Experiment"],
    )
    def post(self, request):
        validator = TableValidator()
        response_data = []
        rejected_requests = False
        accepted_requests = False
        try:
            for datum in request.data:
                identifier = datum["experiment_id"]
                # parsed_phenotype = parse_phenotype(phenotype=datum)
                validator.validate_json(json_object=datum, table_name="experiment")
                results = validator.get_validation_results()
                if results["valid"] is True:
                    existing_experiment = get_experiment(experiment_id=identifier)
                    serializer = ExperimentSerializer(existing_experiment, data=datum)

                    if serializer.is_valid():
                        experiment_instance = serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status="UPDATED" if existing_experiment else "CREATED",
                                code=201 if existing_experiment else 200,
                                message=(
                                    f"Phenotype {identifier} updated."
                                    if existing_experiment
                                    else f"Phenotype {identifier} created."
                                ),
                                data=ExperimentSerializer(experiment_instance).data,
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
