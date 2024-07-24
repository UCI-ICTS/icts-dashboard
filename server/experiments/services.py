#!/usr/bin/env python3
# experiments/servces.py

from django.db import transaction
from rest_framework import serializers
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
