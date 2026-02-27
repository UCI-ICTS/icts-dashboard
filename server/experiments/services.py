#!/usr/bin/env python3
# experiments/servces.py

from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from config.selectors import (
    remove_na,
    response_constructor,
    compare_data,
    TableValidator,
)

from experiments.models import (
    Aligned,
    AlignedDNAShortRead,
    AlignedDNAShortReadSet,
    CalledVariantsDNAShortRead,
    AlignedNanopore,
    AlignedNanoporeSet,
    CalledVariantsNanopore,
    AlignedPacBio,
    AlignedPacBioSet,
    CalledVariantsPacBio,
    AlignedRNAShortRead,
    Experiment,
    ExperimentDNAShortRead,
    ExperimentNanopore,
    ExperimentPacBio,
    ExperimentRNAShortRead,
    LibraryPrepType,
    PrepTargetsDetail,
    ExperimentType,
)
from experiments.selectors import (
    parse_nanopore,
    parse_nanopore_aligned,
    parse_short_read,
    parse_short_read_aligned,
    parse_rna,
    parse_rna_aligned,
    parse_pac_bio,
    parse_pac_bio_aligned,
    swap_experiment_aligned,
)

from metadata.selectors import get_analyte

from rest_framework import serializers
from experiments.models import ExperimentRNAShortRead, LibraryPrepType, ExperimentType


class LibraryPrepTypeSerializer(serializers.ModelSerializer):
    """
    Docstring for LibraryPrepTypeSerializer
    """
    class Meta:
        model = LibraryPrepType
        fields = ["name"]


class ExperimentTypeSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentTypeSerializer
    """
    class Meta:
        model = ExperimentType
        fields = ["name"]


class ExperimentRNAInputSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentRNAInputSerializer
    """
    library_prep_type = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=LibraryPrepType.objects.all(),
        required=False,
        allow_null=True,
    )
    prep_targets_detail = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=PrepTargetsDetail.objects.all(),
        required=False,
        allow_null=True,
    )
    experiment_type = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=ExperimentType.objects.all()
    )

    class Meta:
        model = ExperimentRNAShortRead
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentRNAShortRead instance using the validated data and set the many-to-many relationships"""

        library_prep_types_data = validated_data.pop("library_prep_type", [])
        prep_targets_detail_data = validated_data.pop("prep_targets_detail", [])
        experiment_types_data = validated_data.pop("experiment_type", [])

        experiment_rna_instance = ExperimentRNAShortRead.objects.create(
            **validated_data
        )
        experiment_rna_instance.library_prep_type.set(library_prep_types_data)
        experiment_rna_instance.prep_targets_detail.set(prep_targets_detail_data)
        experiment_rna_instance.experiment_type.set(experiment_types_data)

        return experiment_rna_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data and update the many-to-many relationships if provided"""

        library_prep_types_data = validated_data.pop("library_prep_type", None)
        prep_targets_detail_data = validated_data.pop("prep_targets_detail", None)
        experiment_types_data = validated_data.pop("experiment_type", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if library_prep_types_data is not None:
            instance.library_prep_type.set(library_prep_types_data)
        if prep_targets_detail_data is not None:
            instance.prep_targets_detail.set(prep_targets_detail_data)
        if experiment_types_data is not None:
            instance.experiment_type.set(experiment_types_data)

        instance.save()
        return instance


class ExperimentRNAOutputSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentRNAOutputSerializer
    """
    library_prep_type = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )
    prep_targets_detail = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )
    experiment_type = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )

    class Meta:
        model = ExperimentRNAShortRead
        fields = "__all__"


class ExperimentDNAInputSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentDNAInputSerializer
    """
    experiment_type = serializers.ChoiceField(choices=["targeted", "genome", "exome"])

    class Meta:
        model = ExperimentDNAShortRead
        fields = "__all__"


class ExperimentDNAOutputSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentDNAOutputSerializer
    """
    library_prep_type = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )
    experiment_type = serializers.CharField()  # It's a plain string field

    class Meta:
        model = ExperimentDNAShortRead
        fields = "__all__"


class ExperimentNanoporeSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentNanoporeSerializer
    """
    class Meta:
        model = ExperimentNanopore
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentNanopore instance using the validated data"""

        experiment_nanopore_id = validated_data.get("experiment_nanopore_id")
        experiment_nanopre_instance, created = ExperimentNanopore.objects.get_or_create(
            experiment_nanopore_id=experiment_nanopore_id, defaults=validated_data
        )
        return experiment_nanopre_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ExperimentPacBioSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentPacBioSerializer
    """
    class Meta:
        model = ExperimentPacBio
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentPacBio instance using the validated data"""

        experiment_pac_bio_id = validated_data.get("experiment_pac_bio_id")
        experiment_pac_bio, created = ExperimentPacBio.objects.get_or_create(
            experiment_pac_bio_id=experiment_pac_bio_id, defaults=validated_data
        )
        return experiment_pac_bio

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ExperimentSerializer(serializers.ModelSerializer):
    """
    Docstring for ExperimentSerializer
    """
    class Meta:
        model = Experiment
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Experiment instance using the validated data"""

        experiment_id = validated_data.get("experiment_id")
        experiment, created = Experiment.objects.get_or_create(
            experiment_id=experiment_id, defaults=validated_data
        )
        return experiment

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ExperimentService:
    """
    Service class that provides static methods to create, update, and validate experiments.

    This class encapsulates the logic for handling experiments by interfacing with
    the Experiment model and related serializers to ensure data integrity and compliance
    with business rules before persisting in the database.

    Methods:
        create_or_update_experiment(data): Creates a new experiment or updates an existing one
        based on the provided data dictionary.
        validate_experiment(data, validator): Validates experiment data against a specified
        JSON schema using a validator instance.
    """

    @staticmethod
    def create_or_update_experiment(data):
        identifier = data["experiment_id"]
        existing_experiment = Experiment.objects.filter(
            experiment_id=identifier
        ).first()

        # Determine if it's a creation or update
        if existing_experiment:
            serializer = ExperimentSerializer(existing_experiment, data=data)
        else:
            serializer = ExperimentSerializer(data=data)

        if serializer.is_valid():
            experiment_instance = serializer.save()
            return serializer
        else:
            return serializer

    @staticmethod
    def validate_experiment(data, validator):
        validator.validate_json(json_object=data, table_name="experiment")
        return validator.get_validation_results()


class AlignedRNAShortReadInputSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedRNAShortReadInputSerializer
    """
    class Meta:
        model = AlignedRNAShortRead
        fields = "__all__"
        extra_kwargs = {
            "five_prime_three_prime_bias": {
                "read_only": True
            }  # Prevents duplication issues
        }
        rename_fields = {  # Custom rename logic
            "five_prime_three_prime_bias": "5prime3prime_bias"
        }
        # This renames the field in API input/output while keeping it correct in Django ORM
        five_prime_three_prime_bias = serializers.FloatField(
            required=False, allow_null=True
        )

    def to_representation(self, instance):
        """Rename `five_prime_three_prime_bias` to `5prime3prime_bias` in response"""
        data = super().to_representation(instance)
        if "five_prime_three_prime_bias" in data:
            data["5prime3prime_bias"] = data.pop("five_prime_three_prime_bias")
        return data

    def to_internal_value(self, data):
        """Allow `5prime3prime_bias` as input while mapping it to `five_prime_three_prime_bias`"""
        if "5prime3prime_bias" in data:
            data["five_prime_three_prime_bias"] = data.pop("5prime3prime_bias")
        return super().to_internal_value(data)

    def create(self, validated_data):
        """Create a new AlignedRNAShortRead instance using the validated data and set the many-to-many relationships"""
        aligned_rna_instance = AlignedRNAShortRead.objects.create(**validated_data)

        return aligned_rna_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data and update the many-to-many relationships if provided"""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class AlignedRNAShortReadOutputSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedRNAShortReadOutputSerializer
    """
    class Meta:
        model = AlignedRNAShortRead
        fields = "__all__"

    def to_representation(self, instance):
        """Rename `five_prime_three_prime_bias` to `5prime3prime_bias` in response"""
        data = super().to_representation(instance)
        if "five_prime_three_prime_bias" in data:
            data["5prime3prime_bias"] = data.pop("five_prime_three_prime_bias")
        return data


class AlignedDNAShortReadSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedDNAShortReadSerializer
    """
    class Meta:
        model = AlignedDNAShortRead
        fields = "__all__"

    def create(self, validated_data):
        """Create a new AlignedDNAShortRead instance using the validated data and set the many-to-many relationships"""
        aligned_dna_instance = AlignedDNAShortRead.objects.create(**validated_data)

        return aligned_dna_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data and update the many-to-many relationships if provided"""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class AlignedDNAShortReadSetSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedDNAShortReadSetSerializer
    """
    class Meta:
        model = AlignedDNAShortReadSet
        fields = "__all__"

    def create(self, validated_data):
        """Create a new AlignedDNAShortReadSet instance using the validated data and set the many-to-many relationships"""
        aligned_dna_set_instance = AlignedDNAShortReadSet.objects.create(**validated_data)

        return aligned_dna_set_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data and update the many-to-many relationships if provided"""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CalledVariantsDNAShortReadSerializer(serializers.ModelSerializer):
    """
    Docstring for CalledVariantsDNAShortReadSerializder
    """
    class Meta:
        model = CalledVariantsDNAShortRead
        fields = "__all__"

    def create(self, validated_data):
        """Create a new CalledVariantsDNAShortRead instance using the validated data and set the many-to-many relationships"""
        called_variants_dna_short_read_instance = CalledVariantsDNAShortRead.objects.create(**validated_data)

        return called_variants_dna_short_read_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data and update the many-to-many relationships if provided"""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class AlignedSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedSerializer
    """
    class Meta:
        model = Aligned
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Aligned instance using the validated data"""

        aligned_id = validated_data.get("aligned_id")
        aligned, created = Aligned.objects.get_or_create(
            aligned_id=aligned_id, defaults=validated_data
        )
        return aligned

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AlignedDNAShortReadSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedDNAShortReadSerializer
    """
    class Meta:
        model = AlignedDNAShortRead
        fields = "__all__"


class AlignedPacBioSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedPacBioSerializer
    """
    class Meta:
        model = AlignedPacBio
        fields = "__all__"


class AlignedPacBioSetSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedPacBioSetSerializer
    """
    class Meta:
        model = AlignedPacBioSet
        fields = "__all__"


class CalledVariantsPacBioSerializer(serializers.ModelSerializer):
    """
    Docstring for CalledVariantsPacBioSerializer
    """
    class Meta:
        model = CalledVariantsPacBio
        fields = "__all__"


class AlignedNanoporeSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedNanoporeSerializer
    """
    class Meta:
        model = AlignedNanopore
        fields = "__all__"


class AlignedNanoporeSetSerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedNanoporeSetSerializer
    """
    class Meta:
        model = AlignedNanoporeSet
        fields = "__all__"


class CalledVariantsNanoporeSerializer(serializers.ModelSerializer):
    """
    Docstring for CalledVariantsNanopore
    """
    class Meta:
        model = CalledVariantsNanopore
        fields = "__all__"


class AlignedRNASerializer(serializers.ModelSerializer):
    """
    Docstring for AlignedRNASerializer
    """
    class Meta:
        model = AlignedRNAShortRead
        fields = "__all__"


class AlignedService:
    """
    Service class that provides static methods to create, update, and validate Alignments.

    This class encapsulates the logic for handling alignments by interfacing with
    the Aligned model and related serializers to ensure data integrity and compliance
    with business rules before persisting in the database.

    Methods:
        create_or_update_aligned(data): Creates a new alignement or updates an existing one
        based on the provided data dictionary.
        validate_aligned(data, validator): Validates experiment data against a specified
        JSON schema using a validator instance.
    """

    @staticmethod
    def create_or_update_aligned(data):
        """Create or Update Aligned

        Creates a new alignement or updates an existing one
        based on the provided data dictionary."""

        identifier = data["aligned_id"]
        existing_aligned = Aligned.objects.filter(aligned_id=identifier).first()

        # Determine if it's a creation or update
        if existing_aligned:
            serializer = AlignedSerializer(existing_aligned, data=data)
        else:
            serializer = AlignedSerializer(data=data)

        if serializer.is_valid():
            aligned_instance = serializer.save()
            return serializer
        else:
            return serializer

    @staticmethod
    def validate_aligned(data, validator):
        """Validate Aligned

        Validates experiment data against a specified
        JSON schema using a validator instance.
        """

        validator.validate_json(json_object=data, table_name="aligned")
        return validator.get_validation_results()


def create_experiment(table_name: str, identifier: str, datum: dict, current_user: User):
    """
    Create a new experiment instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create.
        identifier (str): The unique identifier for the experiment instance.
        datum (dict): The data to create the experiment instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """

    table_serializers = {
        "experiment_dna_short_read": {
            "model": ExperimentDNAShortRead,
            "input_serializer": ExperimentDNAInputSerializer,
            "output_serializer": ExperimentDNAOutputSerializer,
            "parsed_data": lambda datum: parse_short_read(short_read=datum),
        },
        "experiment_nanopore": {
            "model": ExperimentNanopore,
            "input_serializer": ExperimentNanoporeSerializer,
            "output_serializer": ExperimentNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore(nanopore=datum),
        },
        "experiment_pac_bio": {
            "model": ExperimentPacBio,
            "input_serializer": ExperimentPacBioSerializer,
            "output_serializer": ExperimentPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio(pac_bio_datum=datum),
        },
        "experiment_rna_short_read": {
            "model": ExperimentRNAShortRead,
            "input_serializer": ExperimentRNAInputSerializer,
            "output_serializer": ExperimentRNAOutputSerializer,
            "parsed_data": lambda datum: parse_rna(rna_datum=datum),
        },
    }
    table_validator = TableValidator()

    if get_analyte(datum["analyte_id"]) is not None:
        participant_id = get_analyte(datum["analyte_id"]).participant_id.participant_id
    else:
        analyte_id = datum["analyte_id"]
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=f"Analyte {analyte_id} does not exist.",
            ),
            "rejected_request",
        )

    experiment_data = {
        "experiment_id": f"{table_name}.{identifier}",
        "table_name": table_name,
        "id_in_table": identifier,
        "participant_id": participant_id,
    }

    experiment_results = ExperimentService.validate_experiment(
        experiment_data, table_validator
    )

    if "parsed_data" in table_serializers[table_name]:
        datum = remove_na(table_serializers[table_name]["parsed_data"](datum))
    else:
        datum = remove_na(datum=datum)
    table_validator.validate_json(json_object=datum, table_name=table_name)
    results = table_validator.get_validation_results()

    if results["valid"] and experiment_results["valid"]:
        serializer = table_serializers[table_name]["input_serializer"](data=datum)
        experiment_serializer = ExperimentService.create_or_update_experiment(
            experiment_data
        )
        if serializer.is_valid() and experiment_serializer.is_valid():
            new_instance = serializer.save(changed_by=current_user)
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="CREATED",
                    code=201,
                    message=f"{table_name} {identifier} created.",
                    data={
                        "instance": table_serializers[table_name]["output_serializer"](
                            new_instance
                        ).data
                    },
                ),
                "accepted_request",
            )
        else:
            error_data = [{item: serializer.errors[item]} for item in serializer.errors]
            if experiment_serializer and hasattr(experiment_serializer, "errors"):
                error_data.extend(
                    [
                        {item: experiment_serializer.errors[item]}
                        for item in experiment_serializer.errors
                    ]
                )
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
                data=results["errors"] + experiment_results["errors"],
            ),
            "rejected_request",
        )


def update_experiments_entry(
    table_name: str, identifier: str, model_instance, datum: dict, current_user: User):
    """
    Update an existing experiment instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to update.
        identifier (str): The unique identifier for the experiment instance.
        model_instance: The existing model instance to update.
        datum (dict): The data to update the experiment instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "experiment_dna_short_read": {
            "model": ExperimentDNAShortRead,
            "input_serializer": ExperimentDNAInputSerializer,
            "output_serializer": ExperimentDNAOutputSerializer,
            "parsed_data": lambda datum: parse_short_read(short_read=datum),
        },
        "experiment_nanopore": {
            "model": ExperimentNanopore,
            "input_serializer": ExperimentNanoporeSerializer,
            "output_serializer": ExperimentNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore(nanopore=datum),
        },
        "experiment_pac_bio": {
            "model": ExperimentPacBio,
            "input_serializer": ExperimentPacBioSerializer,
            "output_serializer": ExperimentPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio(pac_bio_datum=datum),
        },
        "experiment_rna_short_read": {
            "model": ExperimentRNAShortRead,
            "input_serializer": ExperimentRNAInputSerializer,
            "output_serializer": ExperimentRNAOutputSerializer,
            "parsed_data": lambda datum: parse_rna(rna_datum=datum),
        },
        "aligned_dna_short_read": {
            "model": AlignedDNAShortRead,
            "input_serializer": AlignedDNAShortReadSerializer,
            "output_serializer": AlignedDNAShortReadSerializer,
            "parsed_data": lambda datum: parse_short_read_aligned(
                short_read_aligned=datum
            ),
        },
        "aligned_nanopore": {
            "model": AlignedNanopore,
            "input_serializer": AlignedNanoporeSerializer,
            "output_serializer": AlignedNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore_aligned(nanopore_aligned=datum),
        },
        "aligned_pac_bio": {
            "model": AlignedPacBio,
            "input_serializer": AlignedPacBioSerializer,
            "output_serializer": AlignedPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio_aligned(pac_bio_aligned=datum),
        },
        "aligned_rna_short_read": {
            "model": AlignedRNAShortRead,
            "input_serializer": AlignedRNASerializer,
            "output_serializer": AlignedRNASerializer,
            "parsed_data": lambda datum: parse_rna_aligned(rna_aligned=datum),
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

    with transaction.atomic():
        input_serializer = serializers["input_serializer"]
        output_serializer = serializers["output_serializer"]
        changes = compare_data(
            old_data=output_serializer(model_instance).data,
            new_data=datum,
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


def delete_experiment(table_name: str, identifier: str, id_field: str = "id"):
    """
    Delete an existing experiment model instance and the corresponding Experiment object
    based on the provided identifier.

    Args:
        table_name (str): The name of the table (model) to delete from.
        identifier (str): The unique identifier of the model instance.
        id_field (str): The field used as an identifier (default is "id").

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    model_mapping = {
        "experiment_dna_short_read": ExperimentDNAShortRead,
        "experiment_nanopore": ExperimentNanopore,
        "experiment_pac_bio": ExperimentPacBio,
        "experiment_rna_short_read": ExperimentRNAShortRead,
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

            # Remove the associated entry from the Experiment table
            experiment_id = f"{table_name}.{identifier}"
            experiment_instance = Experiment.objects.filter(pk=experiment_id).first()
            if experiment_instance:
                experiment_instance.delete()

            return (
                response_constructor(
                    identifier=identifier,
                    request_status="DELETED",
                    code=200,
                    data=f"{table_name} {identifier} and associated experiment deleted successfully.",
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


def create_aligned(table_name: str, identifier: str, datum: dict, current_user: User):
    """
    Create a new alignment instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to create.
        identifier (str): The unique identifier for the alignment instance.
        datum (dict): The data to create the alignment instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "aligned_dna_short_read": {
            "model": AlignedDNAShortRead,
            "input_serializer": AlignedDNAShortReadSerializer,
            "output_serializer": AlignedDNAShortReadSerializer,
            "parsed_data": lambda datum: parse_short_read_aligned(
                short_read_aligned=datum
            ),
        },
        "aligned_dna_short_read_set": {
            "input_serializer": AlignedDNAShortReadSetSerializer,
            "output_serializer": AlignedDNAShortReadSetSerializer,
        },
        "called_variants_dna_short_read": {
            "input_serializer": CalledVariantsDNAShortReadSerializer,
            "output_serializer": CalledVariantsDNAShortReadSerializer,
        },
        "aligned_nanopore": {
            "model": AlignedNanopore,
            "input_serializer": AlignedNanoporeSerializer,
            "output_serializer": AlignedNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore_aligned(nanopore_aligned=datum),
        },
        "aligned_nanopore_set": {
            "input_serializer": AlignedNanoporeSetSerializer,
            "output_serializer": AlignedNanoporeSetSerializer,
        },
        "called_variants_nanopore": {
            "input_serializer": CalledVariantsNanoporeSerializer,
            "output_serializer": CalledVariantsNanoporeSerializer,
        },
        "aligned_pac_bio": {
            "model": AlignedPacBio,
            "input_serializer": AlignedPacBioSerializer,
            "output_serializer": AlignedPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio_aligned(pac_bio_aligned=datum),
        },
        "aligned_pac_bio_set": {
            "input_serializer": AlignedPacBioSetSerializer,
            "output_serializer": AlignedPacBioSetSerializer,
        },
        "called_variants_pac_bio": {
            "intput_serializer": CalledVariantsPacBioSerializer,
            "output_serializer": CalledVariantsPacBioSerializer,
        },
        "aligned_rna_short_read": {
            "model": AlignedRNAShortRead,
            "input_serializer": AlignedRNASerializer,
            "output_serializer": AlignedRNASerializer,
            "parsed_data": lambda datum: parse_rna_aligned(rna_aligned=datum),
        },
    }
    table_validator = TableValidator()
    experiment_name = swap_experiment_aligned(table_name)
    experiment_id = datum[experiment_name + "_id"]
    if experiment_id != None and isinstance(experiment_id, str):
        try:
            experiment_object = Experiment.objects.get(
                experiment_id=experiment_name + "." + experiment_id
            )
            participant_id = experiment_object.participant_id.participant_id
        except Experiment.DoesNotExist:
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="BAD REQUEST",
                    code=400,
                    data=f"Experiment {experiment_name} for {identifier} does not exist.",
                ),
                "rejected_request",
            )
    else:
        return (
            response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=f"Experiment ID {experiment_id} for {identifier} does not exist.",
            ),
            "rejected_request",
        )

    aligned_data = {
        "aligned_id": f"{table_name}.{identifier}",
        "table_name": table_name,
        "id_in_table": identifier,
        "participant_id": participant_id,
        "aligned_file": datum[f"{table_name}_file"],
        "aligned_index_file": datum[f"{table_name}_index_file"],
    }

    aligned_results = AlignedService.validate_aligned(aligned_data, table_validator)

    if "parsed_data" in table_serializers[table_name]:
        datum = remove_na(table_serializers[table_name]["parsed_data"](datum))
    else:
        datum = remove_na(datum=datum)
    table_validator.validate_json(json_object=datum, table_name=table_name)
    results = table_validator.get_validation_results()

    if results["valid"] and aligned_results["valid"]:
        serializer = table_serializers[table_name]["input_serializer"](data=datum)
        aligned_serializer = AlignedService.create_or_update_aligned(aligned_data)
        if serializer.is_valid() and aligned_serializer.is_valid():
            new_instance = serializer.save(changed_by=current_user)
            return (
                response_constructor(
                    identifier=identifier,
                    request_status="CREATED",
                    code=201,
                    message=f"{table_name} {identifier} created.",
                    data={
                        "instance": table_serializers[table_name]["output_serializer"](
                            new_instance
                        ).data
                    },
                ),
                "accepted_request",
            )
        else:
            error_data = [{item: serializer.errors[item]} for item in serializer.errors]
            if aligned_serializer and hasattr(aligned_serializer, "errors"):
                error_data.extend(
                    [
                        {item: aligned_serializer.errors[item]}
                        for item in aligned_serializer.errors
                    ]
                )
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
                data=results["errors"] + aligned_results["errors"],
            ),
            "rejected_request",
        )


def update_aligned(table_name: str, identifier: str, model_instance, datum: dict, current_user: User):
    """
    Update an existing alignment instance based on the provided data.

    Args:
        table_name (str): The name of the table (model) to update.
        identifier (str): The unique identifier for the alignment instance.
        model_instance: The existing model instance to update.
        datum (dict): The data to update the alignment instance with.

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    table_serializers = {
        "aligned_dna_short_read": {
            "model": AlignedDNAShortRead,
            "input_serializer": AlignedDNAShortReadSerializer,
            "output_serializer": AlignedDNAShortReadSerializer,
            "parsed_data": lambda datum: parse_short_read_aligned(
                short_read_aligned=datum
            ),
        },
        "aligned_dna_short_read_set": {
            "input_serializer": AlignedDNAShortReadSetSerializer,
            "output_serializer": AlignedDNAShortReadSetSerializer,
        },
        "called_variants_dna_short_read": {
            "input_serializer": CalledVariantsDNAShortReadSerializer,
            "output_serializer": CalledVariantsDNAShortReadSerializer,
        },
        "aligned_nanopore": {
            "model": AlignedNanopore,
            "input_serializer": AlignedNanoporeSerializer,
            "output_serializer": AlignedNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore_aligned(nanopore_aligned=datum),
        },
        "aligned_nanopore_set": {
            "input_serializer": AlignedNanoporeSetSerializer,
            "output_serializer": AlignedNanoporeSetSerializer,
        },
        "called_variants_nanopore": {
            "input_serializer": CalledVariantsNanoporeSerializer,
            "output_serializer": CalledVariantsNanoporeSerializer,
        },
        "aligned_pac_bio": {
            "model": AlignedPacBio,
            "input_serializer": AlignedPacBioSerializer,
            "output_serializer": AlignedPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio_aligned(pac_bio_aligned=datum),
        },
        "aligned_pac_bio_set": {
            "input_serializer": AlignedPacBioSetSerializer,
            "output_serializer": AlignedPacBioSetSerializer,
        },
        "called_variants_pac_bio": {
            "intput_serializer": CalledVariantsPacBioSerializer,
            "output_serializer": CalledVariantsPacBioSerializer,
        },
        "aligned_rna_short_read": {
            "model": AlignedRNAShortRead,
            "input_serializer": AlignedRNASerializer,
            "output_serializer": AlignedRNASerializer,
            "parsed_data": lambda datum: parse_rna_aligned(rna_aligned=datum),
        },
    }
    serializer = table_serializers.get(table_name)

    if serializer.is_valid():
        updated_instance = serializer.save(changed_by=current_user)
        changes = compare_data(
            old_data=table_serializers[table_name]["output_serializer"](
                model_instance
            ).data,
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
                    "instance": table_serializers[table_name]["output_serializer"](
                        updated_instance
                    ).data,
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


def delete_aligned(table_name: str, identifier: str, id_field: str = "id"):
    """
    Delete an existing aligned model instance and the corresponding Aligned object
    based on the provided identifier.

    Args:
        table_name (str): The name of the table (model) to delete from.
        identifier (str): The unique identifier of the model instance.
        id_field (str): The field used as an identifier (default is "id").

    Returns:
        dict: A response dictionary indicating the status of the operation.
    """
    model_mapping = {
        "aligned_dna_short_read": AlignedDNAShortRead,
        "aligned_dna_short_read_set": AlignedDNAShortReadSet,
        "called_variants_dna_short_read": CalledVariantsDNAShortRead,
        "aligned_nanopore": AlignedNanopore,
        "aligned_nanopore_set": AlignedNanoporeSet,
        "called_variants_nanopore": CalledVariantsNanopore,
        "aligned_pac_bio": AlignedPacBio,
        "aligned_pac_bio_set": AlignedPacBioSet,
        "called_variants_pac_bio": CalledVariantsPacBio,
        "aligned_rna_short_read": AlignedRNAShortRead,
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

            # Remove the associated entry from the Aligned table
            aligned_id = f"{table_name}.{identifier}"
            aligned_instance = Aligned.objects.filter(pk=aligned_id).first()
            if aligned_instance:
                aligned_instance.delete()

            return (
                response_constructor(
                    identifier=identifier,
                    request_status="DELETED",
                    code=200,
                    data=f"{table_name} {identifier} and associated alignment deleted successfully.",
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
