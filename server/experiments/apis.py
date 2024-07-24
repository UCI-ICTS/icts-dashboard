#!/usr/bin/env python3
# experiments/apis.py

import json
from config.selectors import TableValidator, response_constructor, response_status
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
    get_experiment_dna_short_read,
    get_experiment_nanopore,
    get_experiment_pac_bio,
    get_experiment_rna,
    parse_nanopore,
    parse_rna,
    parse_nanopore_aligned,
    parse_pac_bio,
    parse_pac_bio_aligned,
    parse_rna_aligned,
    parse_short_read,
    parse_short_read_aligned,
)
from rest_framework import status, serializers

# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
                                status=(
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
                                status="BAD REQUEST",
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
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentShortReadApi(APIView):
    """Creating or Updating DNA Short Read Experiment

    API endpoint for creating or updating DNA short read experiment entries.

    This endpoint accepts multiple DNA short read experiment entries and attempts
    to create new records or update existing ones based on the provided experiment ID.
    It validates both the experiment data and the associated short read data against
    specified JSON schema to ensure data integrity before processing. If validation
    or processing fails for any record, detailed error information is returned.

    Attributes:
        post (request): Processes a list of DNA short read experiment data. Each entry
        is validated and then processed to either update an existing record or create a new one.
        The results for each entry are collected and returned in the response.

    Methods:
        post(request): Takes a request containing JSON data in the form of a list
        of experiment data entries. Each entry should include details about the experiment
        and the associated short read. Validates and processes each entry individually.

    Raises:
        Exception: Catches any exceptions during processing and returns an error status.

    Returns:
        Response: A response object containing the results for each submitted experiment
        entry, including success messages or details about any errors encountered.
    """

    @swagger_auto_schema(
        operation_id="create_short_read",
        request_body=ExperimentShortReadSerializer(many=True),
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
                identifier = datum["experiment_dna_short_read_id"]
                experiment_data = {
                    "experiment_id": "experiment_dna_short_read" + "." + identifier,
                    "table_name": "experiment_dna_short_read",
                    "id_in_table": identifier,
                    "participant_id": identifier.split("_")[0],
                }

                experiment_results = ExperimentService.validate_experiment(
                    experiment_data, validator
                )
                parsed_short_read = parse_short_read(short_read=datum)
                validator.validate_json(
                    json_object=parsed_short_read,
                    table_name="experiment_dna_short_read",
                )
                short_read_results = validator.get_validation_results()
                if (
                    short_read_results["valid"] is True
                    and experiment_results["valid"] is True
                ):
                    existing_short_read = get_experiment_dna_short_read(
                        experiment_dna_short_read_id=identifier
                    )
                    short_read_serializer = ExperimentShortReadSerializer(
                        existing_short_read, data=parsed_short_read
                    )
                    experiment_serializer = (
                        ExperimentService.create_or_update_experiment(experiment_data)
                    )
                    short_read_valid = short_read_serializer.is_valid()
                    experiment_valid = experiment_serializer.is_valid()
                    if experiment_valid and short_read_valid:
                        short_read_instance = short_read_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                status="UPDATED" if existing_short_read else "CREATED",
                                code=200 if existing_short_read else 201,
                                message=(
                                    f"Short read experiment {identifier} updated."
                                    if existing_short_read
                                    else f"Short read experiment {identifier} created."
                                ),
                                data=ExperimentShortReadSerializer(
                                    short_read_instance
                                ).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: short_read_serializer.errors[item]}
                            for item in short_read_serializer.errors
                        ]
                        error_data.extend(
                            {item: experiment_serializer.errors[item]}
                            for item in experiment_serializer.errors
                        )

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
                    errors = short_read_results["errors"] + experiment_results["errors"]
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
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
                                status=(
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
                                status="BAD REQUEST",
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
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentPacBio(APIView):
    """
    API view to create or update PacBio experiments.

    This view handles the POST request to create or update multiple PacBio experiments.
    It validates each experiment's data and constructs a response indicating the status
    of each operation.

    Args:
        request (Request): The request object containing the data to process.

    Returns:
        Response: The response object containing the status and data of the operations.
    """

    @swagger_auto_schema(
        operation_id="create_pac_bio",
        request_body=ExperimentPacBioSerializer(many=True),
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
                identifier = datum["experiment_pac_bio_id"]
                experiment_data = {
                    "experiment_id": "experiment_pac_bio" + "." + identifier,
                    "table_name": "experiment_pac_bio",
                    "id_in_table": identifier,
                    "participant_id": identifier.split("_")[0],
                }
                experiment_results = ExperimentService.validate_experiment(
                    experiment_data, validator
                )
                parsed_pac_bio = parse_pac_bio(pac_bio_datum=datum)
                validator.validate_json(
                    json_object=parsed_pac_bio, table_name="experiment_pac_bio"
                )
                pac_bio_results = validator.get_validation_results()
                if (
                    pac_bio_results["valid"] is True
                    and experiment_results["valid"] is True
                ):
                    existing_pac_bio = get_experiment_pac_bio(
                        experiment_pac_bio_id=identifier
                    )
                    pac_bio_serializer = ExperimentPacBioSerializer(
                        existing_pac_bio, data=parsed_pac_bio
                    )
                    experiment_serializer = (
                        ExperimentService.create_or_update_experiment(experiment_data)
                    )
                    pac_bio_valid = pac_bio_serializer.is_valid()
                    experiment_valid = experiment_serializer.is_valid()
                    if experiment_valid and pac_bio_valid:
                        pac_bio_instance = pac_bio_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                status="UPDATED" if existing_pac_bio else "CREATED",
                                code=200 if existing_pac_bio else 201,
                                message=(
                                    f"PacBio experiment {identifier} updated."
                                    if existing_pac_bio
                                    else f"PacBio experiment {identifier} created."
                                ),
                                data=ExperimentPacBioSerializer(pac_bio_instance).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: pac_bio_serializer.errors[item]}
                            for item in pac_bio_serializer.errors
                        ]
                        error_data.extend(
                            {item: experiment_serializer.errors[item]}
                            for item in experiment_serializer.errors
                        )

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
                    errors = pac_bio_results["errors"] + experiment_results["errors"]
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
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
                                status=(
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
                                status="BAD REQUEST",
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
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentNanopore(APIView):
    """API view to create or update Nanopore experiments.

    This view handles the POST request to create or update multiple Nanopore experiments.
    It validates each experiment's data and constructs a response indicating the status
    of each operation.

    Args:
        request (Request): The request object containing the data to process.

    Returns:
        Response: The response object containing the status and data of the operations.
    """

    @swagger_auto_schema(
        operation_id="create_nanopoer",
        request_body=ExperimentNanoporeSerializer(many=True),
        responses={
            200: "All submissions of Nanopore experiments were successfull",
            207: "Some submissions of Nanopore experiments were not successful.",
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
                identifier = datum["experiment_nanopore_id"]
                experiment_data = {
                    "experiment_id": "experiment_nanopore" + "." + identifier,
                    "table_name": "experiment_nanopore",
                    "id_in_table": identifier,
                    "participant_id": identifier.split("_")[0],
                }
                experiment_results = ExperimentService.validate_experiment(
                    experiment_data, validator
                )
                parsed_nanopore = parse_nanopore(nanopore=datum)
                validator.validate_json(
                    json_object=parsed_nanopore, table_name="experiment_nanopore"
                )
                nanopore_results = validator.get_validation_results()

                if (
                    nanopore_results["valid"] is True
                    and experiment_results["valid"] is True
                ):
                    existing_nanopore = get_experiment_nanopore(
                        experiment_nanopore_id=identifier
                    )
                    nanopore_serializer = ExperimentNanoporeSerializer(
                        existing_nanopore, data=parsed_nanopore
                    )
                    experiment_serializer = (
                        ExperimentService.create_or_update_experiment(experiment_data)
                    )
                    nanopore_valid = nanopore_serializer.is_valid()
                    experiment_valid = experiment_serializer.is_valid()
                    if experiment_valid and nanopore_valid:
                        nanopore_instance = nanopore_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                status="UPDATED" if existing_nanopore else "CREATED",
                                code=200 if existing_nanopore else 201,
                                message=(
                                    f"Nanopore experiment {identifier} updated."
                                    if existing_nanopore
                                    else f"Nanopore experiment {identifier} created."
                                ),
                                data=ExperimentNanoporeSerializer(
                                    nanopore_instance
                                ).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: nanopore_serializer.errors[item]}
                            for item in nanopore_serializer.errors
                        ]
                        error_data.extend(
                            {item: experiment_serializer.errors[item]}
                            for item in experiment_serializer.errors
                        )

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
                    errors = nanopore_results["errors"] + experiment_results["errors"]
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
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
                                status=(
                                    "UPDATED"
                                    if existing_aligned_rna
                                    else "CREATED"
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
                                status="BAD REQUEST",
                                code=400,
                                data=error_data,
                            )
                        )
                        rejected_requests = True
                        continue

                else:
                    errors = (
                        rna_aligned_results["errors"] + aligned_results["errors"]
                    )
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CreateOrUpdateExperimentRna(APIView):
    """API view to create or update short read RNA experiments.

    This view handles the POST request to create or update multiple short read RNA experiments.
    It validates each experiment's data and constructs a response indicating the status
    of each operation.

    Args:
        request (Request): The request object containing the data to process.

    Returns:
        Response: The response object containing the status and data of the operations.
    """

    @swagger_auto_schema(
        operation_id="create_short_rna",
        request_body=ExperimentRnaSerializer(many=True),
        responses={
            200: "All submissions of RNA experiments were successfull",
            207: "Some submissions of RNA experiments were not successful.",
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
                identifier = datum["experiment_rna_short_read_id"]
                parsed_rna, experiment_data = parse_rna(rna_datum=datum)
                experiment_results = ExperimentService.validate_experiment(
                    experiment_data, validator
                )
                validator.validate_json(
                    json_object=parsed_rna, table_name="experiment_rna_short_read"
                )
                rna_results = validator.get_validation_results()

                if (
                    rna_results["valid"] is True
                    and experiment_results["valid"] is True
                ):
                    existing_rna = get_experiment_rna(
                        experiment_rna=identifier
                    )
                    rna_serializer = ExperimentRnaSerializer(
                        existing_rna, data=parsed_rna
                    )
                    experiment_serializer = (
                        ExperimentService.create_or_update_experiment(experiment_data)
                    )
                    rna_valid = rna_serializer.is_valid()
                    experiment_valid = experiment_serializer.is_valid()
                    if experiment_valid and rna_valid:
                        rna_instance = rna_serializer.save()
                        response_data.append(
                            response_constructor(
                                identifier=identifier,
                                status="UPDATED" if existing_rna else "CREATED",
                                code=200 if existing_rna else 201,
                                message=(
                                    f"Short read RNA experiment {identifier} updated."
                                    if existing_rna
                                    else f"Short read RNA experiment {identifier} created."
                                ),
                                data=ExperimentRnaSerializer(
                                    rna_instance
                                ).data,
                            )
                        )
                        accepted_requests = True

                    else:
                        error_data = [
                            {item: rna_serializer.errors[item]}
                            for item in rna_serializer.errors
                        ]
                        error_data.extend(
                            {item: experiment_serializer.errors[item]}
                            for item in experiment_serializer.errors
                        )

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
                    errors = rna_results["errors"] + experiment_results["errors"]
                    response_data.append(
                        response_constructor(
                            identifier=identifier,
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
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
                                status="UPDATED" if existing_experiment else "CREATED",
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
                                status="BAD REQUEST",
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
                            status="BAD REQUEST",
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
                    identifier=identifier, status="ERROR", code=500, message=str(error)
                ),
            )
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
