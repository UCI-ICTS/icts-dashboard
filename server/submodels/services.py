#!/usr/bin/env python3
# submodels/servces.py

from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from config.selectors import (
    remove_na,
    response_constructor,
    compare_data,
    TableValidator,
)
from submodels.models import (
    ReportedRace,
    InternalProjectId,
    PmidId,
    TwinId,
)

from experiments.models import PrepTargetsDetail

from rest_framework import serializers


class ReportedRaceSerializer(serializers.ModelSerializer):
    """
    Docstring for ReportedRaceSerializer
    """
    class Meta:
        model = ReportedRace
        fields = ["name"]


class InternalProjectIdSerializer(serializers.ModelSerializer):
    """
    Docstring for InternalProjectIdSerializer
    """
    class Meta:
        model = InternalProjectId
        fields = ["name"]


class PmidIdSerializer(serializers.ModelSerializer):
    """
    Docstring for PmidIdSerializer
    """
    class Meta:
        model = PmidId
        fields = ["name"]


class TwinIdSerializer(serializers.ModelSerializer):
    """
    Docstring for TwinIdSerializer
    """
    class Meta:
        model = TwinId
        fields = ["name"]


class PrepTargetsDetailSerializer(serializers.ModelSerializer):
    """
    Docstring for PrepTargetsDetail
    """
    class Meta:
        model = PrepTargetsDetail
        fields = ["name"]


def create_submodel(table_name: str, identifier: str, datum: dict, current_user: User):
    """
    Create a new submodel instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create.
        identifier (str): The unique identifier for the experiment instance.
        datum (dict): The data to create the experiment instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """

    table_serializers = {
        "reported_race": {
            "input_serializer": ReportedRaceSerializer,
            "output_serializer": ReportedRaceSerializer,
        },
        "internal_project_id": {
            "input_serializer": InternalProjectIdSerializer,
            "output_serializer": InternalProjectIdSerializer,
        },
        "pmid_id": {
            "input_serializer": PmidIdSerializer,
            "output_serializer": PmidIdSerializer,
        },
        "twin_id": {
            "input_serializer": TwinIdSerializer,
            "output_serializer": TwinIdSerializer,
        },
        "prep_targets_detail": {
            "input_serializer": PrepTargetsDetailSerializer,
            "output_serializer": PrepTargetsDetailSerializer,
        },
    }

    model_input_serializer = table_serializers[table_name]["input_serializer"]
    model_output_serializer = table_serializers[table_name]["output_serializer"]

    if "parsed_data" in table_serializers[table_name]:
        datum = remove_na(table_serializers[table_name]["parsed_data"](datum))
    else:
        datum = remove_na(datum=datum)

    table_validator = TableValidator()
    table_validator.validate_json(json_object=datum, table_name=table_name)
    results = table_validator.get_validation_results()
    if results["valid"]:
        serializer = model_input_serializer(data=datum)
        if serializer.is_valid():
            new_instance = serializer.save(changed_by=current_user)
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="CREATED",
                    code=201,
                    message=f"{table_name} {identifier} created.",
                    data={"instance": model_output_serializer(new_instance).data},
                ),
                "accepted_request",
            )
        else:
            error_data = [{item: serializer.errors[item]} for item in serializer.errors]
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="BAD REQUEST",
                    code=400,
                    data=error_data,
                ),
                "rejected_request",
            )
    else:
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=results["errors"],
            ),
            "rejected_request",
        )


def update_submodel(
    table_name: str, identifier: str, model_instance, datum: dict, current_user: User):
    """
    Update an existing submodel instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to update.
        identifier (str): The unique identifier for the experiment instance.
        model_instance: The existing model instance to update.
        datum (dict): The data to update the experiment instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "reported_race": {
            "input_serializer": ReportedRaceSerializer,
            "output_serializer": ReportedRaceSerializer,
        },
        "internal_project_id": {
            "input_serializer": InternalProjectIdSerializer,
            "output_serializer": InternalProjectIdSerializer,
        },
        "pmid_id": {
            "input_serializer": PmidIdSerializer,
            "output_serializer": PmidIdSerializer,
        },
        "twin_id": {
            "input_serializer": TwinIdSerializer,
            "output_serializer": TwinIdSerializer,
        },
        "prep_targets_detail": {
            "input_serializer": PrepTargetsDetailSerializer,
            "output_serializer": PrepTargetsDetailSerializer,
        },
    }

    serializers = table_serializers.get(table_name)
    if not serializers:
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=f"Unsupported table: {table_name}",
            ),
            "rejected_request",
        )

    if "parsed_data" in table_serializers[table_name]:
        datum = table_serializers[table_name]["parsed_data"](datum)

    with transaction.atomic():
        input_serializer = serializers["input_serializer"]
        output_serializer = serializers["output_serializer"]
        changes = compare_data(
            old_data=output_serializer(model_instance).data,
            new_data=datum,
        )

        if not changes:
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="NO CHANGE",
                    code=204,
                    message=f"{table_name} {identifier} had no changes.",
                    data={
                        "updates": None,
                        "instance": output_serializer(model_instance).data,
                    },
                ),
                "accepted_request",
            )

        serializer = input_serializer(model_instance, data=datum, partial=True)

        if serializer.is_valid():
            updated_instance = serializer.save(changed_by=current_user)
            message = (
                f"{table_name} {identifier} updated."
                if changes
                else f"{table_name} {identifier} had no changes."
            )
            status_label = "UPDATED" if changes else "NO CHANGE"
            code = 200 if changes else 204
            return (
                response_constructor(
                    identifier=identifier,
                    request_status=status_label,
                    code=code,
                    message=message,
                    data={
                        "updates": changes or None,
                        "instance": output_serializer(updated_instance).data,
                    },
                ),
                "accepted_request",
            )
        else:
            error_data = [{item: serializer.errors[item]} for item in serializer.errors]
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="BAD REQUEST",
                    code=400,
                    data=error_data,
                ),
                "rejected_request",
            )


def delete_submodel(table_name: str, identifier: str, id_field: str = "id"):
    """
    Delete an existing submodel model instance and the corresponding Submodel object
    based on the provided identifier.

    Args:
        table_name (str): The name of the table (model) to delete from.
        identifier (str): The unique identifier of the model instance.
        id_field (str): The field used as an identifier (default is "id").

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """

    model_mapping = {
        "reported_race": ReportedRace,
        "internal_project_id": InternalProjectId,
        "pmid_id": PmidId,
        "twin_id": TwinId,
        "prep_targets_detail": PrepTargetsDetail,
    }

    model_class = model_mapping.get(table_name)
    if not model_class:
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=f"Invalid table name: {table_name}",
            ),
            "rejected_request",
        )

    try:
        instance = model_class.objects.filter(**{id_field: identifier}).first()
        if instance:
            instance.delete()
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="DELETED",
                    code=200,
                    data=f"{table_name} {identifier} deleted successfully.",
                ),
                "accepted_request",
            )
        else:
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="NOT FOUND",
                    code=404,
                    data=f"{table_name} {identifier} not found.",
                ),
                "rejected_request",
            )

    except Exception as error:
        return (
            response_constructor(
                identifier=identifier,
                request_status="SERVER ERROR",
                code=500,
                data=str(error),
            ),
            "rejected_request",
        )
