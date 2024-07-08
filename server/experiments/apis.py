import json
from config.selectors import TableValidator, response_constructor, response_status
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from experiments.services import ExperimentSerializer, ExperimentShortReadSerializer
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
                datum = parse_short_read(short_read=datum)
                validator.validate_json(
                    json_object=datum, table_name="experiment_dna_short_read"
                )
                results = validator.get_validation_results()
                if results["valid"] is True:
                    existing_experiment = get_experiment_dna_short_read(experiment_dna_short_read_id=identifier)
                    serializer = ExperimentShortReadSerializer(
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
                                    f"Short read experiment {identifier} updated."
                                    if existing_experiment
                                    else f"Short read experiment {identifier} created."
                                ),
                                data=(experiment_instance).data,
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
