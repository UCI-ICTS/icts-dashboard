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

from search.selectors import create_or_update

from experiments.models import (
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
    ExperimentService,
)
from experiments.selectors import (
    get_aligned_pac_bio,
    get_aligned_dna_short_read,
    get_aligned_nanopore,
    get_aligned_rna,
    get_experiment,
    parse_nanopore_aligned,
    parse_pac_bio_aligned,
    parse_rna_aligned,
    parse_short_read_aligned,
)


class CreateOrUpdateAlignedShortRead(APIView):
    """Create or Update Aligned DNA Short Read Records

    API view to create or update aligned DNA short read records.

    This view handles the submission of one or more aligned DNA short read entries,
    performing validation and either creating new records or updating existing ones.
    It integrates detailed validation and response formatting to ensure data integrity
    and provide clear feedback to the client.

    Iterates over the provided data, validating and processing each aligned DNA short read.
    Valid entries are either updated or created in the database, and responses are
    compiled to provide detailed feedback on the outcome of each entry.

    Args:
        request (Request): The request object containing the aligned DNA short read data.

    Returns:
        Response: A Response object containing the status code and a list of results for
        each processed entry indicating whether it was successfully created or updated,
        or if there were any errors.
    """

    @swagger_auto_schema(
        operation_id="create_aligned_short_read",
        request_body=AlignedDNAShortReadSerializer(many=True),
        responses={
            200: "All submissions of aligned DNA short read were successfull",
            207: "Some submissions of aligned DNA short read were not successful.",
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
                identifier = datum["aligned_dna_short_read_id"]
                aligned_data = {
                    "aligned_id": "aligned_dna_short_read" + "." + identifier,
                    "table_name": "aligned_dna_short_read",
                    "id_in_table": identifier,
                    "participant_id": identifier.split("_")[0],
                    "aligned_file": datum["aligned_dna_short_read_file"],
                    "aligned_index_file": datum["aligned_dna_short_read_index_file"],
                }

                aligned_results = AlignedService.validate_aligned(
                    aligned_data, validator
                )
                parsed_short_read_aligned = parse_short_read_aligned(
                    short_read_aligned=datum
                )
                validator.validate_json(
                    json_object=parsed_short_read_aligned,
                    table_name="aligned_dna_short_read",
                )
                short_read_aligned_results = validator.get_validation_results()
                if (
                    short_read_aligned_results["valid"] is True
                    and aligned_results["valid"] is True
                ):
                    existing_aligned_short_read = get_aligned_dna_short_read(
                        aligned_dna_short_read_id=identifier
                    )
                    aligned_short_read_serializer = AlignedDNAShortReadSerializer(
                        existing_aligned_short_read, data=parsed_short_read_aligned
                    )
                    aligned_short_read_valid = aligned_short_read_serializer.is_valid()
                    aligned_serializer = AlignedService.create_or_update_aligned(
                        aligned_data
                    )
                    aligned_valid = aligned_serializer.is_valid()
                    if aligned_valid and aligned_short_read_valid:
                        short_read_instance = aligned_short_read_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                request_status=(
                                    "UPDATED"
                                    if existing_aligned_short_read
                                    else "CREATED"
                                ),
                                code=200 if existing_aligned_short_read else 201,
                                message=(
                                    f"Short read alignement {identifier} updated."
                                    if existing_aligned_short_read
                                    else f"Short read alignement {identifier} created."
                                ),
                                data=AlignedDNAShortReadSerializer(
                                    short_read_instance
                                ).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: aligned_short_read_serializer.errors[item]}
                            for item in aligned_short_read_serializer.errors
                        ]
                        error_data.extend(
                            {item: aligned_serializer.errors[item]}
                            for item in aligned_serializer.errors
                        )

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
                    errors = (
                        short_read_aligned_results["errors"] + aligned_results["errors"]
                    )
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=errors,
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
                return_data, result = create_or_update(
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
            # import pdb; pdb.set_trace()
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

    API view to create or update aligned PacBio records.

    This view handles the submission of one or more PacBio entries,
    performing validation and either creating new records or updating existing ones.
    It integrates detailed validation and response formatting to ensure data integrity
    and provide clear feedback to the client.

    Iterates over the provided data, validating and processing each aligned DNA short read.
    Valid entries are either updated or created in the database, and responses are
    compiled to provide detailed feedback on the outcome of each entry.

    Args:
        request (Request): The request object containing the aligned DNA short read data.

    Returns:
        Response: A Response object containing the status code and a list of results for
        each processed entry indicating whether it was successfully created or updated,
        or if there were any errors.
    """

    @swagger_auto_schema(
        operation_id="create_aligned_pac_bio",
        request_body=AlignedPacBioSerializer(many=True),
        responses={
            200: "All submissions of aligned PacBio data were successfull",
            207: "Some submissions of aligned PacBio data were not successful.",
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
                identifier = datum["aligned_pac_bio_id"]
                aligned_data = {
                    "aligned_id": "aligned_pac_bio" + "." + identifier,
                    "table_name": "aligned_pac_bio",
                    "id_in_table": identifier,
                    "participant_id": identifier.split("_")[0],
                    "aligned_file": datum["aligned_pac_bio_file"],
                    "aligned_index_file": datum["aligned_pac_bio_index_file"],
                }

                aligned_results = AlignedService.validate_aligned(
                    aligned_data, validator
                )
                parsed_pac_bio_aligned = parse_pac_bio_aligned(pac_bio_aligned=datum)
                validator.validate_json(
                    json_object=parsed_pac_bio_aligned,
                    table_name="aligned_pac_bio",
                )
                pac_bio_aligned_results = validator.get_validation_results()
                if (
                    pac_bio_aligned_results["valid"] is True
                    and aligned_results["valid"] is True
                ):
                    existing_aligned_pac_bio = get_aligned_pac_bio(
                        aligned_pac_bio_id=identifier
                    )
                    aligned_pac_bio_serializer = AlignedPacBioSerializer(
                        existing_aligned_pac_bio, data=parsed_pac_bio_aligned
                    )
                    aligned_pac_bio_valid = aligned_pac_bio_serializer.is_valid()
                    aligned_serializer = AlignedService.create_or_update_aligned(
                        aligned_data
                    )
                    aligned_valid = aligned_serializer.is_valid()
                    if aligned_valid and aligned_pac_bio_valid:
                        pac_bio_instance = aligned_pac_bio_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status=(
                                    "UPDATED" if existing_aligned_pac_bio else "CREATED"
                                ),
                                code=200 if existing_aligned_pac_bio else 201,
                                message=(
                                    f"Short read alignement {identifier} updated."
                                    if existing_aligned_pac_bio
                                    else f"Short read alignement {identifier} created."
                                ),
                                data=AlignedPacBioSerializer(pac_bio_instance).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: aligned_pac_bio_serializer.errors[item]}
                            for item in aligned_pac_bio_serializer.errors
                        ]
                        error_data.extend(
                            {item: aligned_serializer.errors[item]}
                            for item in aligned_serializer.errors
                        )

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
                    errors = (
                        pac_bio_aligned_results["errors"] + aligned_results["errors"]
                    )
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=errors,
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
        operation_id="experiment_pac_bio",
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
        dna_short_read = bulk_retrieve(
            request_data=request.data,
            model_class=ExperimentPacBio,
            id="experiment_pac_bio_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                return_data, result = create_or_update(
                    table_name="experiment_pac_bio",
                    identifier = datum["experiment_pac_bio_id"],
                    model_instance = dna_short_read.get(datum["experiment_pac_bio_id"]),
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
            # import pdb; pdb.set_trace()
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

    API view to create or update aligned Nanopore records.

    This view handles the submission of one or more Nanopore entries,
    performing validation and either creating new records or updating existing ones.
    It integrates detailed validation and response formatting to ensure data integrity
    and provide clear feedback to the client.

    Iterates over the provided data, validating and processing each aligned DNA short read.
    Valid entries are either updated or created in the database, and responses are
    compiled to provide detailed feedback on the outcome of each entry.

    Args:
        request (Request): The request object containing the aligned DNA short read data.

    Returns:
        Response: A Response object containing the status code and a list of results for
        each processed entry indicating whether it was successfully created or updated,
        or if there were any errors.
    """

    @swagger_auto_schema(
        operation_id="create_aligned_nanopore",
        request_body=AlignedNanoporeSerializer(many=True),
        responses={
            200: "All submissions of aligned Nanopore data were successfull",
            207: "Some submissions of aligned Nanopore data were not successful.",
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
                identifier = datum["aligned_nanopore_id"]
                aligned_data = {
                    "aligned_id": "aligned_nanopore" + "." + identifier,
                    "table_name": "aligned_nanopore",
                    "id_in_table": identifier,
                    "participant_id": identifier.split("_")[0],
                    "aligned_file": datum["aligned_nanopore_file"],
                    "aligned_index_file": datum["aligned_nanopore_index_file"],
                }

                aligned_results = AlignedService.validate_aligned(
                    aligned_data, validator
                )
                parsed_nanopore_aligned = parse_nanopore_aligned(nanopore_aligned=datum)
                validator.validate_json(
                    json_object=parsed_nanopore_aligned,
                    table_name="aligned_nanopore",
                )
                nanopore_aligned_results = validator.get_validation_results()
                if (
                    nanopore_aligned_results["valid"] is True
                    and aligned_results["valid"] is True
                ):
                    existing_aligned_nanopore = get_aligned_nanopore(
                        aligned_nanopore_id=identifier
                    )

                    aligned_nanopore_serializer = AlignedNanoporeSerializer(
                        existing_aligned_nanopore, data=parsed_nanopore_aligned
                    )
                    aligned_pac_bio_valid = aligned_nanopore_serializer.is_valid()
                    aligned_serializer = AlignedService.create_or_update_aligned(
                        aligned_data
                    )
                    aligned_valid = aligned_serializer.is_valid()
                    if aligned_valid and aligned_pac_bio_valid:
                        nanpore_instance = aligned_nanopore_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status=(
                                    "UPDATED"
                                    if existing_aligned_nanopore
                                    else "CREATED"
                                ),
                                code=200 if existing_aligned_nanopore else 201,
                                message=(
                                    f"Nanopore alignement {identifier} updated."
                                    if existing_aligned_nanopore
                                    else f"Nanopore alignement {identifier} created."
                                ),
                                data=AlignedNanoporeSerializer(nanpore_instance).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: aligned_nanopore_serializer.errors[item]}
                            for item in aligned_nanopore_serializer.errors
                        ]
                        error_data.extend(
                            {item: aligned_serializer.errors[item]}
                            for item in aligned_serializer.errors
                        )

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
                    errors = (
                        nanopore_aligned_results["errors"] + aligned_results["errors"]
                    )
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=errors,
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
        operation_id="update_nanopore",
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
                return_data, result = create_or_update(
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
            # import pdb; pdb.set_trace()
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
    """Create or Update Aligned RNA

    API view to create or update aligned RNA records.

    This view handles the submission of one or more RNA entries,
    performing validation and either creating new records or updating existing ones.
    It integrates detailed validation and response formatting to ensure data integrity
    and provide clear feedback to the client.

    Iterates over the provided data, validating and processing each aligned DNA short read.
    Valid entries are either updated or created in the database, and responses are
    compiled to provide detailed feedback on the outcome of each entry.

    Args:
        request (Request): The request object containing the aligned RNA short read data.

    Returns:
        Response: A Response object containing the status code and a list of results for
        each processed entry indicating whether it was successfully created or updated,
        or if there were any errors.
    """

    @swagger_auto_schema(
        operation_id="create_aligned_rna",
        request_body=AlignedRnaSerializer(many=True),
        responses={
            200: "All submissions of aligned Nanopore data were successfull",
            207: "Some submissions of aligned Nanopore data were not successful.",
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
                identifier = datum["aligned_rna_short_read_id"]
                parsed_rna_aligned, aligned_data = parse_rna_aligned(rna_aligned=datum)
                aligned_results = AlignedService.validate_aligned(
                    aligned_data, validator
                )
                validator.validate_json(
                    json_object=parsed_rna_aligned,
                    table_name="aligned_rna_short_read",
                )
                rna_aligned_results = validator.get_validation_results()

                if (
                    rna_aligned_results["valid"] is True
                    and aligned_results["valid"] is True
                ):
                    existing_aligned_rna = get_aligned_rna(
                        aligned_rna_short_read_id=identifier
                    )

                    aligned_rna_serializer = AlignedRnaSerializer(
                        existing_aligned_rna, data=parsed_rna_aligned
                    )
                    aligned_rna_valid = aligned_rna_serializer.is_valid()
                    aligned_serializer = AlignedService.create_or_update_aligned(
                        aligned_data
                    )
                    aligned_valid = aligned_serializer.is_valid()
                    if aligned_valid and aligned_rna_valid:
                        rna_instance = aligned_rna_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                               request_status=(
                                    "UPDATED" if existing_aligned_rna else "CREATED"
                                ),
                                code=200 if existing_aligned_rna else 201,
                                message=(
                                    f"Nanopore alignement {identifier} updated."
                                    if existing_aligned_rna
                                    else f"Nanopore alignement {identifier} created."
                                ),
                                data=AlignedRnaSerializer(rna_instance).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: aligned_rna_serializer.errors[item]}
                            for item in aligned_rna_serializer.errors
                        ]
                        error_data.extend(
                            {item: aligned_serializer.errors[item]}
                            for item in aligned_serializer.errors
                        )

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
                    errors = rna_aligned_results["errors"] + aligned_results["errors"]
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                           request_status="BAD REQUEST",
                            code=400,
                            data=errors,
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
                return_data, result = create_or_update(
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
            # import pdb; pdb.set_trace()
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
