#!/usr/bin/env python
# metadata/apis.py

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from config.selectors import (
    TableValidator,
    response_constructor,
    response_status,
    remove_na,
)

from experiments.models import Experiment
from experiments.services import ExperimentSerializer

from config.selectors import bulk_retrieve, create_or_update

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
)
from metadata.selectors import (
    participant_parser,
    parse_geneti_findings,
    get_phenotype,
    get_analyte,
    get_genetic_findings,
)


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
            # time.sleep(5)
            return Response(status=status.HTTP_200_OK, data=serilized_return_data)
        except Exception as error:
            response_data.insert(0, str(error))
            return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)


class CrearteOrUpdateParticipantAPI(APIView):
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
        tags=["CreateOrUpdate"],
    )

    def post(self, request):
        # Most efficient query is to pull all ids from request at once
        participants = bulk_retrieve(
            request_data=request.data,
            model_class=Participant,
            id="participant_id"
        )
        
        response_data = []
        rejected_requests = False
        accepted_requests = False

        try:
            for index, datum in enumerate(request.data):
                datum = participant_parser(participant=datum)
                return_data, result = create_or_update(
                    table_name="participant",
                    identifier = datum["participant_id"],
                    model_instance = participants.get(datum["participant_id"]),
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
                    identifier=datum["participant_id"],
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
        operation_id="create_family",
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
        families = bulk_retrieve(
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
                return_data, result = create_or_update(
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
