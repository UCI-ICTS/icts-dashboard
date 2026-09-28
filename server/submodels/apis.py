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


class ReportedRaceViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReportedRaceSerializer
    select_related_fields = "changed_by"

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
        operation_description="Delete ReportedRace entries by comma-separated IDs in the `ids` query parameter. Must be superuser to use.",
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


class InternalProjectIdViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = InternalProjectIdSerializer
    select_related_fields = "changed_by"

    @swagger_auto_schema(
        method="get",
        operation_id="list_all_internal_project_ids",
        operation_description="Retrieve all InternalProjectId entries",
        responses={200: InternalProjectIdSerializer(many=True), 400: "Bad request"},
        tags=["InternalProjectId"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = InternalProjectId.objects.all()
        serializer = InternalProjectIdSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_id="create_internal_project_ids",
        operation_description="Create new InternalProjectId entries.",
        request_body=InternalProjectIdSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["InternalProjectId"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_internal_project_id(self, request):
        internal_project_ids = bulk_model_retrieve(request.data, InternalProjectId, "internal_project_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            internal_project_id = datum.get("internal_project_id")
            if internal_project_id and internal_project_id in internal_project_ids:
                response_data.append(
                    response_constructor(
                        identifier=internal_project_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="InternalProjectId entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_submodel("internal_project_id", internal_project_id, datum, self.request.user)
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="list_internal_project_ids",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["InternalProjectId"],
    )
    def list(self, request):
        ids = [i.strip() for i in request.GET.get("ids", "").split(",") if i.strip()]
        internal_project_ids = bulk_retrieve(InternalProjectId, ids, "internal_project_id")
        response_data, accepted, rejected = [], False, False

        for internal_project_id in ids:
            if internal_project_id in internal_project_ids:
                response_data.append(
                    response_constructor(
                        identifier=internal_project_id,
                        request_status="SUCCESS",
                        code=200,
                        data=internal_project_ids[internal_project_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=internal_project_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="update_internal_project_ids",
        operation_description="Update InternalProjectId entries.",
        request_body=InternalProjectIdSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["InternalProjectId"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_internal_project_id(self, request):
        internal_project_ids = bulk_model_retrieve(request.data, InternalProjectId, "internal_project_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            internal_project_id = datum.get("internal_project_id")
            if internal_project_id not in internal_project_ids:
                response_data.append(
                    response_constructor(
                        identifier=internal_project_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_submodel(
                    "internal_project_id",
                    internal_project_id,
                    internal_project_ids[internal_project_id],
                    datum,
                    self.request.user
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="delete_internal_project_ids",
        operation_description="Delete InternalProjectId entries by comma-separated IDs in the `ids` query parameter.",
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
        tags=["InternalProjectId"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete InternalProjectId entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        internal_project_ids = bulk_retrieve(InternalProjectId, ids, "internal_project_id")
        response_data, accepted, rejected = [], False, False


        for internal_project_id in ids:
            if internal_project_id in internal_project_ids:
                data, result = delete_submodel("internal_project_id", internal_project_id, "internal_project_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=internal_project_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class PmidIdViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PmidIdSerializer
    select_related_fields = "changed_by"

    @swagger_auto_schema(
        method="get",
        operation_id="list_all_pmid_ids",
        operation_description="Retrieve all PmidId entries",
        responses={200: PmidIdSerializer(many=True), 400: "Bad request"},
        tags=["PmidId"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = PmidId.objects.all()
        serializer = PmidIdSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_id="create_pmid_ids",
        operation_description="Create new PmidId entries.",
        request_body=PmidIdSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["PmidId"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_pmid_id(self, request):
        pmid_ids = bulk_model_retrieve(request.data, PmidId, "pmid_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            pmid_id = datum.get("pmid_id")
            if pmid_id and pmid_id in pmid_ids:
                response_data.append(
                    response_constructor(
                        identifier=pmid_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="PmidId entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_submodel("pmid_id", pmid_id, datum, self.request.user)
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="list_pmid_ids",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["PmidId"],
    )
    def list(self, request):
        ids = [i.strip() for i in request.GET.get("ids", "").split(",") if i.strip()]
        pmid_ids = bulk_retrieve(PmidId, ids, "pmid_id")
        response_data, accepted, rejected = [], False, False

        for pmid_id in ids:
            if pmid_id in pmid_ids:
                response_data.append(
                    response_constructor(
                        identifier=pmid_id,
                        request_status="SUCCESS",
                        code=200,
                        data=pmid_ids[pmid_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=pmid_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="update_pmid_ids",
        operation_description="Update PmidId entries.",
        request_body=PmidIdSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["PmidId"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_pmid_id(self, request):
        pmid_ids = bulk_model_retrieve(request.data, PmidId, "pmid_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            pmid_id = datum.get("pmid_id")
            if pmid_id not in pmid_ids:
                response_data.append(
                    response_constructor(
                        identifier=pmid_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_submodel(
                    "pmid_id",
                    pmid_id,
                    pmid_ids[pmid_id],
                    datum,
                    self.request.user
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="delete_pmid_ids",
        operation_description="Delete PmidId entries by comma-separated IDs in the `ids` query parameter.",
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
        tags=["PmidId"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete PmidId entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        pmid_ids = bulk_retrieve(PmidId, ids, "pmid_id")
        response_data, accepted, rejected = [], False, False


        for pmid_id in ids:
            if pmid_id in pmid_ids:
                data, result = delete_submodel("pmid_id", pmid_id, "pmid_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=pmid_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class TwinIdViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TwinIdSerializer
    select_related_fields = "changed_by"

    @swagger_auto_schema(
        method="get",
        operation_id="list_all_twin_ids",
        operation_description="Retrieve all TwinId entries",
        responses={200: TwinIdSerializer(many=True), 400: "Bad request"},
        tags=["TwinId"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = TwinId.objects.all()
        serializer = TwinIdSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_id="create_twin_ids",
        operation_description="Create new TwinId entries.",
        request_body=TwinIdSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["TwinId"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_twin_id(self, request):
        twin_ids = bulk_model_retrieve(request.data, TwinId, "twin_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            twin_id = datum.get("twin_id")
            if twin_id and twin_id in twin_ids:
                response_data.append(
                    response_constructor(
                        identifier=twin_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="TwinId entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_submodel("twin_id", twin_id, datum, self.request.user)
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="list_twin_ids",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["TwinId"],
    )
    def list(self, request):
        ids = [i.strip() for i in request.GET.get("ids", "").split(",") if i.strip()]
        twin_ids = bulk_retrieve(TwinId, ids, "twin_id")
        response_data, accepted, rejected = [], False, False

        for twin_id in ids:
            if twin_id in twin_ids:
                response_data.append(
                    response_constructor(
                        identifier=twin_id,
                        request_status="SUCCESS",
                        code=200,
                        data=twin_ids[twin_id],
                    )
                )
                accepted = True
            else:
                response_data.append(
                    response_constructor(
                        identifier=twin_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="update_twin_ids",
        operation_description="Update TwinId entries.",
        request_body=TwinIdSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["TwinId"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_twin_id(self, request):
        twin_ids = bulk_model_retrieve(request.data, TwinId, "twin_id")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            twin_id = datum.get("twin_id")
            if twin_id not in twin_ids:
                response_data.append(
                    response_constructor(
                        identifier=twin_id,
                        request_status="BAD REQUEST",
                        code=400,
                        data="Entry does not exist",
                    )
                )
                rejected = True
            else:
                data, result = update_submodel(
                    "twin_id",
                    twin_id,
                    twin_ids[twin_id],
                    datum,
                    self.request.user
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="delete_twin_ids",
        operation_description="Delete TwinId entries by comma-separated IDs in the `ids` query parameter.",
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
        tags=["TwinId"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete TwinId entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        twin_ids = bulk_retrieve(TwinId, ids, "twin_id")
        response_data, accepted, rejected = [], False, False


        for twin_id in ids:
            if twin_id in twin_ids:
                data, result = delete_submodel("twin_id", twin_id, "twin_id")
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"
            else:
                response_data.append(
                    response_constructor(
                        identifier=twin_id,
                        request_status="NOT FOUND",
                        code=404,
                        data="Not found",
                    )
                )
                rejected = True

        return Response(response_data, status=response_status(accepted, rejected))


class PrepTargetsDetailViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PrepTargetsDetailSerializer
    select_related_fields = "changed_by"

    @swagger_auto_schema(
        method="get",
        operation_id="list_all_prep_targets_details",
        operation_description="Retrieve all PrepTargetsDetail entries",
        responses={200: PrepTargetsDetailSerializer(many=True), 400: "Bad request"},
        tags=["PrepTargetsDetail"],
    )
    @action(detail=False, methods=["get"], url_path="all")
    def list_all(self, request):
        queryset = PrepTargetsDetail.objects.all()
        serializer = PrepTargetsDetailSerializer(queryset, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_id="create_prep_targets_details",
        operation_description="Create new PrepTargetsDetail entries.",
        request_body=PrepTargetsDetailSerializer(many=True),
        responses={200: "All created", 207: "Partial success", 400: "Bad request"},
        tags=["PrepTargetsDetail"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_prep_targets_detail(self, request):
        prep_targets_details = bulk_model_retrieve(request.data, PrepTargetsDetail, "name")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            name = datum.get("name")
            if name and name in prep_targets_details:
                response_data.append(
                    response_constructor(
                        identifier=name,
                        request_status="BAD REQUEST",
                        code=400,
                        data="PrepTargetsDetail entry already exists",
                    )
                )
                rejected = True
            else:
                data, result = create_submodel("prep_targets_detail", name, datum, self.request.user)
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        operation_id="list_prep_targets_details",
        manual_parameters=[
            openapi.Parameter(
                "ids",
                openapi.IN_QUERY,
                description="Comma-separated list of IDs",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: "All success", 207: "Partial success", 400: "Bad request"},
        tags=["PrepTargetsDetail"],
    )
    def list(self, request):
        ids = [i.strip() for i in request.GET.get("ids", "").split(",") if i.strip()]
        prep_targets_details = bulk_retrieve(PrepTargetsDetail, ids, "name")
        response_data, accepted, rejected = [], False, False

        for name in ids:
            if name in prep_targets_details:
                response_data.append(
                    response_constructor(
                        identifier=name,
                        request_status="SUCCESS",
                        code=200,
                        data=prep_targets_details[name],
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
        operation_id="update_prep_targets_details",
        operation_description="Update PrepTargetsDetail entries.",
        request_body=PrepTargetsDetailSerializer(many=True),
        responses={200: "All updated", 207: "Partial success", 400: "Bad request"},
        tags=["PrepTargetsDetail"],
    )
    @action(detail=False, methods=["post"], url_path="update")
    def update_prep_targets_detail(self, request):
        prep_targets_details = bulk_model_retrieve(request.data, PrepTargetsDetail, "name")
        response_data, accepted, rejected = [], False, False

        for datum in request.data:
            name = datum.get("name")
            if name not in prep_targets_details:
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
                data, result = update_submodel(
                    "prep_targets_detail",
                    name,
                    prep_targets_details[name],
                    datum,
                    self.request.user
                )
                response_data.append(data)
                accepted |= result == "accepted_request"
                rejected |= result != "accepted_request"

        return Response(response_data, status=response_status(accepted, rejected))

    @swagger_auto_schema(
        method="delete",
        operation_id="delete_prep_targets_details",
        operation_description="Delete PrepTargetsDetail entries by comma-separated IDs in the `ids` query parameter.",
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
        tags=["PrepTargetsDetail"],
    )
    @action(detail=False, methods=["delete"], url_path="delete")
    def delete(self, request):
        """
        Bulk delete PrepTargetsDetail entries by ID.
        """
        ids = request.GET.get("ids", "").split(",")
        prep_targets_details = bulk_retrieve(PrepTargetsDetail, ids, "name")
        response_data, accepted, rejected = [], False, False


        for name in ids:
            if name in prep_targets_details:
                data, result = delete_submodel("prep_targets_detail", name, "name")
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