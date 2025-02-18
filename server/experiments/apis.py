#!/usr/bin/env python3
# experiments/apis.py

from config.selectors import TableValidator, response_constructor, response_status
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.selectors import bulk_retrieve

from experiments.models import (
    Aligned,
    AlignedRNAShortRead,
    AlignedPacBio,
    AlignedDNAShortRead,
    AlignedNanopore,
    Experiment,
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
    AlignedService,
    ExperimentSerializer,
    ExperimentShortReadSerializer,
    ExperimentNanoporeSerializer,
    ExperimentPacBioSerializer,
    ExperimentRnaSerializer,
    create_or_update_experiment,
    create_or_update_alignment
)
from experiments.selectors import (
    get_aligned_pac_bio,
    get_experiment,
    parse_pac_bio_aligned,
)


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
        aligned_dna_short_read = bulk_retrieve(
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
        dna_short_read = bulk_retrieve(
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

        This API endpoint accepts a list of short read RNA experiment entries, 
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
        aligned_pac_bio = bulk_retrieve(
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
        experiment_pac_bio = bulk_retrieve(
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
            200: "All submissions of RNA short read experiments were successfull",
            207: "Some submissions of RNA short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        aligned_nanopore = bulk_retrieve(
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
        dna_short_read = bulk_retrieve(
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
        aligned_rna = bulk_retrieve(
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
        request_body=ExperimentRnaSerializer(many=True),
        responses={
            200: "All submissions of RNA short read experiments were successfull",
            207: "Some submissions of RNA short read experiments were not successful.",
            400: "Bad request",
        },
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        rna_short_read = bulk_retrieve(
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
