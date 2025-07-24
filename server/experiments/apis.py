#!/usr/bin/env python3
# experiments/apis.py

from config.selectors import TableValidator, response_constructor, response_status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from config.selectors import bulk_model_retrieve, bulk_retrieve

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
    ExperimentRNAShortRead,
)
from experiments.services import (
    AlignedDNAShortReadSerializer,
    AlignedRNAShortReadInputSerializer,
    AlignedRNAShortReadOutputSerializer,
    AlignedNanoporeSerializer,
    AlignedPacBioSerializer,
    AlignedRNASerializer,
    AlignedSerializer,
    ExperimentSerializer,
    ExperimentNanoporeSerializer,
    ExperimentPacBioSerializer,
    ExperimentRNAInputSerializer,
    ExperimentRNAOutputSerializer,
    ExperimentDNAInputSerializer,
    ExperimentDNAOutputSerializer,
    create_experiment,
    update_experiments_entry,
    delete_experiment,
    create_aligned,
    delete_aligned,
)
from experiments.selectors import get_experiment


class ExperimentViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all Experiment entries",
        responses={200: ExperimentSerializer(many=True), 400: "Bad request"},
        tags=["Experiment"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = Experiment.objects.all()
        serializer = ExperimentSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

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
        tags=["Experiment"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        experiments = bulk_retrieve(Experiment, ids, "experiment_id")
        response_data, accepted, rejected = [], False, False

        # import pdb; pdb.set_trace()
        for experiment_id in ids:
            if experiment_id in experiments:
                response_data.append(
                    response_constructor(
                        identifier=experiment_id,
                        request_status="SUCCESS",
                        code=200,
                        data=experiments[experiment_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class AlignedViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all Aligned entries",
        responses={200: AlignedSerializer(many=True), 400: "Bad request"},
        tags=["Aligned"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = Aligned.objects.all()
        serializer = AlignedSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

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
        tags=["Aligned"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")

        aligned = bulk_retrieve(Aligned, ids, "aligned_id")
        response_data, accepted, rejected = [], False, False

        for aligned_id in ids:
            if aligned_id in aligned:
                response_data.append(
                    response_constructor(
                        identifier=aligned_id,
                        request_status="SUCCESS",
                        code=200,
                        data=aligned[aligned_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class ExperimentRNAShortReadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all ExperimentRNAShortRead entries",
        responses={200: ExperimentRNAOutputSerializer(many=True), 400: "Bad request"},
        tags=["ExperimentRNAShortRead"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = ExperimentRNAShortRead.objects.all()
        serializer = ExperimentRNAOutputSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=ExperimentRNAInputSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentRNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_experiment_rna_short_read(self, request):
        experiment_rna_short_read = bulk_model_retrieve(
            request.data, ExperimentRNAShortRead, "experiment_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_rna_short_read_id = datum.get("experiment_rna_short_read_id")
            if (
                experiment_rna_short_read_id
                and experiment_rna_short_read_id in experiment_rna_short_read
            ):
                response_data.append(
                    response_constructor(
                        identifier=experiment_rna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="ExperimentRNAShortRead entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_experiment(
                    "experiment_rna_short_read", experiment_rna_short_read_id, datum
                )
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
        tags=["ExperimentRNAShortRead"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        experiment_rna_short_read = bulk_retrieve(
            ExperimentRNAShortRead, ids, "experiment_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_rna_short_read_id in ids:
            if experiment_rna_short_read_id in experiment_rna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=experiment_rna_short_read_id,
                        request_status="SUCCESS",
                        code=200,
                        data=experiment_rna_short_read[experiment_rna_short_read_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_rna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=ExperimentRNAInputSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentRNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_experiment_rna_short_read(self, request):
        experiment_rna_short_read = bulk_model_retrieve(
            request.data, ExperimentRNAShortRead, "experiment_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_rna_short_read_id = datum.get("experiment_rna_short_read_id")
            if experiment_rna_short_read_id not in experiment_rna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=experiment_rna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "experiment_rna_short_read",
                    experiment_rna_short_read_id,
                    experiment_rna_short_read[experiment_rna_short_read_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_experiment_rna_short_read_entries",
        operation_description="Bulk delete ExperimentRNAShortRead entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of ExperimentRNAShortRead IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["ExperimentRNAShortRead"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete ExperimentRNAShortRead entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        experiment_rna_short_read = bulk_retrieve(
            ExperimentRNAShortRead, ids, "experiment_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_rna_short_read_id in ids:
            if experiment_rna_short_read_id in experiment_rna_short_read:
                data, result = delete_experiment(
                    "experiment_rna_short_read",
                    experiment_rna_short_read_id,
                    "experiment_rna_short_read_id",
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_rna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class AlignedRNAShortReadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all AlignedRNAShortRead entries",
        responses={
            200: AlignedRNAShortReadOutputSerializer(many=True),
            400: "Bad request",
        },
        tags=["AlignedRNAShortRead"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = AlignedRNAShortRead.objects.all()
        serializer = AlignedRNAShortReadOutputSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=AlignedRNAShortReadInputSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedRNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_aligned_rna_short_read(self, request):
        aligned_rna_short_read = bulk_model_retrieve(
            request.data, AlignedRNAShortRead, "aligned_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_rna_short_read_id = datum.get("aligned_rna_short_read_id")
            if (
                aligned_rna_short_read_id
                and aligned_rna_short_read_id in aligned_rna_short_read
            ):
                response_data.append(
                    response_constructor(
                        identifier=aligned_rna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="AlignedRNAShortRead entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_aligned(
                    "aligned_rna_short_read", aligned_rna_short_read_id, datum
                )
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
        tags=["AlignedRNAShortRead"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        aligned_rna_short_read = bulk_retrieve(
            AlignedRNAShortRead, ids, "aligned_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for aligned_rna_short_read_id in ids:
            if aligned_rna_short_read_id in aligned_rna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=aligned_rna_short_read_id,
                        request_status="SUCCESS",
                        code=200,
                        data=aligned_rna_short_read[aligned_rna_short_read_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_rna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=AlignedRNAShortReadInputSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedRNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_aligned_rna_short_read(self, request):
        aligned_rna_short_read = bulk_model_retrieve(
            request.data, AlignedRNAShortRead, "aligned_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_rna_short_read_id = datum.get("aligned_rna_short_read_id")
            if aligned_rna_short_read_id not in aligned_rna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=aligned_rna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "aligned_rna_short_read",
                    aligned_rna_short_read_id,
                    aligned_rna_short_read[aligned_rna_short_read_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_aligned_rna_short_read_entries",
        operation_description="Bulk delete AlignedRNAShortRead entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of AlignedRNAShortRead IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["AlignedRNAShortRead"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete AlignedRNAShortRead entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        aligned_rna_short_read = bulk_retrieve(
            AlignedRNAShortRead, ids, "aligned_rna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for aligned_rna_short_read_id in ids:
            if aligned_rna_short_read_id in aligned_rna_short_read:
                data, result = delete_aligned(
                    "aligned_rna_short_read",
                    aligned_rna_short_read_id,
                    "aligned_rna_short_read_id",
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_rna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class ExperimentDNAShortReadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all ExperimentDNAShortRead entries",
        responses={200: ExperimentDNAOutputSerializer(many=True), 400: "Bad request"},
        tags=["ExperimentDNAShortRead"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = ExperimentDNAShortRead.objects.all()
        serializer = ExperimentDNAOutputSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=ExperimentDNAInputSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentDNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_experiment_dna_short_read(self, request):
        experiment_dna_short_read = bulk_model_retrieve(
            request.data, ExperimentDNAShortRead, "experiment_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_dna_short_read_id = datum.get("experiment_dna_short_read_id")
            if (
                experiment_dna_short_read_id
                and experiment_dna_short_read_id in experiment_dna_short_read
            ):
                response_data.append(
                    response_constructor(
                        identifier=experiment_dna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="ExperimentDNAShortRead entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_experiment(
                    "experiment_dna_short_read", experiment_dna_short_read_id, datum
                )
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
        tags=["ExperimentDNAShortRead"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        experiment_dna_short_read = bulk_retrieve(
            ExperimentDNAShortRead, ids, "experiment_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_dna_short_read_id in ids:
            if experiment_dna_short_read_id in experiment_dna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=experiment_dna_short_read_id,
                        request_status="SUCCESS",
                        code=200,
                        data=experiment_dna_short_read[experiment_dna_short_read_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_dna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=ExperimentDNAInputSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentDNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_experiment_dna_short_read(self, request):
        experiment_dna_short_read = bulk_model_retrieve(
            request.data, ExperimentDNAShortRead, "experiment_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_dna_short_read_id = datum.get("experiment_dna_short_read_id")
            if experiment_dna_short_read_id not in experiment_dna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=experiment_dna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "experiment_dna_short_read",
                    experiment_dna_short_read_id,
                    experiment_dna_short_read[experiment_dna_short_read_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_experiment_dna_short_read_entries",
        operation_description="Bulk delete ExperimentDNAShortRead entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of ExperimentDNAShortRead IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["ExperimentDNAShortRead"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete ExperimentDNAShortRead entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        experiment_dna_short_read = bulk_retrieve(
            ExperimentDNAShortRead, ids, "experiment_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_dna_short_read_id in ids:
            if experiment_dna_short_read_id in experiment_dna_short_read:
                data, result = delete_experiment(
                    "experiment_dna_short_read",
                    experiment_dna_short_read_id,
                    "experiment_dna_short_read_id",
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_dna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class AlignedDNAShortReadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all AlignedDNAShortRead entries",
        responses={200: AlignedDNAShortReadSerializer(many=True), 400: "Bad request"},
        tags=["AlignedDNAShortRead"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = AlignedDNAShortRead.objects.all()
        serializer = AlignedDNAShortReadSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=AlignedDNAShortReadSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedDNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_aligned_dna_short_read(self, request):
        aligned_dna_short_read = bulk_model_retrieve(
            request.data, AlignedDNAShortRead, "aligned_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_dna_short_read_id = datum.get("aligned_dna_short_read_id")
            if (
                aligned_dna_short_read_id
                and aligned_dna_short_read_id in aligned_dna_short_read
            ):
                response_data.append(
                    response_constructor(
                        identifier=aligned_dna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="AlignedDNAShortRead entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_aligned(
                    "aligned_dna_short_read", aligned_dna_short_read_id, datum
                )
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
        tags=["AlignedDNAShortRead"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        aligned_dna_short_read = bulk_retrieve(
            AlignedDNAShortRead, ids, "aligned_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for aligned_dna_short_read_id in ids:
            if aligned_dna_short_read_id in aligned_dna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=aligned_dna_short_read_id,
                        request_status="SUCCESS",
                        code=200,
                        data=aligned_dna_short_read[aligned_dna_short_read_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_dna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=AlignedDNAShortReadSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedDNAShortRead"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_aligned_dna_short_read(self, request):
        aligned_dna_short_read = bulk_model_retrieve(
            request.data, AlignedDNAShortRead, "aligned_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_dna_short_read_id = datum.get("aligned_dna_short_read_id")
            if aligned_dna_short_read_id not in aligned_dna_short_read:
                response_data.append(
                    response_constructor(
                        identifier=aligned_dna_short_read_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "aligned_dna_short_read",
                    aligned_dna_short_read_id,
                    aligned_dna_short_read[aligned_dna_short_read_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_aligned_dna_short_read_entries",
        operation_description="Bulk delete AlignedDNAShortRead entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of AlignedDNAShortRead IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["AlignedDNAShortRead"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete AlignedDNAShortRead entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        aligned_dna_short_read = bulk_retrieve(
            AlignedDNAShortRead, ids, "aligned_dna_short_read_id"
        )
        response_data, accepted, rejected = [], False, False

        for aligned_dna_short_read_id in ids:
            if aligned_dna_short_read_id in aligned_dna_short_read:
                data, result = delete_aligned(
                    "aligned_dna_short_read",
                    aligned_dna_short_read_id,
                    "aligned_dna_short_read_id",
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_dna_short_read_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class ExperimentPacBioViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all ExperimentPacBio entries",
        responses={200: ExperimentPacBioSerializer(many=True), 400: "Bad request"},
        tags=["ExperimentPacBio"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = ExperimentPacBio.objects.all()
        serializer = ExperimentPacBioSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=ExperimentPacBioSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentPacBio"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_experiment_pac_bio(self, request):
        experiment_pac_bio = bulk_model_retrieve(
            request.data, ExperimentPacBio, "experiment_pac_bio_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_pac_bio_id = datum.get("experiment_pac_bio_id")
            if experiment_pac_bio_id and experiment_pac_bio_id in experiment_pac_bio:
                response_data.append(
                    response_constructor(
                        identifier=experiment_pac_bio_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="ExperimentPacBio entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_experiment(
                    "experiment_pac_bio", experiment_pac_bio_id, datum
                )
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
        tags=["ExperimentPacBio"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        experiment_pac_bio = bulk_retrieve(
            ExperimentPacBio, ids, "experiment_pac_bio_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_pac_bio_id in ids:
            if experiment_pac_bio_id in experiment_pac_bio:
                response_data.append(
                    response_constructor(
                        identifier=experiment_pac_bio_id,
                        request_status="SUCCESS",
                        code=200,
                        data=experiment_pac_bio[experiment_pac_bio_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_pac_bio_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=ExperimentPacBioSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentPacBio"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_experiment_pac_bio(self, request):
        experiment_pac_bio = bulk_model_retrieve(
            request.data, ExperimentPacBio, "experiment_pac_bio_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_pac_bio_id = datum.get("experiment_pac_bio_id")
            if experiment_pac_bio_id not in experiment_pac_bio:
                response_data.append(
                    response_constructor(
                        identifier=experiment_pac_bio_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "experiment_pac_bio",
                    experiment_pac_bio_id,
                    experiment_pac_bio[experiment_pac_bio_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_experiment_pac_bio_entries",
        operation_description="Bulk delete ExperimentPacBio entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of ExperimentPacBio IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["ExperimentPacBio"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete ExperimentPacBio entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        experiment_pac_bio = bulk_retrieve(
            ExperimentPacBio, ids, "experiment_pac_bio_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_pac_bio_id in ids:
            if experiment_pac_bio_id in experiment_pac_bio:
                data, result = delete_experiment(
                    "experiment_pac_bio", experiment_pac_bio_id, "experiment_pac_bio_id"
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_pac_bio_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class AlignedPacBioViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all AlignedPacBio entries",
        responses={200: AlignedPacBioSerializer(many=True), 400: "Bad request"},
        tags=["AlignedPacBio"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = AlignedPacBio.objects.all()
        serializer = AlignedPacBioSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=AlignedPacBioSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedPacBio"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_aligned_pac_bio(self, request):
        aligned_pac_bio = bulk_model_retrieve(
            request.data, AlignedPacBio, "aligned_pac_bio_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_pac_bio_id = datum.get("aligned_pac_bio_id")
            if aligned_pac_bio_id and aligned_pac_bio_id in aligned_pac_bio:
                response_data.append(
                    response_constructor(
                        identifier=aligned_pac_bio_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="AlignedPacBio entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_aligned(
                    "aligned_pac_bio", aligned_pac_bio_id, datum
                )
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
        tags=["AlignedPacBio"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        aligned_pac_bio = bulk_retrieve(AlignedPacBio, ids, "aligned_pac_bio_id")
        response_data, accepted, rejected = [], False, False

        for aligned_pac_bio_id in ids:
            if aligned_pac_bio_id in aligned_pac_bio:
                response_data.append(
                    response_constructor(
                        identifier=aligned_pac_bio_id,
                        request_status="SUCCESS",
                        code=200,
                        data=aligned_pac_bio[aligned_pac_bio_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_pac_bio_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=AlignedPacBioSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedPacBio"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_aligned_pac_bio(self, request):
        aligned_pac_bio = bulk_model_retrieve(
            request.data, AlignedPacBio, "aligned_pac_bio_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_pac_bio_id = datum.get("aligned_pac_bio_id")
            if aligned_pac_bio_id not in aligned_pac_bio:
                response_data.append(
                    response_constructor(
                        identifier=aligned_pac_bio_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "aligned_pac_bio",
                    aligned_pac_bio_id,
                    aligned_pac_bio[aligned_pac_bio_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_aligned_pac_bio_entries",
        operation_description="Bulk delete AlignedPacBio entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of AlignedPacBio IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["AlignedPacBio"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete AlignedPacBio entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        aligned_pac_bio = bulk_retrieve(AlignedPacBio, ids, "aligned_pac_bio_id")
        response_data, accepted, rejected = [], False, False

        for aligned_pac_bio_id in ids:
            if aligned_pac_bio_id in aligned_pac_bio:
                data, result = delete_aligned(
                    "aligned_pac_bio", aligned_pac_bio_id, "aligned_pac_bio_id"
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_pac_bio_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class ExperimentNanoporeViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all ExperimentNanopore entries",
        responses={200: ExperimentNanoporeSerializer(many=True), 400: "Bad request"},
        tags=["ExperimentNanopore"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = ExperimentNanopore.objects.all()
        serializer = ExperimentNanoporeSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=ExperimentNanoporeSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentNanopore"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_experiment_nanopore(self, request):
        experiment_nanopore = bulk_model_retrieve(
            request.data, ExperimentNanopore, "experiment_nanopore_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_nanopore_id = datum.get("experiment_nanopore_id")
            if experiment_nanopore_id and experiment_nanopore_id in experiment_nanopore:
                response_data.append(
                    response_constructor(
                        identifier=experiment_nanopore_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="ExperimentNanopore entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_experiment(
                    "experiment_nanopore", experiment_nanopore_id, datum
                )
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
        tags=["ExperimentNanopore"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        experiment_nanopore = bulk_retrieve(
            ExperimentNanopore, ids, "experiment_nanopore_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_nanopore_id in ids:
            if experiment_nanopore_id in experiment_nanopore:
                response_data.append(
                    response_constructor(
                        identifier=experiment_nanopore_id,
                        request_status="SUCCESS",
                        code=200,
                        data=experiment_nanopore[experiment_nanopore_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_nanopore_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=ExperimentNanoporeSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["ExperimentNanopore"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_experiment_nanopore(self, request):
        experiment_nanopore = bulk_model_retrieve(
            request.data, ExperimentNanopore, "experiment_nanopore_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            experiment_nanopore_id = datum.get("experiment_nanopore_id")
            if experiment_nanopore_id not in experiment_nanopore:
                response_data.append(
                    response_constructor(
                        identifier=experiment_nanopore_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "experiment_nanopore",
                    experiment_nanopore_id,
                    experiment_nanopore[experiment_nanopore_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_experiment_nanopore_entries",
        operation_description="Bulk delete ExperimentNanopore entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of ExperimentNanopore IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["ExperimentNanopore"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete ExperimentNanopore entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        experiment_nanopore = bulk_retrieve(
            ExperimentNanopore, ids, "experiment_nanopore_id"
        )
        response_data, accepted, rejected = [], False, False

        for experiment_nanopore_id in ids:
            if experiment_nanopore_id in experiment_nanopore:
                data, result = delete_experiment(
                    "experiment_nanopore",
                    experiment_nanopore_id,
                    "experiment_nanopore_id",
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=experiment_nanopore_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class AlignedNanoporeViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve all AlignedNanopore entries",
        responses={200: AlignedNanoporeSerializer(many=True), 400: "Bad request"},
        tags=["AlignedNanopore"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = AlignedNanopore.objects.all()
        serializer = AlignedNanoporeSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        request_body=AlignedNanoporeSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedNanopore"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_aligned_nanopore(self, request):
        aligned_nanopore = bulk_model_retrieve(
            request.data, AlignedNanopore, "aligned_nanopore_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_nanopore_id = datum.get("aligned_nanopore_id")
            if aligned_nanopore_id and aligned_nanopore_id in aligned_nanopore:
                response_data.append(
                    response_constructor(
                        identifier=aligned_nanopore_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="AlignedNanopore entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_aligned(
                    "aligned_nanopore", aligned_nanopore_id, datum
                )
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
        tags=["AlignedNanopore"],
    )
    def list(self, request):
        ids = request.GET.get("ids", "").split(",")
        aligned_nanopore = bulk_retrieve(AlignedNanopore, ids, "aligned_nanopore_id")
        response_data, accepted, rejected = [], False, False

        for aligned_nanopore_id in ids:
            if aligned_nanopore_id in aligned_nanopore:
                response_data.append(
                    response_constructor(
                        identifier=aligned_nanopore_id,
                        request_status="SUCCESS",
                        code=200,
                        data=aligned_nanopore[aligned_nanopore_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_nanopore_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        request_body=AlignedNanoporeSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["AlignedNanopore"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_aligned_nanopore(self, request):
        aligned_nanopore = bulk_model_retrieve(
            request.data, AlignedNanopore, "aligned_nanopore_id"
        )
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            aligned_nanopore_id = datum.get("aligned_nanopore_id")
            if aligned_nanopore_id not in aligned_nanopore:
                response_data.append(
                    response_constructor(
                        identifier=aligned_nanopore_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_experiments_entry(
                    "aligned_nanopore",
                    aligned_nanopore_id,
                    aligned_nanopore[aligned_nanopore_id],
                    datum,
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="bulk_delete_aligned_nanopore_entries",
        operation_description="Bulk delete AlignedNanopore entries by comma-separated IDs in the `ids` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of AlignedNanopore IDs (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["AlignedNanopore"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete AlignedNanopore entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        aligned_nanopore = bulk_retrieve(AlignedNanopore, ids, "aligned_nanopore_id")
        response_data, accepted, rejected = [], False, False

        for aligned_nanopore_id in ids:
            if aligned_nanopore_id in aligned_nanopore:
                data, result = delete_aligned(
                    "aligned_nanopore", aligned_nanopore_id, "aligned_nanopore_id"
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=aligned_nanopore_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))
