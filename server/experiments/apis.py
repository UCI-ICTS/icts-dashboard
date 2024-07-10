import json
from config.selectors import TableValidator, response_constructor, response_status
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from experiments.services import ExperimentSerializer, ExperimentShortReadSerializer, ExperimentService
from experiments.selectors import get_experiment, get_experiment_dna_short_read, parse_short_read
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class CreateOrUpdateExperimentShortReadApi(APIView):
    """"""

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
                    "participant_id": identifier.split("_")[0]
                }
                
                experiment_results = experiment_results = ExperimentService.validate_experiment(experiment_data, validator)
                parsed_short_read = parse_short_read(short_read=datum)
                validator.validate_json(
                    json_object=parsed_short_read, table_name="experiment_dna_short_read"
                )
                short_read_results = validator.get_validation_results()
                if short_read_results["valid"] is True and experiment_results["valid"] is True:
                    existing_short_read = get_experiment_dna_short_read(experiment_dna_short_read_id=identifier)
                    short_read_serializer = ExperimentShortReadSerializer(
                        existing_short_read, data=parsed_short_read
                    )
                    experiment_serializer = ExperimentService.create_or_update_experiment(experiment_data)
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
                                data=ExperimentShortReadSerializer(short_read_instance).data,
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
                validator.validate_json(
                    json_object=datum, table_name="experiment"
                )
                results = validator.get_validation_results()
                if results["valid"] is True:
                    existing_experiment = get_experiment(experiment_id=identifier)
                    serializer = ExperimentSerializer(
                        existing_experiment, data=datum
                    )

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
