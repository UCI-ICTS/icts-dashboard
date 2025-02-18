#!/usr/bin/env python3
# experiments/servces.py

from django.db import transaction
from rest_framework import serializers
from config.selectors import (
    remove_na,
    response_constructor,
    compare_data,
    TableValidator
)

from experiments.models import (
    Aligned,
    AlignedDNAShortRead,
    AlignedNanopore,
    AlignedPacBio,
    AlignedRNAShortRead,
    Experiment,
    ExperimentDNAShortRead,
    ExperimentNanopore,
    ExperimentPacBio,
    ExperimentRNAShortRead,
    LibraryPrepType,
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
    swap_experiment_aligned
)

from metadata.selectors import get_analyte

from rest_framework import serializers
from .models import ExperimentRNAShortRead, LibraryPrepType, ExperimentType


class LibraryPrepTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryPrepType
        fields = ["name"]


class ExperimentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentType
        fields = ["name"]


class ExperimentRnaSerializer(serializers.ModelSerializer):
    library_prep_type = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=LibraryPrepType.objects.all()
    )

    experiment_type = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=ExperimentType.objects.all()
    )

    class Meta:
        model = ExperimentRNAShortRead
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentRNAShortRead instance using the validated data and set the many-to-many relationships"""

        library_prep_types_data = validated_data.pop("library_prep_type")
        experiment_types_data = validated_data.pop("experiment_type")

        experiment_rna_short_read_id = validated_data.get(
            "experiment_rna_short_read_id"
        )
        experiment_rna_instance, created = ExperimentRNAShortRead.objects.get_or_create(
            experiment_rna_short_read_id=experiment_rna_short_read_id,
            defaults=validated_data,
        )

        experiment_rna_instance.library_prep_type.set(library_prep_types_data)
        experiment_rna_instance.experiment_type.set(experiment_types_data)

        return experiment_rna_instance

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data and update the many-to-many relationships if provided"""

        library_prep_types_data = validated_data.pop("library_prep_type", None)
        experiment_types_data = validated_data.pop("experiment_type", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if library_prep_types_data is not None:
            instance.library_prep_type.set(library_prep_types_data)
        if experiment_types_data is not None:
            instance.experiment_type.set(experiment_types_data)

        return instance


class ExperimentNanoporeSerializer(serializers.ModelSerializer):
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
        return instance


class ExperimentPacBioSerializer(serializers.ModelSerializer):
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
        return instance


class ExperimentShortReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentDNAShortRead
        fields = "__all__"

    def create(self, validated_data):
        """Create a new ExperimentDNAShortRead instance using the validated data"""

        experiment_dna_short_read_id = validated_data.get(
            "experiment_dna_short_read_id"
        )
        experiment_dna_short_read, created = (
            ExperimentDNAShortRead.objects.get_or_create(
                experiment_dna_short_read_id=experiment_dna_short_read_id,
                defaults=validated_data,
            )
        )
        return experiment_dna_short_read

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class ExperimentSerializer(serializers.ModelSerializer):
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


class AlignedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aligned
        fields = "__all__"

    def create(self, validated_data):
        """Create a new Experiment instance using the validated data"""

        aligned_id = validated_data.get("aligned_id")
        aligned, created = Aligned.objects.get_or_create(
            aligned_id=aligned_id, defaults=validated_data
        )
        return aligned

    def update(self, instance, validated_data):
        """Update each attribute of the instance with validated data"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance


class AlignedDNAShortReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlignedDNAShortRead
        fields = "__all__"


class AlignedPacBioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlignedPacBio
        fields = "__all__"


class AlignedNanoporeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlignedNanopore
        fields = "__all__"


class AlignedRnaSerializer(serializers.ModelSerializer):
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


def create_or_update_experiment(table_name: str, identifier: str, model_instance, datum: dict):
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
        "experiment_dna_short_read": {
            "model": ExperimentDNAShortRead,
            "input_serializer": ExperimentShortReadSerializer,
            "output_serializer": ExperimentShortReadSerializer,
            "parsed_data": lambda datum: parse_short_read(short_read=datum)
        },
        "experiment_nanopore": {
            "model": ExperimentNanopore,
            "input_serializer": ExperimentNanoporeSerializer,
            "output_serializer": ExperimentNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore(nanopore=datum)
        },
        "experiment_pac_bio": {
            "model": ExperimentPacBio,
            "input_serializer": ExperimentPacBioSerializer,
            "output_serializer": ExperimentPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio(pac_bio_datum=datum)
        },
        "experiment_rna_short_read": {
            "model": ExperimentRNAShortRead,
            "input_serializer": ExperimentRnaSerializer,
            "output_serializer": ExperimentRnaSerializer,
            "parsed_data": lambda datum: parse_rna(rna_datum=datum)
        }
    }
    table_validator = TableValidator()
    
    if get_analyte(datum["analyte_id"]) is not None:
        participant_id = get_analyte(datum["analyte_id"]).participant_id.participant_id
    else: 
        analyte_id = datum["analyte_id"]
        return response_constructor(
            identifier=identifier,
            request_status="BAD REQUEST",
            code=400,
            data=f"Analyte {analyte_id} dose not exist.",
        ), "rejected_request"

    experiment_data = {
        "experiment_id": f"{table_name}.{identifier}",
        "table_name": table_name,
        "id_in_table": identifier,
        "participant_id": participant_id,
    }
    experiment_results = ExperimentService.validate_experiment(experiment_data, table_validator)

    model_input_serializer = table_serializers[table_name]["input_serializer"]
    model_output_serializer = table_serializers[table_name]["output_serializer"]

    if "parsed_data" in table_serializers[table_name]:
        datum = remove_na(table_serializers[table_name]["parsed_data"](datum))
    else:
        datum = remove_na(datum=datum)

    table_validator.validate_json(json_object=datum, table_name=table_name)
    results = table_validator.get_validation_results()
    if results["valid"] and experiment_results['valid']:
        changes = compare_data(
            old_data=model_output_serializer(model_instance).data,
            new_data=datum
        ) if model_instance else {identifier:"CREATED"}

        serializer = model_input_serializer(model_instance, data=datum)
        experiment_serializer = ExperimentService.create_or_update_experiment(experiment_data)
        if serializer.is_valid() and experiment_serializer.is_valid():
            updated_instance = serializer.save()
            if not changes:
                return response_constructor(
                    identifier=identifier,
                    request_status="SUCCESS",
                    code=200,
                    message=f"{table_name} {identifier} had no changes.",
                    data={
                        "updates": None,
                        "instance": model_output_serializer(updated_instance).data
                    }
                ), "accepted_request"

            return response_constructor(
                identifier=identifier,
                request_status="UPDATED" if model_instance else "CREATED",
                code=200 if model_instance else 201,
                message=(
                    f"{table_name} {identifier} updated." if model_instance 
                    else f"{table_name} {identifier} created."
                ),
                data={
                    "updates": changes,
                    "instance": model_output_serializer(updated_instance).data
                }
            ), "accepted_request"
            
        else:
            error_data = [
                {item: serializer.errors[item]}
                for item in serializer.errors
            ]
            if experiment_serializer and hasattr(experiment_serializer, 'errors'):
                error_data.extend(
                    [{item: experiment_serializer.errors[item]} for item in experiment_serializer.errors]
                )
            return response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=error_data,
            ), "rejected_request"
        
    else:
        return response_constructor(
            identifier=identifier,
            request_status="BAD REQUEST",
            code=400,
            data=results["errors"] + experiment_results["errors"],
        ), "rejected_request"


def create_or_update_alignment(table_name: str, identifier: str, model_instance, datum: dict):
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
        "aligned_dna_short_read": {
            "model": AlignedDNAShortRead,
            "input_serializer": AlignedDNAShortReadSerializer,
            "output_serializer": AlignedDNAShortReadSerializer,
            "parsed_data": lambda datum: parse_short_read_aligned(short_read_aligned=datum)
        },
        "aligned_nanopore": {
            "model": AlignedNanopore,
            "input_serializer": AlignedNanoporeSerializer,
            "output_serializer": AlignedNanoporeSerializer,
            "parsed_data": lambda datum: parse_nanopore_aligned(nanopore_aligned=datum)
        },
        "aligned_pac_bio": {
            "model": AlignedPacBio,
            "input_serializer": AlignedPacBioSerializer,
            "output_serializer": AlignedPacBioSerializer,
            "parsed_data": lambda datum: parse_pac_bio_aligned(pac_bio_aligned=datum)
        },
        "aligned_rna_short_read": {
            "model": AlignedRNAShortRead,
            "input_serializer": AlignedRnaSerializer,
            "output_serializer": AlignedRnaSerializer,
            "parsed_data": lambda datum: parse_rna_aligned(rna_aligned=datum)
        }
    }
    table_validator = TableValidator()
    experiment_name = swap_experiment_aligned(table_name)

    try:
        experiment_object = Experiment.objects.get(id_in_table=datum[experiment_name+"_id"])
        participant_id = experiment_object.participant_id.participant_id
    except Experiment.DoesNotExist: 
        return response_constructor(
            identifier=identifier,
            request_status="BAD REQUEST",
            code=400,
            data=f"Experiment {experiment_name} for {identifier} dose not exist.",
        ), "rejected_request"
    
    aligned_data = {
        "aligned_id": f"{table_name}.{identifier}",
        "table_name": table_name,
        "id_in_table": identifier,
        "participant_id": participant_id,
        "aligned_file": datum[f"{table_name}_file"],
        "aligned_index_file": datum[f"{table_name}_index_file"]
    }
    
    aligned_results = AlignedService.validate_aligned(aligned_data, table_validator)

    model_input_serializer = table_serializers[table_name]["input_serializer"]
    model_output_serializer = table_serializers[table_name]["output_serializer"]
    model_class = table_serializers[table_name]["model"]

    if "parsed_data" in table_serializers[table_name]:
        datum = remove_na(table_serializers[table_name]["parsed_data"](datum))
    else:
        datum = remove_na(datum=datum) 
    table_validator.validate_json(json_object=datum, table_name=table_name)
    results = table_validator.get_validation_results()

    if results["valid"] and aligned_results['valid']:
        changes = compare_data(
            old_data=model_output_serializer(model_instance).data,
            new_data=datum
        ) if model_instance else {identifier:"CREATED"}

        serializer = model_input_serializer(model_instance, data=datum)
        alignment_serializer = AlignedService.create_or_update_aligned(aligned_data)
        if serializer.is_valid() and alignment_serializer.is_valid:
            updated_instance = serializer.save()
            if not changes:
                return response_constructor(
                    identifier=identifier,
                    request_status="SUCCESS",
                    code=200,
                    message=f"{table_name} {identifier} had no changes.",
                    data={
                        "updates": None,
                        "instance": model_output_serializer(updated_instance).data
                    }
                ), "accepted_request"

            return response_constructor(
                identifier=identifier,
                request_status="UPDATED" if model_instance else "CREATED",
                code=200 if model_instance else 201,
                message=(
                    f"{table_name} {identifier} updated." if model_instance 
                    else f"{table_name} {identifier} created."
                ),
                data={
                    "updates": changes,
                    "instance": model_output_serializer(updated_instance).data
                }
            ), "accepted_request"
            
        else:
            error_data = [
                {item: serializer.errors[item]}
                for item in serializer.errors
            ]
            if alignment_serializer and hasattr(alignment_serializer, 'errors'):
                error_data.extend(
                    [{item: alignment_serializer.errors[item]} for item in alignment_serializer.errors]
                )
            return response_constructor(
                identifier=identifier,
                request_status="BAD REQUEST",
                code=400,
                data=error_data,
            ), "rejected_request"
        
    else:
        return response_constructor(
            identifier=identifier,
            request_status="BAD REQUEST",
            code=400,
            data=results["errors"] + aligned_results["errors"],
        ), "rejected_request"
