#!/usr/bin/env python3
# metadata/servces.py

from django.db import transaction, IntegrityError
from rest_framework import serializers
from config.selectors import (
    remove_na,
    response_constructor,
    compare_data,
    TableValidator,
)
from metadata.models import (
    Analyte,
    GeneticFindings,
    Participant,
    Family,
    Phenotype,
    InternalProjectId,
    PmidId,
    TwinId,
    Biobank,
    ExperimentId,
    AlignedId,
)

from metadata.selectors import (
    participant_parser,
    genetic_findings_parser,
    biobank_parser,
)

from submodels.models import ReportedRace


class GeneticFindingsSerializer(serializers.ModelSerializer):
    """
    1. Pop the ManyToMany field from validated_data
    2. Create/update the main instance with the remaining fields
    3. Use .set() to assign the ManyToMany relation
    """

    additional_family_members_with_variant = serializers.PrimaryKeyRelatedField(
        queryset=Participant.objects.all(), many=True, required=False
    )

    experiment_id = serializers.JSONField(required=False)
    variant_type = serializers.JSONField(required=False)
    gene_of_interest = serializers.JSONField(required=False)
    condition_inheritance = serializers.JSONField(required=False)
    method_of_discovery = serializers.JSONField(required=False)

    class Meta:
        model = GeneticFindings
        fields = "__all__"

    def create(self, validated_data):
        """
        Create a new GeneticFindings instance using the validated data
        """
        additional_family_members = validated_data.pop(
            "additional_family_members_with_variant", []
        )
        genetic_findings_instance = GeneticFindings.objects.create(**validated_data)
        if additional_family_members:
            genetic_findings_instance.additional_family_members_with_variant.set(
                additional_family_members
            )
        genetic_findings_instance.save()
        return genetic_findings_instance

    def update(self, instance, validated_data):
        """
        Update each attribute of the instance with validated data
        """
        additional_family_members = validated_data.pop(
            "additional_family_members_with_variant", []
        )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if additional_family_members:
            instance.additional_family_members_with_variant.clear()
            instance.additional_family_members_with_variant.set(
                additional_family_members
            )
        instance.save()

        return instance


class AnalyteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analyte
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Analyte instance using the validated data"""

        # participant_instance = validated_data["participant_id"]
        # if "age_at_collection" in validated_data:
        #     try:
        #         participant_instance.age_at_enrollment == validated_data["age_at_collection"]
        #     except:
        #         raise ValueError

        analyte_instance = Analyte.objects.create(**validated_data)
        return analyte_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class BiobankSerializer(serializers.ModelSerializer):
    child_analytes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="List of downstream analytes and their associated experiments",
    )

    class Meta:
        model = Biobank
        fields = "__all__"

    def create(self, validated_data):
        child_analyte = validated_data.pop("child_analytes", [])
        experiment = validated_data.pop("experiments", [])
        aligned = validated_data.pop("alignments", [])

        try:
            with transaction.atomic():
                biobank = Biobank.objects.create(**validated_data)
                if child_analyte:
                    self._set_relationship(
                        biobank, Analyte, child_analyte, "child_analytes"
                    )
                if experiment:
                    self._set_relationship(
                        biobank, ExperimentId, experiment, "experiments"
                    )
                if aligned:
                    self._set_relationship(
                        biobank, AlignedId, aligned, "alignments"
                    )
                biobank.save()
        except IntegrityError as error:
            raise serializers.ValidationError(error)

        return biobank

    def update(self, instance, validated_data):
        child_analyte = validated_data.pop("child_analytes", [])
        experiment = validated_data.pop("experiments", [])
        aligned = validated_data.pop("alignments", [])

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            self._set_relationship(instance, Analyte, child_analyte, "child_analytes")
            self._set_relationship(instance, ExperimentId, experiment, "experiments")
            self._set_relationship(instance, AlignedId, aligned, "alignments")

        return instance

    def _set_relationship(self, instance, model, ids, related_name):
        # Setting ManyToMany relations
        try:
            manager = getattr(instance, related_name)
            manager.set(model.objects.filter(pk__in=ids))
        except Exception as e:
            print(f"Error setting relationship: {e}")
            raise


class PhenotypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phenotype
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Phenotype instance using the validated data"""
        phenotype = Phenotype.objects.create(**validated_data)
        return phenotype

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            instance.save()
        return instance


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = "__all__"

    def create(self, validated_data):
        """Create an new instance of the model with validated data"""
        family_id = validated_data.get("family_id")
        family, created = Family.objects.get_or_create(
            family_id=family_id, defaults=validated_data
        )
        return family

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ParticipantOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = "__all__"


class ParticipantInputSerializer(serializers.ModelSerializer):
    prior_testing = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of prior testing entries",
    )

    internal_project_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="An identifier used by GREGoR research centers to identify a set of participants for their internal tracking",
    )

    pmid_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Case specific PubMed IDs if applicable",
    )

    twin_id = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Participant IDs for twins, triplets, etc.",
    )

    reported_race = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Participant race if available.",
    )

    class Meta:
        model = Participant
        fields = "__all__"

    def create(self, validated_data):
        internal_project_id = validated_data.pop("internal_project_id", [])
        pmid_id = validated_data.pop("pmid_id", [])
        twin_id = validated_data.pop("twin_id", [])
        reported_race = validated_data.pop("reported_race", [])

        try:
            with transaction.atomic():
                participant = Participant.objects.create(**validated_data)
                if internal_project_id:
                    self._set_relationship(
                        participant,
                        InternalProjectId,
                        internal_project_id,
                        "internal_project_id",
                    )
                if pmid_id:
                    self._set_relationship(participant, PmidId, pmid_id, "pmid_id")
                if twin_id:
                    self._set_relationship(participant, TwinId, twin_id, "twin_id")
                if reported_race:
                    self._set_relationship(
                        participant, ReportedRace, reported_race, "reported_race"
                    )
                participant.save()
        except IntegrityError as error:
            raise serializers.ValidationError(error)

        return participant

    def update(self, instance, validated_data):
        internal_project_id = validated_data.pop("internal_project_id", [])
        pmid_id = validated_data.pop("pmid_id", [])
        twin_id = validated_data.pop("twin_id", [])
        reported_race = validated_data.pop("reported_race", [])

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            self._set_relationship(
                instance, InternalProjectId, internal_project_id, "internal_project_id"
            )
            self._set_relationship(instance, PmidId, pmid_id, "pmid_id")
            self._set_relationship(instance, TwinId, twin_id, "twin_id")
            self._set_relationship(
                instance, ReportedRace, reported_race, "reported_race"
            )

        return instance

    def _set_relationship(self, instance, model, ids, related_name):
        # Setting ManyToMany relations
        # print(instance, model, ids, related_name)  # Debugging
        try:
            manager = getattr(instance, related_name)
            if model == ReportedRace:  # Special handling for ReportedRace
                manager.set(model.objects.filter(description__in=ids))
            else:
                manager.set(model.objects.filter(pk__in=ids))
        except Exception as e:
            print(f"Error setting relationship: {e}")
            raise


def get_or_create_sub_models(datum: dict) -> dict:
    """
    Create or retrieve related model instances based on the provided data.

    This function processes the `datum` dictionary to handle the creation or retrieval
    of related model instances. It updates the `datum` dictionary with the primary keys
    of the related instances.

    Args:
        datum (dict): A dictionary containing the data for the main model and its related models.

    Returns:
        dict: The updated `datum` dictionary with primary keys of the related instances.
    """
    # Define how to handle creation of related objects
    mapping = {
        "family_id": (Family, "family_id"),
        "internal_project_id": (InternalProjectId, "internal_project_id"),
        "pmid_id": (PmidId, "pmid_id"),
        "twin_id": (TwinId, "twin_id"),
        "experiment_id": (ExperimentId, "experiment_id"),
        "aligned_id": (AlignedId, "aligned_id"),
    }
    for key, (model, field_name) in mapping.items():
        if isinstance(datum.get(key), list):  # Handles list fields differently
            objects = []
            for item in datum[key]:
                obj, created = model.objects.get_or_create(**{field_name: item})
                objects.append(obj.pk)
            datum[key] = objects
        else:
            if datum.get(key):
                obj, created = model.objects.get_or_create(**{field_name: datum[key]})
                datum[key] = obj.pk
    return datum


def create_or_update_metadata(
    table_name: str, identifier: str, model_instance, datum: dict
):
    """
    Create or update a model instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create or update.
        identifier (str): The unique identifier for the model instance.
        model_instance: The existing model instance to update, or None to create
            a new instance.
        datum (dict): The data to create or update the model instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """

    table_serializers = {
        "participant": {
            "input_serializer": ParticipantInputSerializer,
            "output_serializer": ParticipantOutputSerializer,
            "parsed_data": lambda datum: participant_parser(participant=datum),
        },
        "family": {
            "input_serializer": FamilySerializer,
            "output_serializer": FamilySerializer,
        },
        "genetic_findings": {
            "input_serializer": GeneticFindingsSerializer,
            "output_serializer": GeneticFindingsSerializer,
            "parsed_data": lambda datum: genetic_findings_parser(
                genetic_findings=datum
            ),
        },
        "analyte": {
            "input_serializer": AnalyteSerializer,
            "output_serializer": AnalyteSerializer,
        },
        "phenotype": {
            "input_serializer": PhenotypeSerializer,
            "output_serializer": PhenotypeSerializer,
        },
        "biobank": {
            "input_serializer": BiobankSerializer,
            "output_serializer": BiobankSerializer,
            "parsed_data": lambda datum: biobank_parser(biobank=datum),
        }
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
        changes = (
            compare_data(
                old_data=model_output_serializer(model_instance).data, new_data=datum
            )
            if model_instance
            else {identifier: "CREATED"}
        )
        # create needed submodules before serialization
        if table_name == "participant":
            datum = get_or_create_sub_models(datum=datum)
        serializer = model_input_serializer(model_instance, data=datum)

        if serializer.is_valid():
            updated_instance = serializer.save()
            if not changes:
                return (
                    response_constructor(
                        identifier=identifier,
                        request_status="SUCCESS",
                        code=200,
                        message=f"{table_name} {identifier} had no changes.",
                        data={
                            "updates": None,
                            "instance": model_output_serializer(updated_instance).data,
                        },
                    ),
                    "accepted_request",
                )

            return (
                response_constructor(
                    identifier=identifier,
                    request_status="UPDATED" if model_instance else "CREATED",
                    code=200 if model_instance else 201,
                    message=(
                        f"{table_name} {identifier} updated."
                        if model_instance
                        else f"{table_name} {identifier} created."
                    ),
                    data={
                        "updates": changes,
                        "instance": model_output_serializer(updated_instance).data,
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


def create_metadata(table_name: str, identifier: str, datum: dict):
    """
    Create a new model instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create.
        identifier (str): The unique identifier for the model instance.
        datum (dict): The data to create the model instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "participant": {
            "input_serializer": ParticipantInputSerializer,
            "output_serializer": ParticipantOutputSerializer,
            "parsed_data": lambda datum: participant_parser(participant=datum),
        },
        "family": {
            "input_serializer": FamilySerializer,
            "output_serializer": FamilySerializer,
        },
        "genetic_findings": {
            "input_serializer": GeneticFindingsSerializer,
            "output_serializer": GeneticFindingsSerializer,
            "parsed_data": lambda datum: genetic_findings_parser(
                genetic_findings=datum
            ),
        },
        "analyte": {
            "input_serializer": AnalyteSerializer,
            "output_serializer": AnalyteSerializer,
        },
        "phenotype": {
            "input_serializer": PhenotypeSerializer,
            "output_serializer": PhenotypeSerializer,
        },
        "biobank": {
            "input_serializer": BiobankSerializer,
            "output_serializer": BiobankSerializer,
            "parsed_data": lambda datum: biobank_parser(biobank=datum),
        }
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
            new_instance = serializer.save()
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


def update_metadata(table_name: str, identifier: str, model_instance, datum: dict):
    """
    Update an existing model instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to update.
        identifier (str): The unique identifier for the model instance.
        model_instance: The existing model instance to update.
        datum (dict): The data to update the model instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "participant": {
            "input_serializer": ParticipantInputSerializer,
            "output_serializer": ParticipantOutputSerializer,
            "parsed_data": lambda datum: participant_parser(participant=datum),
        },
        "family": {
            "input_serializer": FamilySerializer,
            "output_serializer": FamilySerializer,
        },
        "genetic_findings": {
            "input_serializer": GeneticFindingsSerializer,
            "output_serializer": GeneticFindingsSerializer,
            "parsed_data": lambda datum: genetic_findings_parser(
                genetic_findings=datum
            ),
        },
        "analyte": {
            "input_serializer": AnalyteSerializer,
            "output_serializer": AnalyteSerializer,
        },
        "phenotype": {
            "input_serializer": PhenotypeSerializer,
            "output_serializer": PhenotypeSerializer,
        },
        "biobank": {
            "input_serializer": BiobankSerializer,
            "output_serializer": BiobankSerializer,
            "parsed_data": lambda datum: biobank_parser(biobank=datum),
        }
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
        with transaction.atomic():
            serializer = model_input_serializer(model_instance, data=datum)
            if serializer.is_valid():
                updated_instance = serializer.save()
                changes = compare_data(
                    old_data=model_output_serializer(model_instance).data,
                    new_data=datum,
                )
                return (
                    response_constructor(
                        identifier=identifier,
                        request_status="UPDATED",
                        code=200,
                        message=f"{table_name} {identifier} updated.",
                        data={
                            "updates": changes,
                            "instance": model_output_serializer(updated_instance).data,
                        },
                    ),
                    "accepted_request",
                )
            else:
                error_data = [
                    {item: serializer.errors[item]} for item in serializer.errors
                ]
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


def delete_metadata(table_name: str, identifier: str, id_field: str = "id"):
    """
    Delete an existing model instance based on the provided identifier.

    Args:
        table_name (str): The name of the table (model) to delete from.
        identifier (str): The unique identifier of the model instance.
        id_field (str): The field used as an identifier (default is "id").

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    model_mapping = {
        "participant": Participant,
        "family": Family,
        "genetic_findings": GeneticFindings,
        "analyte": Analyte,
        "phenotype": Phenotype,
        "biobank": Biobank
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
