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


class ParticipantViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ParticipantInputSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["Participant"]
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_participant(self, request):
        participant = bulk_model_retrieve(request.data, Participant, "participant_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            participant_id = datum.get("participant_id")
            if participant_id and participant_id in participant:
                response_data.append(response_constructor(
                    identifier=participant_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Participant entry already exists"
                ))
                rejected = True
            else:
                data, result = create_metadata("participant", participant_id, datum)
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
        tags=["Participant"]
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        participant = bulk_retrieve(Participant, ids, "participant_id")
        response_data, accepted, rejected = [], False, False

        for participant_id in ids:
            if participant_id in participant:
                response_data.append(response_constructor(
                    identifier=participant_id,
                    request_status="SUCCESS",
                    code=200,
                    data=participant[participant_id]
                ))
                accepted = True
            else:
                response_data.append(response_constructor(
                    identifier=participant_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=ParticipantInputSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["Participant"]
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_participant(self, request):
        participant = bulk_model_retrieve(request.data, Participant, "participant_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            participant_id = datum.get("participant_id")
            if participant_id not in participant:
                response_data.append(response_constructor(
                    identifier=participant_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Entry does not exist"
                ))
                rejected = True
            else:
                data, result = update_metadata(
                    "participant", participant_id, participant[participant_id], datum
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_participant_entries",
        operation_description="Bulk delete Participant entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of Participant IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["Participant"]
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete Participant entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        participant = bulk_retrieve(Participant, ids, "participant_id")
        response_data, accepted, rejected = [], False, False

        for participant_id in ids:
            if participant_id in participant:
                data, result = delete_metadata("participant", participant_id, "participant_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(response_constructor(
                    identifier=participant_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class FamilyViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=FamilySerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["Family"]
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_family(self, request):
        family = bulk_model_retrieve(request.data, Family, "family_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            family_id = datum.get("family_id")
            if family_id and family_id in family:
                response_data.append(response_constructor(
                    identifier=family_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Family entry already exists"
                ))
                rejected = True
            else:
                data, result = create_metadata("family", family_id, datum)
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
        tags=["Family"]
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        family = bulk_retrieve(Family, ids, "family_id")
        response_data, accepted, rejected = [], False, False

        for family_id in ids:
            if family_id in family:
                response_data.append(response_constructor(
                    identifier=family_id,
                    request_status="SUCCESS",
                    code=200,
                    data=family[family_id]
                ))
                accepted = True
            else:
                response_data.append(response_constructor(
                    identifier=family_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=FamilySerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["Family"]
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_family(self, request):
        family = bulk_model_retrieve(request.data, Family, "family_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            family_id = datum.get("family_id")
            if family_id not in family:
                response_data.append(response_constructor(
                    identifier=family_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Entry does not exist"
                ))
                rejected = True
            else:
                data, result = update_metadata(
                    "family", family_id, family[family_id], datum
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_family_entries",
        operation_description="Bulk delete Family entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of Family IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["Family"]
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete Family entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        family = bulk_retrieve(Family, ids, "family_id")
        response_data, accepted, rejected = [], False, False

        for family_id in ids:
            if family_id in family:
                data, result = delete_metadata("family", family_id, "family_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(response_constructor(
                    identifier=family_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class AnalyteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=AnalyteSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["Analyte"]
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_analyte(self, request):
        analyte = bulk_model_retrieve(request.data, Analyte, "analyte_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            analyte_id = datum.get("analyte_id")
            if analyte_id and analyte_id in analyte:
                response_data.append(response_constructor(
                    identifier=analyte_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Analyte entry already exists"
                ))
                rejected = True
            else:
                data, result = create_metadata("analyte", analyte_id, datum)
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
        tags=["Analyte"]
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        analyte = bulk_retrieve(Analyte, ids, "analyte_id")
        response_data, accepted, rejected = [], False, False

        for analyte_id in ids:
            if analyte_id in analyte:
                response_data.append(response_constructor(
                    identifier=analyte_id,
                    request_status="SUCCESS",
                    code=200,
                    data=analyte[analyte_id]
                ))
                accepted = True
            else:
                response_data.append(response_constructor(
                    identifier=analyte_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=AnalyteSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["Analyte"]
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_analyte(self, request):
        analyte = bulk_model_retrieve(request.data, Analyte, "analyte_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            analyte_id = datum.get("analyte_id")
            if analyte_id not in analyte:
                response_data.append(response_constructor(
                    identifier=analyte_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Entry does not exist"
                ))
                rejected = True
            else:
                data, result = update_metadata(
                    "analyte", analyte_id, analyte[analyte_id], datum
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_analyte_entries",
        operation_description="Bulk delete Analyte entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of Analyte IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["Analyte"]
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete Analyte entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        analyte = bulk_retrieve(Analyte, ids, "analyte_id")
        response_data, accepted, rejected = [], False, False

        for analyte_id in ids:
            if analyte_id in analyte:
                data, result = delete_metadata("analyte", analyte_id, "analyte_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(response_constructor(
                    identifier=analyte_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class PhenotypeViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PhenotypeSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["Phenotype"]
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_phenotype(self, request):
        phenotype = bulk_model_retrieve(request.data, Phenotype, "phenotype_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            phenotype_id = datum.get("phenotype_id")
            if phenotype_id and phenotype_id in phenotype:
                response_data.append(response_constructor(
                    identifier=phenotype_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Phenotype entry already exists"
                ))
                rejected = True
            else:
                data, result = create_metadata("phenotype", phenotype_id, datum)
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
        tags=["Phenotype"]
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        phenotype = bulk_retrieve(Phenotype, ids, "phenotype_id")
        response_data, accepted, rejected = [], False, False

        for phenotype_id in ids:
            if phenotype_id in phenotype:
                response_data.append(response_constructor(
                    identifier=phenotype_id,
                    request_status="SUCCESS",
                    code=200,
                    data=phenotype[phenotype_id]
                ))
                accepted = True
            else:
                response_data.append(response_constructor(
                    identifier=phenotype_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=PhenotypeSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["Phenotype"]
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_phenotype(self, request):
        phenotype = bulk_model_retrieve(request.data, Phenotype, "phenotype_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            phenotype_id = datum.get("phenotype_id")
            if phenotype_id not in phenotype:
                response_data.append(response_constructor(
                    identifier=phenotype_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Entry does not exist"
                ))
                rejected = True
            else:
                data, result = update_metadata(
                    "phenotype", phenotype_id, phenotype[phenotype_id], datum
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_phenotype_entries",
        operation_description="Bulk delete Phenotype entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of Phenotype IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["Phenotype"]
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete Phenotype entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        phenotype = bulk_retrieve(Phenotype, ids, "phenotype_id")
        response_data, accepted, rejected = [], False, False

        for phenotype_id in ids:
            if phenotype_id in phenotype:
                data, result = delete_metadata("phenotype", phenotype_id, "phenotype_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(response_constructor(
                    identifier=phenotype_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class GeneticFindingsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=GeneticFindingsSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["GeneticFindings"]
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_genetic_findings(self, request):
        genetic_findings = bulk_model_retrieve(request.data, GeneticFindings, "genetic_findings_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            genetic_findings_id = datum.get("genetic_findings_id")
            if genetic_findings_id and genetic_findings_id in genetic_findings:
                response_data.append(response_constructor(
                    identifier=genetic_findings_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="GeneticFindings entry already exists"
                ))
                rejected = True
            else:
                data, result = create_metadata("genetic_findings", genetic_findings_id, datum)
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
        tags=["GeneticFindings"]
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        genetic_findings = bulk_retrieve(GeneticFindings, ids, "genetic_findings_id")
        response_data, accepted, rejected = [], False, False

        for genetic_findings_id in ids:
            if genetic_findings_id in genetic_findings:
                response_data.append(response_constructor(
                    identifier=genetic_findings_id,
                    request_status="SUCCESS",
                    code=200,
                    data=genetic_findings[genetic_findings_id]
                ))
                accepted = True
            else:
                response_data.append(response_constructor(
                    identifier=genetic_findings_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=GeneticFindingsSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["GeneticFindings"]
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_genetic_findings(self, request):
        genetic_findings = bulk_model_retrieve(request.data, GeneticFindings, "genetic_findings_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            genetic_findings_id = datum.get("genetic_findings_id")
            if genetic_findings_id not in genetic_findings:
                response_data.append(response_constructor(
                    identifier=genetic_findings_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Entry does not exist"
                ))
                rejected = True
            else:
                data, result = update_metadata(
                    "genetic_findings", genetic_findings_id, genetic_findings[genetic_findings_id], datum
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_genetic_findings_entries",
        operation_description="Bulk delete GeneticFindings entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of GeneticFindings IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["GeneticFindings"]
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete GeneticFindings entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        genetic_findings = bulk_retrieve(GeneticFindings, ids, "genetic_findings_id")
        response_data, accepted, rejected = [], False, False

        for genetic_findings_id in ids:
            if genetic_findings_id in genetic_findings:
                data, result = delete_metadata("genetic_findings", genetic_findings_id, "genetic_findings_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(response_constructor(
                    identifier=genetic_findings_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


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
        tags=["ExperimentStage"]
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_experiment_stage(self, request):
        experiment_stage = bulk_model_retrieve(request.data, ExperimentStage, "experiment_stage_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_stage_id = datum.get("experiment_stage_id")
            if experiment_stage_id and experiment_stage_id in experiment_stage:
                response_data.append(response_constructor(
                    identifier=experiment_stage_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="ExperimentStage entry already exists"
                ))
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
                "ids", openapi.IN_QUERY, description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentStage"]
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        experiment_stage = bulk_retrieve(ExperimentStage, ids, "experiment_stage_id")
        response_data, accepted, rejected = [], False, False

        for experiment_stage_id in ids:
            if experiment_stage_id in experiment_stage:
                response_data.append(response_constructor(
                    identifier=experiment_stage_id,
                    request_status="SUCCESS",
                    code=200,
                    data=experiment_stage[experiment_stage_id]
                ))
                accepted = True
            else:
                response_data.append(response_constructor(
                    identifier=experiment_stage_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=ExperimentStageSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentStage"]
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_experiment_stage(self, request):
        experiment_stage = bulk_model_retrieve(request.data, ExperimentStage, "experiment_stage_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_stage_id = datum.get("experiment_stage_id")
            if experiment_stage_id not in experiment_stage:
                response_data.append(response_constructor(
                    identifier=experiment_stage_id,
                    request_status="BAD REQUEST",
                    code=400,
                    data="Entry does not exist"
                ))
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
        tags=["ExperimentStage"]
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
                response_data.append(response_constructor(
                    identifier=experiment_stage_id,
                    request_status="NOT FOUND",
                    code=404,
                    data="Not found"
                ))
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))