#!/usr/bin/env python3
# submodels/apis.py

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

from submodels.models import (
    ReportedRace,
    InternalProjectId,
    PmidId,
    TwinId,
)

from experiments.models import PrepTargetsDetail

from submodels.services import (
    ReportedRaceSerializer,
    InternalProjectIdSerializer,
    PmidIdSerializer,
    TwinIdSerializer,
    PrepTargetsDetailSerializer,
    create_submodel,
    update_submodel,
    delete_submodel,
)


class ReportedRaceViewSet(
    viewsets.GenericViewSet,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReportedRaceSerializer
    select_related_fields = ("changed_by", )

    @swagger_auto_schema(
        method="get",
        operation_id="list_all_reported_races",
        operation_description="Retrieve all ReportedRace entries",
        responses={200: ReportedRaceSerializer(many=True), 400: "Bad request"},
        tags=["ReportedRace"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = ReportedRace.objects.all()
        serializer = ReportedRaceSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_id="create_reported_races",
        operation_description="Create new ReportedRace entries. Must be a superuser.",
        request_body=ReportedRaceSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["ReportedRace"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_reported_race(self, request):
        reported_races = bulk_model_retrieve(request.data, ReportedRace, "name")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            name = datum.get("name")
            if name and name in reported_races:
                response_data.append(
                    response_constructor(
                        identifier=name,
                        request_status="BAD REQUEST",
                        code=400,
                        data="ReportedRace entry already exists",
                    )
                )
                rejected = True
            else:
                if not self.request.user.is_superuser:
                    response_data.append(
                        response_constructor(
                            identifier=name,
                            request_status="FORBIDDEN",
                            code=403
                        )
                    )
                    rejected = True
                else:
                    data, result = create_submodel("reported_race", name, datum, self.request.user)
                    response_data.append(data)
                    accepted |= result == "accepted_request"
                    rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="list_reported_races",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["ReportedRace"],
    )
    def list(self, request):
        ids = [i.strip() for i in request.GET.get("ids", "").split(",") if i.strip()]
        reported_races = bulk_retrieve(ReportedRace, ids, "name")
        response_data, accepted, rejected = [], False, False

        for name in ids:
            if name in reported_races:
                response_data.append(
                    response_constructor(
                        identifier=name,
                        request_status="SUCCESS",
                        code=200,
                        data=reported_races[name],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=name,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="update_reported_races",
        operation_description="Update ReportedRace entries. Must be a superuser.",
        request_body=ReportedRaceSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["ReportedRace"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_reported_race(self, request):
        reported_races = bulk_model_retrieve(request.data, ReportedRace, "name")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            name = datum.get("name")
            if name not in reported_races:
                response_data.append(
                    response_constructor(
                        identifier=name,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                if not self.request.user.is_superuser:
                    response_data.append(
                        response_constructor(
                            identifier=name,
                            request_status="FORBIDDEN",
                            code=403
                        )
                    )
                    rejected = True
                else:
                    data, result = update_submodel(
                        "reported_race",
                        name,
                        reported_races[name],
                        datum,
                        self.request.user
                    )
                    response_data.append(data)
                    accepted |= result == "accepted_request"
                    rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="delete_reported_races",
        operation_description="Bulk delete ReportedRace entries by comma-separated IDs in the `ids` query parameter. Must be superuser to use.",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of Names (e.g., B1,B2,B3)",
                required=True,
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "All deletions successful",
            207: "Some deletions failed",
            400: "Bad request",
        },
        tags=["ReportedRace"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete ReportedRace entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        reported_races = bulk_retrieve(ReportedRace, ids, "name")
        response_data, accepted, rejected = [], False, False

        if not self.request.user.is_superuser:
            response_data.append(
                response_constructor(
                    identifier=name,
                    request_status="FORBIDDEN",
                    code=403
                )
            )
            rejected = True
        else:
            for name in ids:
                if name in reported_races:
                    data, result = delete_submodel("reported_race", name, "name")
                    response_data.append(data)
                    accepted |= result == "accepted_request"
                    rejected |= result != "accepted_request"
                else:
                    response_data.append(
                        response_constructor(
                            identifier=name,
                            request_status="NOT FOUND",
                            code=404,
                            data="Not found",
                        )
                    )
                    rejected = True

        return Response(response_data, status=response_status(accepted, rejected))
